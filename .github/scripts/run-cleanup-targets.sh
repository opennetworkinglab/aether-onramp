#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <make_target> [make_target ...]" >&2
  exit 1
fi

for target in "$@"; do
  if ! make "$target"; then
    echo "Failed to run cleanup target: ${target}"
  fi
done
