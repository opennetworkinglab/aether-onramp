# SPDX-FileCopyrightText: 2026-present Intel Corporation
# SPDX-License-Identifier: Apache-2.0
"""Resolve `core.networks` and `core.upf.instances` into the facts the 5GC
roles consume.

Everything in `core.networks` and `core.upf.instances` is optional. Leaving
both out describes today's collapsed deployment: one UPF, both sides attached
as macvlan children of the default-route interface, the host acting as the
gateway on `192.168.252.0/24` (access, N3) and `192.168.250.0/24` (core, N6).
Every field has a constant default, so the result is a pure function of the
`core` dict plus the one host fact passed in; nothing is inherited from a
parent key and nothing depends on the order keys appear in.

The host-dependent steps - deriving `ran_subnet` from an interface's address,
checking that interfaces exist, refusing to move the default-route interface
into a pod - stay in `tasks/upf_networks.yml`, which calls this filter twice:
once to learn which networks need a derived `ran_subnet`, and once more with
the derived values.

Configuration errors raise AnsibleFilterError with the offending key path, so
the install stops before anything is rendered or deployed.
"""

import ipaddress
import re

from ansible.errors import AnsibleFilterError

# A network name becomes the macvlan interface the host creates for it, so it
# is bound by IFNAMSIZ (16 including the terminator). An instance name becomes
# part of a Kubernetes namespace (`aether-upf-<name>`), so with that 11-byte
# prefix it must fit a 63-character DNS label.
_NETWORK_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,14}$")
_INSTANCE_NAME = re.compile(r"^[a-z0-9]([a-z0-9-]{0,50}[a-z0-9])?$")
_IFNAMSIZ = 15

_NETWORK_KEYS = {"iface", "vlan", "subnet", "gateway", "attach", "resource_name", "ran_subnet"}
# set only by _translate_retired: the host-gateway address an older install used
_PRIVATE_NETWORK_KEYS = {"_gateway_address"}
_INSTANCE_KEYS = {"access", "core", "ue_ip_pool", "mode"}
_SIDE_KEYS = {"network", "ip"}

_ATTACH = ("macvlan", "host-device")
_MODES = ("af_packet", "dpdk")

# The two networks that exist whether or not they are configured. Their
# subnets and SR-IOV pool names are the values OnRamp has always shipped.
_NETWORK_DEFAULTS = {
    "access": {"subnet": "192.168.252.0/24", "resource_name": "intel.com/intel_sriov_vfio_access"},
    "core": {"subnet": "192.168.250.0/24", "resource_name": "intel.com/intel_sriov_vfio_core"},
}
# The built-in UPF. It is rendered into the sd-core release rather than
# deployed as its own bess-upf release, and it always exists.
_BUILTIN = "default"
_BUILTIN_UE_POOL = "192.168.100.0/24"
# Host index of a UPF's address within its network when not configured. The
# host itself takes the first address when it is the gateway.
_UPF_HOST_INDEX = 3


def _err(path, msg):
    raise AnsibleFilterError("%s: %s" % (path, msg))


def _dict(value, path):
    if value is None:
        return {}
    if not isinstance(value, dict):
        _err(path, "must be a mapping, got %s" % type(value).__name__)
    return value


def _reject_unknown(d, allowed, path):
    unknown = sorted(set(d) - allowed)
    if unknown:
        _err(path, "unknown key(s) %s; allowed: %s" % (", ".join(unknown), ", ".join(sorted(allowed))))


def _cidr(value, path, min_prefix=8, max_prefix=30):
    """An IPv4 network in CIDR form with no host bits set."""
    try:
        net = ipaddress.IPv4Network(str(value), strict=True)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as exc:
        _err(path, "%r is not an IPv4 network in CIDR form with no host bits (%s)" % (value, exc))
    if not min_prefix <= net.prefixlen <= max_prefix:
        _err(path, "%s: prefix length must be between /%d and /%d" % (value, min_prefix, max_prefix))
    return net


def _address_in(value, net, path):
    try:
        addr = ipaddress.IPv4Address(str(value))
    except (ipaddress.AddressValueError, ValueError):
        _err(path, "%r is not an IPv4 address" % (value,))
    if addr not in net or addr == net.network_address or addr == net.broadcast_address:
        _err(path, "%s is not a usable host address in %s" % (addr, net))
    return addr


