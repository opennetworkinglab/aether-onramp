# SPDX-FileCopyrightText: 2026-present Intel Corporation
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the `resolve_upf_networks` filter.

Run with `pytest tests/` from the repository root. The filter is a pure
function of the `core` dict, so none of this needs a host, a cluster or
Ansible's runtime; only `ansible.errors` for the exception type.
"""

import copy
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "deps", "common", "roles", "preflight", "filter_plugins"))

from ansible.errors import AnsibleFilterError  # noqa: E402
from upf_networks import resolve_upf_networks  # noqa: E402

IFACE = "eno1"


def resolve(core=None, **kw):
    return resolve_upf_networks(copy.deepcopy(core or {}), IFACE, **kw)


def fails(core, *fragments, **kw):
    with pytest.raises(AnsibleFilterError) as info:
        resolve(core, **kw)
    for fragment in fragments:
        assert fragment in str(info.value), str(info.value)


# ---------------------------------------------------------------- defaults

def test_empty_config_is_todays_collapsed_deployment():
    r = resolve({})
    assert set(r["networks"]) == {"access", "core"}
    assert set(r["instances"]) == {"default"}

    access, core = r["networks"]["access"], r["networks"]["core"]
    for net, subnet, gw in ((access, "192.168.252.0/24", "192.168.252.1"), (core, "192.168.250.0/24", "192.168.250.1")):
        assert net["iface"] == net["parent"] == IFACE
        assert net["vlan"] is None
        assert (net["subnet"], net["prefix"], net["gateway"]) == (subnet, 24, gw)
        assert net["host_gateway"] is True
        assert net["attach"] == "macvlan"
        assert net["mode"] == "af_packet"
    assert access["role"] == "access" and core["role"] == "core"
    assert access["needs_ran_subnet"] is True and access["ran_subnet"] == ""
    assert core["needs_ran_subnet"] is False

    d = r["instances"]["default"]
    assert d["builtin"] is True and d["mode"] == "af_packet"
    assert d["ue_ip_pool"] == "192.168.100.0/24"
    assert d["access"] == {
        "network": "access", "ip": "192.168.252.3", "ip_cidr": "192.168.252.3/24", "subnet": "192.168.252.0/24",
        "gateway": "192.168.252.1", "host_gateway": True, "iface": IFACE, "cni": "macvlan", "resource_name": None,
        "ran_subnet": "",
    }
    assert d["core"]["ip_cidr"] == "192.168.250.3/24" and d["core"]["gateway"] == "192.168.250.1"
    assert "ran_subnet" not in d["core"]


def test_no_default_route_and_no_iface_is_an_error():
    with pytest.raises(AnsibleFilterError, match="core.networks.access.iface: not set"):
        resolve_upf_networks({}, "")


def test_non_strict_tolerates_a_missing_interface():
    r = resolve_upf_networks({}, "", strict=False)
    assert r["networks"]["access"]["iface"] == "" and r["networks"]["access"]["parent"] == ""
    assert r["instances"]["default"]["access"]["subnet"] == "192.168.252.0/24"
    assert r["instances"]["default"]["core"]["gateway"] == "192.168.250.1"


def test_network_name_must_not_be_an_attachment_interface():
    fails({"networks": {"eno1": {"subnet": "10.0.0.0/24"}}, "upf": {"instances": {"default": {"core": {"network": "eno1"}}}}},
          "core.networks.eno1: the name would become a macvlan interface")
    fails({"networks": {"core": {"iface": "eno2", "vlan": 7}, "eno2.7": {"subnet": "10.0.0.0/24"}},
           "upf": {"instances": {"b": {"access": {"network": "eno2.7"}, "ue_ip_pool": "10.9.0.0/24"}}}},
          "core.networks.eno2.7")


def test_ran_subnet_second_pass():
    first = resolve({})
    assert first["networks"]["access"]["needs_ran_subnet"]
    second = resolve({}, ran_subnets={"access": "10.76.28.0/24"})
    assert second["networks"]["access"]["ran_subnet"] == "10.76.28.0/24"
    assert second["networks"]["access"]["needs_ran_subnet"] is False
    assert second["instances"]["default"]["access"]["ran_subnet"] == "10.76.28.0/24"


def test_explicit_ran_subnet_wins_over_derived():
    r = resolve({"networks": {"access": {"ran_subnet": "172.20.0.0/16"}}}, ran_subnets={"access": "10.0.0.0/24"})
    assert r["networks"]["access"]["ran_subnet"] == "172.20.0.0/16"


def test_derived_ran_subnet_is_validated():
    fails({}, "core.networks.access.ran_subnet (derived from eno1)", ran_subnets={"access": "garbage"})


# ------------------------------------------------------------- separation

def test_core_on_second_nic_with_external_gateway():
    r = resolve({"networks": {"core": {"iface": "eno2", "subnet": "10.60.0.0/24", "gateway": "10.60.0.1"}}})
    core = r["networks"]["core"]
    assert core["parent"] == "eno2" and core["host_gateway"] is False and core["gateway"] == "10.60.0.1"
    assert r["networks"]["access"]["parent"] == IFACE
    d = r["instances"]["default"]
    assert d["core"] == {
        "network": "core", "ip": "10.60.0.3", "ip_cidr": "10.60.0.3/24", "subnet": "10.60.0.0/24", "gateway": "10.60.0.1",
        "host_gateway": False, "iface": "eno2", "cni": "macvlan", "resource_name": None,
    }


def test_host_device_requires_external_gateway():
    fails({"networks": {"core": {"iface": "eno2", "attach": "host-device"}}}, "core.networks.core.gateway", "host-device moves the interface")
    r = resolve({"networks": {"core": {"iface": "eno2", "attach": "host-device", "gateway": "192.168.250.1"}}})
    assert r["instances"]["default"]["core"]["cni"] == "host-device"


def test_vlan_parent_naming():
    r = resolve({"networks": {"core": {"vlan": 100}}})
    assert r["networks"]["core"]["parent"] == "eno1.100" and r["networks"]["core"]["iface"] == IFACE
    assert r["instances"]["default"]["core"]["iface"] == "eno1.100"
    fails({"networks": {"core": {"vlan": 0}}}, "core.networks.core.vlan")
    fails({"networks": {"core": {"vlan": 4095}}}, "core.networks.core.vlan")
    fails({"networks": {"core": {"vlan": True}}}, "core.networks.core.vlan")
    fails({"networks": {"core": {"vlan": "100"}}}, "core.networks.core.vlan")
    fails({"networks": {"core": {"iface": "enp123s0f1np1", "vlan": 1000}}}, "interface name limit")


def test_gateway_must_be_inside_subnet():
    fails({"networks": {"core": {"gateway": "10.0.0.1"}}}, "core.networks.core.gateway", "not a usable host address in 192.168.250.0/24")
    fails({"networks": {"core": {"gateway": "192.168.250.0"}}}, "core.networks.core.gateway")
    fails({"networks": {"core": {"gateway": "192.168.250.255"}}}, "core.networks.core.gateway")


def test_subnet_validation():
    fails({"networks": {"core": {"subnet": "192.168.250.1/24"}}}, "core.networks.core.subnet", "no host bits")
    fails({"networks": {"core": {"subnet": "192.168.250.0/31"}}}, "prefix length must be between /8 and /30")
    fails({"networks": {"core": {"subnet": "not-a-subnet"}}}, "core.networks.core.subnet")


def test_unknown_keys_are_rejected():
    fails({"networks": {"core": {"interface": "eno2"}}}, "core.networks.core: unknown key(s) interface")
    fails({"upf": {"instances": {"default": {"ue_pool": "10.0.0.0/24"}}}}, "core.upf.instances.default: unknown key(s) ue_pool")
    fails({"upf": {"instances": {"default": {"core": {"address": "1.2.3.4"}}}}}, "core.upf.instances.default.core: unknown key(s) address")


def test_network_name_rules():
    fails({"networks": {"N6": {"subnet": "10.0.0.0/24"}}, "upf": {"instances": {"default": {"core": {"network": "N6"}}}}}, "core.networks.N6: network names become interface names")
    fails({"networks": {"a-very-long-name-x": {"subnet": "10.0.0.0/24"}}, "upf": {"instances": {"default": {"core": {"network": "a-very-long-name-x"}}}}}, "core.networks.a-very-long-name-x")


def test_unused_and_undefined_networks():
    fails({"networks": {"n6": {"subnet": "10.0.0.0/24"}}}, "core.networks.n6: is not used by any UPF instance")
    fails({"upf": {"instances": {"default": {"core": {"network": "n6"}}}}}, "core.upf.instances.default.core.network: 'n6' is not defined")


def test_custom_network_needs_subnet():
    fails({"networks": {"n6": {}}, "upf": {"instances": {"default": {"core": {"network": "n6"}}}}}, "core.networks.n6.subnet: required")


def test_ran_subnet_only_on_access_side():
    fails({"networks": {"core": {"ran_subnet": "172.20.0.0/16"}}}, "core.networks.core.ran_subnet: only applies")


def test_same_network_both_sides_is_rejected():
    fails({"upf": {"instances": {"default": {"core": {"network": "access"}}}}}, "access and core must use different networks")


# ---------------------------------------------------------------- instances

def test_second_upf_on_its_own_networks():
    core = {
        "networks": {
            "n3b": {"iface": "eno3", "subnet": "10.70.0.0/24"},
            "n6b": {"iface": "eno4", "subnet": "10.80.0.0/24", "gateway": "10.80.0.1"},
        },
        "upf": {"instances": {"edge-2": {
            "access": {"network": "n3b", "ip": "10.70.0.5"},
            "core": {"network": "n6b", "ip": "10.80.0.5"},
            "ue_ip_pool": "172.248.0.0/16",
        }}},
    }
    r = resolve(core)
    assert set(r["networks"]) == {"access", "core", "n3b", "n6b"}
    assert set(r["instances"]) == {"default", "edge-2"}
    e = r["instances"]["edge-2"]
    assert e["builtin"] is False
    assert e["access"]["ip_cidr"] == "10.70.0.5/24" and e["access"]["gateway"] == "10.70.0.1" and e["access"]["host_gateway"]
    assert e["core"]["ip_cidr"] == "10.80.0.5/24" and e["core"]["host_gateway"] is False
    assert r["networks"]["n3b"]["role"] == "access" and r["networks"]["n3b"]["needs_ran_subnet"]
    assert r["networks"]["n6b"]["role"] == "core"
    assert r["instances"]["default"]["ue_ip_pool"] == "192.168.100.0/24"


def test_second_upf_sharing_default_networks():
    r = resolve({"upf": {"instances": {"edge": {"access": {"ip": "192.168.252.6"}, "core": {"ip": "192.168.250.6"}, "ue_ip_pool": "192.168.101.0/24"}}}})
    assert r["instances"]["edge"]["access"]["network"] == "access"
    assert r["networks"]["access"]["parent"] == IFACE


def test_additional_upf_requires_pool_and_unique_addresses():
    fails({"upf": {"instances": {"edge": {}}}}, "core.upf.instances.edge.ue_ip_pool: required")
    fails({"upf": {"instances": {"edge": {"ue_ip_pool": "10.9.0.0/24"}}}}, "core.upf.instances.edge.access.ip", "already used by 'default'")
    fails({"upf": {"instances": {"edge": {"access": {"ip": "192.168.252.6"}, "core": {"ip": "192.168.250.6"}, "ue_ip_pool": "192.168.100.0/25"}}}}, "ue_ip_pool", "overlaps 192.168.100.0/24 used by 'default'")


def test_instance_name_rules():
    fails({"upf": {"instances": {"Edge_1": {"ue_ip_pool": "10.9.0.0/24"}}}}, "core.upf.instances.Edge_1: instance names become Kubernetes namespaces")


def test_ip_must_be_in_subnet_and_not_the_gateway():
    fails({"upf": {"instances": {"default": {"core": {"ip": "10.0.0.3"}}}}}, "core.upf.instances.default.core.ip", "not a usable host address")
    fails({"upf": {"instances": {"default": {"core": {"ip": "192.168.250.1"}}}}}, "is the gateway address of network 'core'")


def test_network_role_and_mode_must_agree_across_instances():
    fails({"networks": {"x": {"subnet": "10.1.0.0/24"}}, "upf": {"instances": {
        "default": {"core": {"network": "x"}},
        "b": {"access": {"network": "x"}, "ue_ip_pool": "10.9.0.0/24"},
    }}}, "core.networks.x: used as the access side by 'b' and the core side by 'default'", "a network serves one side")
    fails({"upf": {"instances": {"b": {"mode": "dpdk", "access": {"ip": "192.168.252.6"}, "core": {"ip": "192.168.250.6"}, "ue_ip_pool": "10.9.0.0/24"}}}},
          "core.networks.access: used by 'b' (dpdk) and 'default' (af_packet)")


# --------------------------------------------------------------------- dpdk

def test_dpdk_defaults_match_todays_sriov_blueprint():
    r = resolve({"upf": {"mode": "dpdk"}})
    d = r["instances"]["default"]
    assert d["mode"] == "dpdk"
    assert d["access"]["cni"] == d["core"]["cni"] == "vfioveth"
    assert d["access"]["resource_name"] == "intel.com/intel_sriov_vfio_access"
    assert d["core"]["resource_name"] == "intel.com/intel_sriov_vfio_core"
    assert r["networks"]["access"]["mode"] == "dpdk"


def test_dpdk_rejects_attach_and_split_interfaces():
    fails({"upf": {"mode": "dpdk"}, "networks": {"core": {"attach": "macvlan"}}}, "core.networks.core.attach: a dpdk UPF attaches through SR-IOV")
    fails({"upf": {"mode": "dpdk"}, "networks": {"core": {"iface": "eno2"}}}, "core.upf.instances.default: in dpdk mode both sides must be on the same interface")
    fails({"upf": {"mode": "dpdk", "instances": {"default": {"core": {"network": "n6"}}}}, "networks": {"n6": {"subnet": "10.0.0.0/24"}}},
          "core.networks.n6.resource_name: required in dpdk mode")


def test_resource_name_only_in_dpdk():
    fails({"networks": {"core": {"resource_name": "intel.com/x"}}}, "core.networks.core.resource_name: only applies in dpdk mode")


def test_mode_values():
    fails({"upf": {"mode": "sriov"}}, "core.upf.mode")
    fails({"upf": {"instances": {"default": {"mode": "fast"}}}}, "core.upf.instances.default.mode")
    r = resolve({"upf": {"mode": "dpdk", "instances": {"default": {"mode": "af_packet"}}}})
    assert r["instances"]["default"]["mode"] == "af_packet"


# ------------------------------------------------------------------ hygiene

def test_input_is_not_mutated():
    core = {"networks": {"core": {"iface": "eno2"}}, "upf": {"instances": {"default": {}}}}
    snapshot = copy.deepcopy(core)
    resolve_upf_networks(core, IFACE)
    assert core == snapshot


def test_none_values_are_treated_as_empty_mappings():
    r = resolve({"networks": None, "upf": {"instances": None}})
    assert set(r["instances"]) == {"default"}
    r = resolve({"networks": {"core": None}})
    assert r["networks"]["core"]["subnet"] == "192.168.250.0/24"


# -------------------------------------------------------------- round three

def test_instance_name_fits_the_namespace():
    ok = "a" * 52
    assert ok in resolve({"upf": {"instances": {ok: {"access": {"ip": "192.168.252.6"}, "core": {"ip": "192.168.250.6"}, "ue_ip_pool": "10.9.0.0/24"}}}})["instances"]
    fails({"upf": {"instances": {"a" * 53: {"ue_ip_pool": "10.9.0.0/24"}}}}, "at most 52 characters")


def test_host_device_parent_is_exclusive():
    fails({"networks": {"access": {"iface": "eno2", "attach": "host-device", "gateway": "192.168.252.1"},
                        "core": {"iface": "eno2"}}},
          "core.networks.access", "network 'core' also attaches through it")
    fails({"networks": {"core": {"iface": "eno2", "attach": "host-device", "gateway": "192.168.250.1"}},
           "upf": {"instances": {"b": {"access": {"ip": "192.168.252.6"}, "core": {"ip": "192.168.250.6"}, "ue_ip_pool": "10.9.0.0/24"}}}},
          "core.networks.core", "UPFs 'b', 'default' all use this network")
    # a VLAN child moving into the pod leaves its base interface usable
    r = resolve({"networks": {"core": {"iface": "eno2", "vlan": 7, "attach": "host-device", "gateway": "192.168.250.1"},
                              "access": {"iface": "eno2"}}})
    assert r["networks"]["core"]["parent"] == "eno2.7" and r["networks"]["access"]["parent"] == "eno2"


LEGACY = {
    "data_iface": "eno9",
    "ran_subnet": "10.20.0.0/16",
    "upf": {
        "access_subnet": "192.168.60.1/24",
        "core_subnet": "192.168.70.1/24",
        "mode": "af_packet",
        "multihop_gnb": False,
        "default_upf": {"ip": {"access": "192.168.60.3", "core": "192.168.70.3"}, "ue_ip_pool": "10.45.0.0/16"},
        "additional_upfs": {"1": {"ip": {"access": "192.168.60.6", "core": "192.168.70.6"}, "ue_ip_pool": "10.46.0.0/16"}},
    },
}


def test_non_strict_translates_a_retired_config():
    r = resolve_upf_networks(copy.deepcopy(LEGACY), "eno1", strict=False)
    a, c = r["networks"]["access"], r["networks"]["core"]
    assert a["parent"] == c["parent"] == "eno9"
    assert (a["subnet"], a["gateway"], a["host_gateway"], a["ran_subnet"]) == ("192.168.60.0/24", "192.168.60.1", True, "10.20.0.0/16")
    assert (c["subnet"], c["gateway"], c["host_gateway"]) == ("192.168.70.0/24", "192.168.70.1", True)
    d, one = r["instances"]["default"], r["instances"]["1"]
    assert d["access"]["ip_cidr"] == "192.168.60.3/24" and d["core"]["ip_cidr"] == "192.168.70.3/24" and d["ue_ip_pool"] == "10.45.0.0/16"
    assert one["access"]["ip"] == "192.168.60.6" and one["core"]["ip"] == "192.168.70.6" and one["ue_ip_pool"] == "10.46.0.0/16"


def test_translation_of_the_overlay_flag_and_strict_ignores_retired_keys():
    # the gNBs' own router is the gateway: the UPF's access side sits in that network
    legacy = copy.deepcopy(LEGACY); del legacy["upf"]["additional_upfs"]
    legacy["upf"]["multihop_gnb"] = True; legacy["upf"]["access_subnet"] = "10.20.0.1/16"
    legacy["upf"]["default_upf"]["ip"]["access"] = "10.20.0.3"
    r = resolve_upf_networks(legacy, "eno1", strict=False)
    assert r["networks"]["access"]["host_gateway"] is False and r["networks"]["access"]["gateway"] == "10.20.0.1"
    legacy2 = copy.deepcopy(legacy); del legacy2["upf"]["multihop_gnb"]; legacy2["upf"]["access_overlay"] = False
    assert resolve_upf_networks(legacy2, "eno1", strict=False)["networks"]["access"]["host_gateway"] is False
    # strict callers never translate: the task-level guard has already refused the keys
    r = resolve_upf_networks(copy.deepcopy(LEGACY), "eno1", strict=True)
    assert r["networks"]["access"]["subnet"] == "192.168.252.0/24" and set(r["instances"]) == {"default"}


def test_translation_keeps_new_keys_when_both_are_present():
    legacy = copy.deepcopy(LEGACY); legacy["networks"] = {"access": {"iface": "eno5"}}
    r = resolve_upf_networks(legacy, "eno1", strict=False)
    assert r["networks"]["access"]["parent"] == "eno5" and r["networks"]["core"]["parent"] == "eno9"


# --------------------------------------------------------------- round four

def test_addresses_are_unique_per_interface_not_per_network_name():
    # n6b's gateway is external so only the UPF addresses collide, not the host's own
    fails({"networks": {"n6b": {"subnet": "192.168.250.0/24", "gateway": "192.168.250.254"}},
           "upf": {"instances": {"b": {"access": {"ip": "192.168.252.6"}, "core": {"network": "n6b"}, "ue_ip_pool": "10.9.0.0/24"}}}},
          "core.upf.instances.default.core.ip", "192.168.250.3 on eno1 is already used by 'b'")
    # the same address on different interfaces is two L2 domains
    r = resolve({"networks": {"n6b": {"iface": "eno2", "subnet": "192.168.250.0/24"}},
                 "upf": {"instances": {"b": {"access": {"ip": "192.168.252.6"}, "core": {"network": "n6b"}, "ue_ip_pool": "10.9.0.0/24"}}}})
    assert r["instances"]["b"]["core"]["ip"] == r["instances"]["default"]["core"]["ip"] == "192.168.250.3"


def test_host_device_on_a_base_interface_with_a_vlan_child_in_use():
    fails({"networks": {"access": {"iface": "eno2", "vlan": 7},
                        "core": {"iface": "eno2", "attach": "host-device", "gateway": "192.168.250.1"}}},
          "core.networks.core", "network 'access' attaches through a VLAN child of it")


def test_translation_keeps_a_legacy_gateway_address():
    legacy = copy.deepcopy(LEGACY); del legacy["upf"]["additional_upfs"]
    legacy["upf"]["core_subnet"] = "192.168.70.254/24"; legacy["upf"]["default_upf"]["ip"]["core"] = "192.168.70.1"
    r = resolve_upf_networks(legacy, "eno1", strict=False)
    assert r["networks"]["core"]["gateway"] == "192.168.70.254" and r["networks"]["core"]["host_gateway"] is True
    assert r["instances"]["default"]["core"]["ip"] == "192.168.70.1"
    # the private key is not accepted from a user's config
    fails({"networks": {"core": {"_gateway_address": "192.168.250.254"}}}, "unknown key(s) _gateway_address")


# --------------------------------------------------------------- round five

def test_upf_address_must_not_be_another_networks_host_gateway_on_the_same_interface():
    fails({"networks": {"n6b": {"subnet": "192.168.250.0/24", "gateway": "192.168.250.254"}},
           "upf": {"instances": {"b": {"access": {"ip": "192.168.252.6"}, "core": {"network": "n6b", "ip": "192.168.250.1"}, "ue_ip_pool": "10.9.0.0/24"}}}},
          "core.upf.instances.b.core.ip", "192.168.250.1 is the address this host holds on eno1 as the gateway of network 'core'")
    fails({"networks": {"n6b": {"subnet": "192.168.250.0/24"}},
           "upf": {"instances": {"b": {"access": {"ip": "192.168.252.6"}, "core": {"network": "n6b", "ip": "192.168.250.6"}, "ue_ip_pool": "10.9.0.0/24"}}}},
          "core.networks.n6b", "this host would hold 192.168.250.1 on eno1 for both 'core' and this network")
