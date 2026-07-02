#!/bin/sh
# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -eu

action="${1:-start}"

{% set peer_gnbsim_nodes = [] %}
{% if inventory_hostname in groups['master_nodes'] %}
{% set peer_gnbsim_nodes = play_hosts | intersect(groups['gnbsim_nodes']) | difference(groups['master_nodes']) | list %}
{% endif %}

case "$action" in
  start)
{% if inventory_hostname in groups['master_nodes'] %}
{% if peer_gnbsim_nodes | length > 0 %}
{% for item in peer_gnbsim_nodes %}
    /usr/sbin/ip route replace {{ gnbsim.router.macvlan.subnet_prefix }}.{{ lookup('ansible.utils.index_of', groups['gnbsim_nodes'], 'eq', item) }}.0/24 via {{ hostvars[item]['ansible_default_ipv4']['address'] }}
{% endfor %}
{% else %}
  :
{% endif %}
{% elif inventory_hostname in groups['gnbsim_nodes'] %}
    /usr/sbin/ip route replace {{ core.upf.access_subnet | regex_replace('[0-9]+/24', '0/24') }} via {{ core.amf.ip }}
{% endif %}
    ;;
  stop)
{% if inventory_hostname in groups['master_nodes'] %}
{% if peer_gnbsim_nodes | length > 0 %}
{% for item in peer_gnbsim_nodes %}
    /usr/sbin/ip route del {{ gnbsim.router.macvlan.subnet_prefix }}.{{ lookup('ansible.utils.index_of', groups['gnbsim_nodes'], 'eq', item) }}.0/24 via {{ hostvars[item]['ansible_default_ipv4']['address'] }} || true
{% endfor %}
{% else %}
  :
{% endif %}
{% elif inventory_hostname in groups['gnbsim_nodes'] %}
    /usr/sbin/ip route del {{ core.upf.access_subnet | regex_replace('[0-9]+/24', '0/24') }} via {{ core.amf.ip }} || true
{% endif %}
    ;;
  *)
    echo "usage: $0 {start|stop}" >&2
    exit 1
    ;;
esac
