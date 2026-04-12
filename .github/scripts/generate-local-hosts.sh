#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <target_group> [output_file]" >&2
  exit 1
fi

target_group="$1"
output_file="${2:-hosts.ini}"
ansible_user="${USER:-runner}"

cat > "$output_file" <<EOF
[all]
localhost ansible_connection=local ansible_user=${ansible_user} ansible_python_interpreter=/usr/bin/python3

[master_nodes]
localhost

[worker_nodes]
#node2

[${target_group}]
localhost
EOF
