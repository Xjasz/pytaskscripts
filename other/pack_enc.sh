#!/usr/bin/env bash
set -euo pipefail
cmd="$1"; shift
encrypt() {
  src="$1"; out="$2"; pw="$3"
  tar --exclude='*.jsonp' --exclude='*.jsonx' -C "$src" -cf - . \
    | gzip -9 \
    | openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:"$pw" \
        -out "$out"
  echo "Packed & encrypted → $out"
}
decrypt() {
  in="$1"; dst="$2"; pw="$3"
  mkdir -p "$dst"
  openssl enc -d -aes-256-cbc -pbkdf2 -in "$in" -pass pass:"$pw" \
    | gzip -d \
    | tar -C "$dst" -xf -
  echo "Decrypted & unpacked → $dst/"
}
case "$cmd" in
  pack)   [[ $# -eq 3 ]] || { echo "Usage: $0 pack <src> <out> <pass>"; exit 1; }; encrypt "$@";;
  unpack) [[ $# -eq 3 ]] || { echo "Usage: $0 unpack <in> <dest> <pass>"; exit 1; }; decrypt "$@";;
  *) echo "Unknown cmd: $cmd"; echo "Use: $0 {pack|unpack} args…"; exit 1;;
esac
