#!/usr/bin/env bash
set -euo pipefail
fail() { printf 'Erreur : %s\n' "$*" >&2; exit 2; }
(( $# == 2 )) || fail "Usage : $0 source destination"
for tool in tar sha256sum mktemp mkdir; do
    command -v "$tool" >/dev/null || fail "Commande absente : $tool"
done
[[ -d "$1" ]] || fail 'Source inexistante.'
source_dir=$(cd -- "$1" && pwd -P)
mkdir -p -- "$2"
destination=$(cd -- "$2" && pwd -P)
# Éviter que tar archive sa propre sortie, y compris via un lien symbolique.
[[ "$source_dir" != / ]] || fail 'Choisir un sous-répertoire comme source.'
case "$destination/" in "$source_dir/"*) fail 'Destination située dans la source.' ;; esac
work=$(mktemp -d "$destination/backup-XXXXXXXX")
success=false
cleanup() { if [[ "$success" != true ]]; then rm -rf -- "$work"; fi; }
trap cleanup EXIT
archive="$work/archive.tar.gz"
tar -czf "$archive" -C "$source_dir" .
(cd -- "$work" && sha256sum archive.tar.gz > SHA256SUMS && sha256sum -c SHA256SUMS)
success=true
printf 'Sauvegarde vérifiée : %s\n' "$work"
