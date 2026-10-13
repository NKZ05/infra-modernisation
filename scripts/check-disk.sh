#!/usr/bin/env bash
set -euo pipefail
threshold=${1:-80}
LC_ALL=C df -Pk | awk -v limit="$threshold" 'NR>1 {usage=$5; sub(/%$/, "", usage); if (usage+0 > limit) {print "ALERTE : " $0; alert=1}} END {exit alert ? 1 : 0}'
