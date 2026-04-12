#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <output_dir> <file_prefix> [namespace]" >&2
  exit 1
fi

output_dir="$1"
file_prefix="$2"
namespace="${3:-aether-5gc}"

mkdir -p "$output_dir"

for component in amf webui udr udm ausf smf; do
  pod_name="$(kubectl get pods -n "$namespace" | awk -v pattern="$component" '$0 ~ pattern { print $1; exit }' || true)"
  if [[ -n "$pod_name" ]]; then
    echo "Retrieving ${component} logs from: ${pod_name}"
    kubectl logs "$pod_name" -n "$namespace" > "$output_dir/${file_prefix}_${component}.log"
  fi
done