def _resolve_network(name, raw, default_iface, role, mode, ran_subnets, require_iface):
    path = "core.networks.%s" % name
    if not _NETWORK_NAME.match(name):
        _err(path, "network names become interface names: lowercase letters, digits, '-' or '_', at most %d characters" % _IFNAMSIZ)
    raw = _dict(raw, path)
    _reject_unknown(raw, _NETWORK_KEYS | (_PRIVATE_NETWORK_KEYS if not require_iface else set()), path)
    defaults = _NETWORK_DEFAULTS.get(name, {})

    iface = str(raw.get("iface") or default_iface or "")
    if not iface and require_iface:
        _err(path + ".iface", "not set, and this host has no IPv4 default route to derive it from")

    vlan = raw.get("vlan")
    if vlan is not None:
        if isinstance(vlan, bool) or not isinstance(vlan, int) or not 1 <= vlan <= 4094:
            _err(path + ".vlan", "%r is not a VLAN id between 1 and 4094" % (vlan,))
        parent = "%s.%d" % (iface, vlan)
        if len(parent) > _IFNAMSIZ:
            _err(path + ".vlan", "'%s' exceeds the %d-character interface name limit" % (parent, _IFNAMSIZ))
    else:
        parent = iface

    if "subnet" in raw:
        subnet = _cidr(raw["subnet"], path + ".subnet")
    elif "subnet" in defaults:
        subnet = ipaddress.IPv4Network(defaults["subnet"])
    else:
        _err(path + ".subnet", "required for a network other than 'access' or 'core'")

    attach = raw.get("attach", "macvlan")
    if attach not in _ATTACH:
        _err(path + ".attach", "%r is not one of %s" % (attach, ", ".join(_ATTACH)))
    if mode == "dpdk" and "attach" in raw:
        _err(path + ".attach", "a dpdk UPF attaches through SR-IOV (vfioveth); 'attach' only applies in af_packet mode")

    gateway_raw = raw.get("gateway", "host")
    host_gateway = gateway_raw == "host"
    if host_gateway:
        if attach == "host-device":
            _err(path + ".gateway", "host-device moves the interface into the UPF pod, so this host cannot be the gateway on it; set gateway to the address of the router on that network")
        gateway = _address_in(raw["_gateway_address"], subnet, path + ".gateway") if raw.get("_gateway_address") else subnet.network_address + 1
    else:
        gateway = _address_in(gateway_raw, subnet, path + ".gateway")

    resource_name = raw.get("resource_name", defaults.get("resource_name"))
    if mode == "dpdk" and not resource_name:
        _err(path + ".resource_name", "required in dpdk mode for a network other than 'access' or 'core'")
    if "resource_name" in raw and mode != "dpdk":
        _err(path + ".resource_name", "only applies in dpdk mode")

    ran_subnet = ""
    if "ran_subnet" in raw and role != "access":
        _err(path + ".ran_subnet", "only applies to a network a UPF uses as its access (N3) side")
    if role == "access":
        ran_raw = raw.get("ran_subnet", "")
        if ran_raw in (None, ""):
            ran_subnet = str(ran_subnets.get(name, ""))
            if ran_subnet:
                _cidr(ran_subnet, path + ".ran_subnet (derived from %s)" % parent)
        else:
            ran_subnet = str(_cidr(ran_raw, path + ".ran_subnet"))

    return {
        "name": name,
        "iface": iface,
        "vlan": vlan,
        "parent": parent,
        "subnet": str(subnet),
        "prefix": subnet.prefixlen,
        "gateway": str(gateway),
        "host_gateway": host_gateway,
        "attach": attach,
        "resource_name": resource_name,
        "role": role,
        "mode": mode,
        "ran_subnet": ran_subnet,
        "needs_ran_subnet": role == "access" and ran_subnet == "",
    }


