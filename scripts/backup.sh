#!/usr/bin/env bash
set -euo pipefail
(( $# == 2 )) || exit 2
mkdir -p -- "$2"
work=$(mktemp -d "$2/backup-XXXXXXXX")
tar -czf "$work/archive.tar.gz" -C "$1" .
printf 'Archive : %s\n' "$work/archive.tar.gz"
