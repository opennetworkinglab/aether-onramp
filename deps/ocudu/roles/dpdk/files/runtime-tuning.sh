#!/usr/bin/env bash
#
# Host runtime tuning for a DPDK OCUDU gNB.
#
# These are sysfs knobs that reset on every boot, so they belong in a unit
# rather than in a one-shot Ansible task: a reboot would otherwise leave the
# node with the isolation and hugepages from the kernel command line but the
# CPUs back on the default governor, which shows up as RF underflow.

set -u

rc=0

# Hold every CPU at its maximum frequency. A scaling governor that ramps
# clocks down under the gNB's bursty load starves the radio thread.
governors=(/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor)
if [[ -e "${governors[0]}" ]]; then
  for f in "${governors[@]}"; do
    [[ -w "$f" ]] || continue
    if ! echo performance > "$f"; then
      echo "failed to set performance governor on $f" >&2
      rc=1
    fi
  done
else
  echo "no cpufreq governor interface; skipping governor" >&2
fi

# DRM's output polling wakes a worker on a timer and adds jitter to an
# otherwise quiet system. Headless nodes do not need it.
poll_path=/sys/module/drm_kms_helper/parameters/poll
if [[ -w "$poll_path" ]]; then
  if ! echo N > "$poll_path"; then
    echo "failed to disable DRM KMS helper polling" >&2
    rc=1
  fi
fi

exit "$rc"