def _instance_sides(name, raw, default_mode):
    """First pass over an instance: which networks it uses, and how."""
    path = "core.upf.instances.%s" % name
    if not _INSTANCE_NAME.match(name):
        _err(path, "instance names become Kubernetes namespaces (aether-upf-<name>): lowercase letters, digits and '-', starting and ending alphanumeric, at most 52 characters")
    raw = _dict(raw, path)
    _reject_unknown(raw, _INSTANCE_KEYS, path)
    mode = raw.get("mode", default_mode)
    if mode not in _MODES:
        _err(path + ".mode", "%r is not one of %s" % (mode, ", ".join(_MODES)))
    sides = {}
    for side in ("access", "core"):
        side_raw = _dict(raw.get(side), "%s.%s" % (path, side))
        _reject_unknown(side_raw, _SIDE_KEYS, "%s.%s" % (path, side))
        sides[side] = {"network": str(side_raw.get("network", side)), "ip": side_raw.get("ip")}
    if sides["access"]["network"] == sides["core"]["network"]:
        _err(path, "access and core must use different networks (both use '%s')" % sides["access"]["network"])
    return mode, sides


def _translate_retired(core):
    """Express a pre-networks config (data_iface, access_subnet, ...) in the
    current shape, for callers that resolve non-strictly: uninstall and the
    RAN-side roles must act on what an older install actually built, not on
    the defaults. Install itself refuses these keys (tasks/upf_networks.yml).
    """
    core = dict(core)
    upf = dict(_dict(core.get("upf"), "core.upf"))
    nets = {k: dict(_dict(v, "core.networks.%s" % k)) for k, v in _dict(core.get("networks"), "core.networks").items()}
    insts = {k: dict(_dict(v, "core.upf.instances.%s" % k)) for k, v in _dict(upf.get("instances"), "core.upf.instances").items()}
    access, cnet = nets.setdefault("access", {}), nets.setdefault("core", {})
    default = insts.setdefault(_BUILTIN, {})

    if core.get("data_iface") not in (None, "", "data"):
        access.setdefault("iface", core["data_iface"]); cnet.setdefault("iface", core["data_iface"])
    if core.get("data_iface_n6"):
        cnet["iface"] = core["data_iface_n6"]
    if core.get("ran_subnet"):
        access.setdefault("ran_subnet", core["ran_subnet"])
    # the old keys carried the gateway address with the subnet's prefix, and
    # multihop_gnb (later access_overlay) said whether the host built the
    # access overlay or the gNBs' own router was the gateway
    overlay = not upf.get("multihop_gnb", False) if "multihop_gnb" in upf else upf.get("access_overlay", True)
    for key, net, hosted in (("access_subnet", access, overlay), ("core_subnet", cnet, True)):
        if upf.get(key):
            iface = ipaddress.IPv4Interface(str(upf[key]))
            net.setdefault("subnet", str(iface.network))
            net.setdefault("gateway", "host" if hosted else str(iface.ip))
            if hosted:
                net.setdefault("_gateway_address", str(iface.ip))
    for key, net in (("access_resource_name", access), ("core_resource_name", cnet)):
        if upf.get(key) and upf.get("mode") == "dpdk":
            net.setdefault("resource_name", upf[key])
    for key, net in (("access_cni_plugin", access), ("core_cni_plugin", cnet)):
        if upf.get(key) == "host-device":
            net.setdefault("attach", "host-device")
    def side_ips(entry, inst):
        ips = _dict(_dict(entry, "upf").get("ip"), "upf.ip")
        for role in ("access", "core"):
            if ips.get(role):
                inst.setdefault(role, {}); inst[role].setdefault("ip", ips[role])
        if entry.get("ue_ip_pool"):
            inst.setdefault("ue_ip_pool", entry["ue_ip_pool"])
    if upf.get("default_upf"):
        side_ips(upf["default_upf"], default)
    for name, entry in _dict(upf.get("additional_upfs"), "core.upf.additional_upfs").items():
        side_ips(_dict(entry, "core.upf.additional_upfs.%s" % name), insts.setdefault(str(name), {}))

    nets = {k: v for k, v in nets.items() if v or k in _NETWORK_DEFAULTS}
    upf["instances"] = insts
    core["networks"] = nets
    core["upf"] = upf
    return core


