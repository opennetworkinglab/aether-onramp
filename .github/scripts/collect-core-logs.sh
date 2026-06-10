#!/usr/bin/env bash

set -uo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <output_dir> <file_prefix> [namespace]" >&2
  exit 1
fi

output_dir="$1"
file_prefix="$2"
namespace="${3:-aether-5gc}"
error_log="${output_dir}/${file_prefix}_log_collection_errors.log"

mkdir -p "$output_dir"
: > "$error_log"

log_error() {
  echo "$1" | tee -a "$error_log" >&2
}

capture_to_file() {
  local destination="$1"
  shift

  if ! "$@" > "$destination" 2>&1; then
    log_error "Warning: failed to run command for $(basename "$destination")"
  fi
}

capture_namespace_state() {
  capture_to_file "${output_dir}/${file_prefix}_cluster_events.log" \
    kubectl get events -A --sort-by=.lastTimestamp
  capture_to_file "${output_dir}/${file_prefix}_nodes.log" \
    kubectl get nodes -o wide
  capture_to_file "${output_dir}/${file_prefix}_pods_summary.log" \
    kubectl get pods -n "$namespace" -o wide
  capture_to_file "${output_dir}/${file_prefix}_services.log" \
    kubectl get svc -n "$namespace" -o wide
  capture_to_file "${output_dir}/${file_prefix}_deployments.log" \
    kubectl get deployment -n "$namespace" -o wide
}

collect_pod_diagnostics() {
  local pod_name pod_names

  if ! pod_names="$(kubectl get pods -n "$namespace" -o jsonpath='{.items[*].metadata.name}' 2>&1)"; then
    log_error "Warning: failed to list pod names in namespace ${namespace}: ${pod_names}"
    return
  fi

  while IFS= read -r pod_name; do
    [[ -z "$pod_name" ]] && continue

    if ! kubectl describe pod -n "$namespace" "$pod_name" > "$output_dir/${file_prefix}_${pod_name}_describe.log" 2>&1; then
      log_error "Warning: failed to describe pod ${pod_name}"
    fi

    if ! kubectl logs --all-containers -n "$namespace" "$pod_name" > "$output_dir/${file_prefix}_${pod_name}.log" 2>&1; then
      log_error "Warning: failed to collect all-container logs for pod ${pod_name}; attempting fallback"
      if ! kubectl logs -n "$namespace" "$pod_name" >> "$output_dir/${file_prefix}_${pod_name}.log" 2>&1; then
        log_error "Warning: fallback log collection also failed for pod ${pod_name}"
      fi
    fi
  done < <(printf '%s\n' "$pod_names" | tr ' ' '\n')
}

capture_namespace_state
collect_pod_diagnostics

if [[ ! -s "$error_log" ]]; then
  rm -f "$error_log"
fi
