#!/usr/bin/env bash
set -euo pipefail
fail() { printf 'Erreur : %s\n' "$*" >&2; exit 2; }
(( $# <= 1 )) || fail "Usage : $0 [seuil 1-100]"
threshold=${1:-80}
[[ "$threshold" =~ ^[0-9]{1,3}$ ]] || fail 'Seuil entier attendu.'
threshold=$((10#$threshold))
(( threshold >= 1 && threshold <= 100 )) || fail 'Seuil hors limites.'
command -v df >/dev/null || fail 'df absent.'
command -v awk >/dev/null || fail 'awk absent.'
report=$(LC_ALL=C df -Pk) || fail 'Impossible de lire les systèmes de fichiers.'
# Correction : comparer numériquement la colonne Use%, y compris à 100%.
# Le format POSIX stabilise les colonnes ; la comparaison inclut le seuil exact.
if printf '%s\n' "$report" | awk -v limit="$threshold" '
NR > 1 {
    usage=$5
    if (usage !~ /^[0-9]+%$/) { bad=1; next }
    sub(/%$/, "", usage)
    if (usage+0 > limit) { print "ALERTE disque : " $0; alert=1 }
    count++
}
END { if (bad || !count) exit 2; if (alert) exit 1; print "OK : espace disque sous le seuil de " limit "%" }
'; then
    exit 0
else
    exit "$?"
fi