_RETIRED_CORE = ("data_iface", "data_iface_n6", "ran_subnet")
_RETIRED_UPF = ("access_subnet", "core_subnet", "multihop_gnb", "access_overlay", "access_resource_name",
                "core_resource_name", "access_cni_plugin", "core_cni_plugin", "default_upf", "additional_upfs")


def resolve_upf_networks(core, default_iface="", ran_subnets=None, strict=True):
    """Return {'networks': {...}, 'instances': {...}} for the `core` dict.

    `default_iface` is the host's default-route interface, used for any
    network that does not name one. `ran_subnets` maps network name to the
    CIDR derived on the host for access networks that left `ran_subnet`
    empty; pass the result of the first call's `needs_ran_subnet` lookups.
    With `strict` false a network may resolve with no interface at all, for
    callers that only need subnets and gateways (RAN-side roles, uninstall)
    on hosts that may have no default route, and a config still written with
    the retired keys is translated rather than ignored, so cleanup acts on
    what that install built.
    """
    core = _dict(core, "core")
    ran_subnets = _dict(ran_subnets, "ran_subnets")
    if not strict and (any(k in core for k in _RETIRED_CORE) or any(k in _dict(core.get("upf"), "core.upf") for k in _RETIRED_UPF)):
        core = _translate_retired(core)
    networks_raw = _dict(core.get("networks"), "core.networks")
    upf = _dict(core.get("upf"), "core.upf")
    default_mode = upf.get("mode", "af_packet")
    if default_mode not in _MODES:
        _err("core.upf.mode", "%r is not one of %s" % (default_mode, ", ".join(_MODES)))
    instances_raw = dict(_dict(upf.get("instances"), "core.upf.instances"))
    instances_raw.setdefault(_BUILTIN, {})

    # Pass over instances first: a network's role (access or core) and mode
    # come from the instances that use it, and a network nobody uses is a
    # typo rather than something to build.
    usage = {}  # network name -> {"role": ..., "mode": ..., "users": [...]}
    sides_by_instance = {}
    for inst_name in sorted(instances_raw):
        mode, sides = _instance_sides(inst_name, instances_raw[inst_name], default_mode)
        sides_by_instance[inst_name] = (mode, sides)
        for role, side in sides.items():
            net = side["network"]
            if net not in networks_raw and net not in _NETWORK_DEFAULTS:
                _err("core.upf.instances.%s.%s.network" % (inst_name, role), "'%s' is not defined in core.networks" % net)
            use = usage.setdefault(net, {"role": role, "mode": mode, "users": []})
            if use["role"] != role:
                _err("core.networks.%s" % net, "used as the %s side by '%s' and the %s side by '%s'; a network serves one side" % (use["role"], use["users"][0], role, inst_name))
            if use["mode"] != mode:
                _err("core.networks.%s" % net, "used by '%s' (%s) and '%s' (%s); the attachment differs by mode, so they need separate networks" % (use["users"][0], use["mode"], inst_name, mode))
            use["users"].append(inst_name)
    for net in sorted(set(networks_raw) - set(usage)):
        _err("core.networks.%s" % net, "is not used by any UPF instance (check core.upf.instances.*.access.network / core.network)")

    networks = {}
    for net in sorted(usage):
        networks[net] = _resolve_network(net, networks_raw.get(net), default_iface, usage[net]["role"], usage[net]["mode"], ran_subnets, strict)
    # A network's name becomes a macvlan interface the host creates, so it
    # must not collide with an interface any network attaches through.
    taken = {n[k] for n in networks.values() for k in ("iface", "parent") if n[k]}
    for net in sorted(networks):
        if net in taken:
            _err("core.networks.%s" % net, "the name would become a macvlan interface, but an interface of that name is one a network attaches through")
    # host-device moves the interface into one pod, so nothing else can
    # attach through it: no second network on that parent, no second UPF.
    for net in sorted(networks):
        n = networks[net]
        if n["attach"] != "host-device" or not n["parent"]:
            continue
        for other in sorted(networks):
            if other != net and networks[other]["parent"] == n["parent"]:
                _err("core.networks.%s" % net, "host-device moves %s into the UPF pod, but network '%s' also attaches through it" % (n["parent"], other))
            if other != net and n["vlan"] is None and networks[other]["iface"] == n["iface"]:
                _err("core.networks.%s" % net, "host-device moves %s into the UPF pod, but network '%s' attaches through a VLAN child of it" % (n["iface"], other))
        if len(usage[net]["users"]) > 1:
            _err("core.networks.%s" % net, "host-device moves %s into one UPF pod, but UPFs %s all use this network" % (n["parent"], ", ".join("'%s'" % u for u in usage[net]["users"])))

    # every address this host itself holds, per interface: a UPF must not take
    # any of them, whichever network it is attached through
    host_gateways = {}
    for net in sorted(networks):
        n = networks[net]
        if n["host_gateway"]:
            key = (n["parent"] or n["name"], n["gateway"])
            if key in host_gateways:
                _err("core.networks.%s" % net, "this host would hold %s on %s for both '%s' and this network" % (n["gateway"], key[0], host_gateways[key]))
            host_gateways[key] = net

    instances = {}
    used_addresses = {}  # (interface, ip) -> instance
    pools = {}  # instance -> IPv4Network
    for inst_name in sorted(sides_by_instance):
        mode, sides = sides_by_instance[inst_name]
        path = "core.upf.instances.%s" % inst_name
        raw = _dict(instances_raw[inst_name], path)
        if mode == "dpdk":
            a, c = networks[sides["access"]["network"]], networks[sides["core"]["network"]]
            if a["parent"] != c["parent"]:
                _err(path, "in dpdk mode both sides must be on the same interface (access on %s, core on %s): the SR-IOV preflight validates one PF per UPF" % (a["parent"], c["parent"]))
        if "ue_ip_pool" in raw:
            pool = _cidr(raw["ue_ip_pool"], path + ".ue_ip_pool")
        elif inst_name == _BUILTIN:
            pool = ipaddress.IPv4Network(_BUILTIN_UE_POOL)
        else:
            _err(path + ".ue_ip_pool", "required for a UPF other than 'default'")
        for other, other_pool in pools.items():
            if pool.overlaps(other_pool):
                _err(path + ".ue_ip_pool", "%s overlaps %s used by '%s'" % (pool, other_pool, other))
        pools[inst_name] = pool

        resolved = {"name": inst_name, "builtin": inst_name == _BUILTIN, "mode": mode, "ue_ip_pool": str(pool)}
        for role, side in sides.items():
            net = networks[side["network"]]
            subnet = ipaddress.IPv4Network(net["subnet"])
            side_path = "%s.%s.ip" % (path, role)
            if side["ip"] is None:
                ip = subnet.network_address + _UPF_HOST_INDEX
                if ip >= subnet.broadcast_address:
                    _err(side_path, "not set and %s is too small to hold the default address (.%d)" % (subnet, _UPF_HOST_INDEX))
            else:
                ip = _address_in(side["ip"], subnet, side_path)
            if str(ip) == net["gateway"]:
                _err(side_path, "%s is the gateway address of network '%s'" % (ip, net["name"]))
            owner = host_gateways.get((net["parent"] or net["name"], str(ip)))
            if owner:
                _err(side_path, "%s is the address this host holds on %s as the gateway of network '%s'" % (ip, net["parent"] or net["name"], owner))
            # two networks on one interface are one L2 domain, whatever they are called
            key = (net["parent"] or net["name"], str(ip))
            if key in used_addresses:
                _err(side_path, "%s on %s is already used by '%s'" % (ip, net["parent"] or net["name"], used_addresses[key]))
            used_addresses[key] = inst_name
            resolved[role] = {
                "network": net["name"],
                "ip": str(ip),
                "ip_cidr": "%s/%d" % (ip, net["prefix"]),
                "subnet": net["subnet"],
                "gateway": net["gateway"],
                "host_gateway": net["host_gateway"],
                "iface": net["parent"],
                "cni": "vfioveth" if mode == "dpdk" else net["attach"],
                "resource_name": net["resource_name"] if mode == "dpdk" else None,
            }
            if role == "access":
                resolved[role]["ran_subnet"] = net["ran_subnet"]
        instances[inst_name] = resolved

    return {"networks": networks, "instances": instances}


class FilterModule(object):
    def filters(self):
        return {"resolve_upf_networks": resolve_upf_networks}
