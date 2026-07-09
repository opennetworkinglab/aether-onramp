#!/usr/bin/env bash

set -u

failures=0
warnings=0
ptp4l_unit=ocudu-ptp4l.service
phc2sys_unit=ocudu-phc2sys.service

say() {
  printf '%s\n' "$*"
}

pass() {
  say "PASS: $*"
}

warn() {
  say "WARN: $*"
  warnings=$((warnings + 1))
}

fail() {
  say "FAIL: $*"
  failures=$((failures + 1))
}

require_command() {
  local command_name=$1
  if ! command -v "$command_name" >/dev/null 2>&1; then
    fail "missing required command: $command_name"
    return 1
  fi
}

get_systemctl_property() {
  local unit=$1
  local property=$2
  systemctl show "$unit" --property "$property" --value 2>/dev/null
}

trim() {
  local value=$1
  value=${value#${value%%[![:space:]]*}}
  value=${value%${value##*[![:space:]]}}
  printf '%s' "$value"
}

extract_pf_iface() {
  local exec_start
  exec_start=$(get_systemctl_property "$ptp4l_unit" ExecStart)
  printf '%s\n' "$exec_start" | sed -n 's/.* -i \([^ ;][^ ]*\).*/\1/p' | head -n 1
}

extract_phc_device() {
  local exec_start
  exec_start=$(get_systemctl_property "$phc2sys_unit" ExecStart)
  printf '%s\n' "$exec_start" | sed -n 's/.*-s \/dev\/\([^ ;][^ ]*\).*/\1/p' | head -n 1
}

check_unit_enabled_active() {
  local unit=$1
  local expected_active=$2
  local enabled active substate

  enabled=$(get_systemctl_property "$unit" UnitFileState)
  active=$(get_systemctl_property "$unit" ActiveState)
  substate=$(get_systemctl_property "$unit" SubState)

  if [[ "$enabled" == "enabled" ]]; then
    pass "$unit is enabled"
  else
    fail "$unit is not enabled (state: ${enabled:-unknown})"
  fi

  if [[ "$active" == "$expected_active" ]]; then
    pass "$unit active state is $active${substate:+/$substate}"
  else
    fail "$unit active state is ${active:-unknown}${substate:+/$substate}, expected $expected_active"
  fi
}

check_marker() {
  if [[ -f /var/lib/ocudu/dpdk-ready ]]; then
    pass "readiness marker exists at /var/lib/ocudu/dpdk-ready"
  else
    fail "readiness marker missing at /var/lib/ocudu/dpdk-ready"
  fi
}

check_time_sync_conflicts() {
  local ntp_value
  ntp_value=$(timedatectl show -p NTP --value 2>/dev/null || true)
  ntp_value=$(trim "$ntp_value")
  if [[ "$ntp_value" == "no" ]]; then
    pass "timedatectl NTP is disabled"
  else
    fail "timedatectl NTP is ${ntp_value:-unknown}, expected no"
  fi

  if systemctl list-unit-files systemd-timesyncd.service >/dev/null 2>&1; then
    if systemctl is-active --quiet systemd-timesyncd.service; then
      fail "systemd-timesyncd.service is still active"
    else
      pass "systemd-timesyncd.service is inactive"
    fi
  fi

  if systemctl list-unit-files ntpsec.service >/dev/null 2>&1; then
    if systemctl is-active --quiet ntpsec.service; then
      fail "ntpsec.service is still active"
    else
      pass "ntpsec.service is inactive"
    fi
  fi
}

check_hugepages() {
  local path count
  path=/sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages
  if [[ ! -r "$path" ]]; then
    fail "cannot read hugepages count from $path"
    return
  fi

  count=$(<"$path")
  count=$(trim "$count")
  if [[ "$count" =~ ^[0-9]+$ ]] && (( count > 0 )); then
    pass "1G hugepages configured: $count"
  else
    fail "1G hugepages count is ${count:-invalid}, expected > 0"
  fi
}

resolve_vf_bdf() {
  local pf_iface=$1
  local vf_sysfs

  vf_sysfs=$(readlink -f "/sys/class/net/${pf_iface}/device/virtfn0" 2>/dev/null || true)
  if [[ -z "$vf_sysfs" || ! -e "$vf_sysfs" ]]; then
    return 1
  fi

  basename "$vf_sysfs"
}

check_driver_binding() {
  local pf_iface=$1
  local vf_bdf current_driver

  vf_bdf=$(resolve_vf_bdf "$pf_iface" || true)
  if [[ -z "$vf_bdf" ]]; then
    fail "could not resolve VF 0 sysfs path for PF interface ${pf_iface}"
    return
  fi

  current_driver=$(basename "$(readlink -f "/sys/bus/pci/devices/${vf_bdf}/driver" 2>/dev/null || true)")
  if [[ -z "$current_driver" ]]; then
    fail "VF is not currently bound to any PCI driver: ${vf_bdf}"
    return
  fi

  if [[ "$current_driver" == "vfio-pci" ]]; then
    pass "VF is bound to vfio-pci: ${vf_bdf}"
  else
    fail "VF is bound to ${current_driver}, expected vfio-pci: ${vf_bdf}"
  fi
}

check_pf_tuning() {
  local pf_iface=$1
  local qdisc txqlen ring_output coalesce_output features_output pause_output

  qdisc=$(tc qdisc show dev "$pf_iface" 2>/dev/null || true)
  if [[ "$qdisc" == *" fq "* ]] || [[ "$qdisc" == fq* ]]; then
    pass "$pf_iface root qdisc includes fq"
  else
    fail "$pf_iface root qdisc does not include fq"
  fi

  txqlen=$(ip -o link show dev "$pf_iface" 2>/dev/null | sed -n 's/.*qlen \([0-9]\+\).*/\1/p')
  if [[ "$txqlen" == "10000" ]]; then
    pass "$pf_iface txqueuelen is 10000"
  else
    fail "$pf_iface txqueuelen is ${txqlen:-unknown}, expected 10000"
  fi

  ring_output=$(ethtool -g "$pf_iface" 2>/dev/null || true)
  if [[ "$ring_output" == *"RX:"*"8160"* ]] && [[ "$ring_output" == *"TX:"*"2048"* ]]; then
    pass "$pf_iface ring sizes include rx 8160 and tx 2048"
  else
    warn "could not confirm ring sizes rx 8160 / tx 2048 on $pf_iface"
  fi

  coalesce_output=$(ethtool -c "$pf_iface" 2>/dev/null || true)
  if [[ "$coalesce_output" == *"rx-usecs: 16"* ]] && [[ "$coalesce_output" == *"tx-usecs: 16"* ]]; then
    pass "$pf_iface coalescing includes rx-usecs 16 and tx-usecs 16"
  else
    warn "could not confirm coalescing rx-usecs 16 / tx-usecs 16 on $pf_iface"
  fi
  if [[ "$coalesce_output" == *"Adaptive RX: off"* ]] && [[ "$coalesce_output" == *"Adaptive TX: off"* ]]; then
    pass "$pf_iface adaptive coalescing is off"
  else
    warn "could not confirm adaptive coalescing is off on $pf_iface"
  fi

  features_output=$(ethtool -k "$pf_iface" 2>/dev/null || true)
  if [[ "$features_output" == *"tcp-segmentation-offload: on"* ]] &&
     [[ "$features_output" == *"generic-segmentation-offload: on"* ]] &&
     [[ "$features_output" == *"generic-receive-offload: on"* ]]; then
    pass "$pf_iface major segmentation offloads are enabled"
  else
    warn "could not confirm TSO/GSO/GRO are enabled on $pf_iface"
  fi
  if [[ "$features_output" == *"large-receive-offload: off"* ]]; then
    pass "$pf_iface LRO is off"
  else
    warn "could not confirm LRO is off on $pf_iface"
  fi

  pause_output=$(ethtool -a "$pf_iface" 2>/dev/null || true)
  if [[ "$pause_output" == *"RX: on"* ]] && [[ "$pause_output" == *"TX: on"* ]]; then
    pass "$pf_iface pause parameters have RX/TX on"
  else
    warn "could not confirm pause parameters RX/TX on for $pf_iface"
  fi
}

check_phc_device() {
  local phc_device=$1
  if [[ -n "$phc_device" && -e "/dev/$phc_device" ]]; then
    pass "PHC device exists: /dev/$phc_device"
  else
    fail "PHC device missing: /dev/${phc_device:-unknown}"
  fi
}

check_recent_logs() {
  local unit=$1
  local lines
  lines=$(journalctl -u "$unit" -b -n 5 --no-pager 2>/dev/null || true)
  if [[ -n "$lines" ]]; then
    pass "$unit has recent boot log entries"
  else
    warn "$unit has no recent boot log entries"
  fi
}

usage() {
  cat <<'EOF'
Usage: verify-dpdk-services.sh [--pf IFACE]

Verifies the OCUDU DPDK host preparation performed by make ocudu-dpdk-install.
Defaults:
  --pf      auto-detect from OCUDU ptp4l unit ExecStart
EOF
}

main() {
  local pf_iface=""
  local phc_device
  local vf_bdf=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --pf)
        pf_iface=${2:-}
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        say "Unknown argument: $1"
        usage
        exit 2
        ;;
    esac
  done

  require_command systemctl || exit 2
  require_command timedatectl || exit 2
  require_command tc || exit 2
  require_command ip || exit 2
  require_command ethtool || exit 2
  require_command journalctl || exit 2

  check_marker
  check_unit_enabled_active vf-bootstrap.service active
  check_unit_enabled_active pf-tuning.service active
  check_unit_enabled_active "$ptp4l_unit" active
  check_unit_enabled_active "$phc2sys_unit" active
  check_time_sync_conflicts
  if [[ -z "$pf_iface" ]]; then
    pf_iface=$(extract_pf_iface)
  fi
  pf_iface=$(trim "$pf_iface")
  if [[ -z "$pf_iface" ]]; then
    fail "could not auto-detect PF interface from ${ptp4l_unit}; pass --pf <iface>"
  elif [[ -d "/sys/class/net/$pf_iface" ]]; then
    pass "PF interface detected: $pf_iface"
    vf_bdf=$(resolve_vf_bdf "$pf_iface" || true)
    check_hugepages
    check_driver_binding "$pf_iface"
    check_pf_tuning "$pf_iface"
  else
    fail "PF interface does not exist: $pf_iface"
  fi

  phc_device=$(extract_phc_device)
  phc_device=$(trim "$phc_device")
  check_phc_device "$phc_device"

  check_recent_logs vf-bootstrap.service
  check_recent_logs pf-tuning.service
  check_recent_logs "$ptp4l_unit"
  check_recent_logs "$phc2sys_unit"

  say
  say "Summary: ${failures} failure(s), ${warnings} warning(s)"
  say "VF PCI address: ${vf_bdf:-unknown}"
  if (( failures > 0 )); then
    exit 1
  fi
}

main "$@"
