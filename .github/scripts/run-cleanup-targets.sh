#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <make_target> [make_target ...]" >&2
  exit 1
fi

for target in "$@"; do
  if make "$target"; then
    :
  else
    exit_code=$?
    echo "Failed to run cleanup target: ${target} (exit code: ${exit_code})" >&2
  fi
done
