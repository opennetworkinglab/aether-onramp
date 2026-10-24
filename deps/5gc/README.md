# 5gc

The 5gc repository builds a standalone Aether core with a physical RAN setup.
It depends on a k8s cluster, which can be deployed using the k8s repository to create a multi-node cluster.

To set up the 5gc repository, you need to provide the following:

1. Node configurations with IP addresses in the hosts.ini file.
   - You can specify both master and worker nodes.
2. Aether configuration parameters, such as the AMF address and the UPF's networks, in the `./vars/main.yml` file.

To download the 5gc repository, use the following command:
```
git clone https://github.com/omec-project/aether-5gc.git
```
To download the k8s repository used to provision the cluster, use:
```
git clone https://github.com/omec-project/aether-k8s.git
```
### Step-by-Step Installation
To install the 5g-core, follow these steps:
1. Set the configuration variables in the `vars/main.yml` file.
   - Set the "values_file" parameter:
      - Use "roles/core/templates/sdcore-5g-values.yaml" for a stateful 5g core.
      - Set `core.upf.mode` to `dpdk` when you want the built-in UPF rendered with SR-IOV, hugepages, and `vfioveth` networking.
   - The UPF's networking is described by `core.networks` and `core.upf.instances`. Both are optional; see [UPF networking](#upf-networking) below.
2. Add the hosts to `hosts.ini`.
3. Run `make ansible`.
4. In the running Ansible docker terminal:
   - Make sure you have deployed a k8s cluster using `k8s-install` from the k8s repo.
   - Run `make 5gc-install`.
   - It creates the host side of the UPF's networks (the `access` and `core` interfaces by default) using `5gc-router-install`.
   - Finally, it installs the 5g core using the values specified in `5gc-core-install`.
   - When a UPF's mode is `dpdk`, the core and additional UPF install roles validate that the interface its networks sit on has at least two VFs bound to the `vfio-pci` driver before deploying the UPF workload. The chart's SR-IOV device-plugin selector only exposes `vfio-pci`-bound VFs, so VFs bound to any other driver are ignored (they can never be allocated to the UPF pod).
      - If the access and core networks' `resource_name` values are different, the chart pins access/core to `vf 0` and `vf 1` specifically, so those two VFs must be bound to `vfio-pci` and have non-zero MAC addresses.
      - If they are the same, access/core share one SR-IOV resource pool whose selector exposes every `vfio-pci`-bound VF on the interface. The allocator may hand the UPF any of them, so **all** `vfio-pci`-bound VFs on the interface must have non-zero MAC addresses.
      - In dpdk mode both sides of a UPF must be on the same interface.
     - The installation process may take up to 3 minutes.

#### One-Step Installation
To install 5gc in one go, run `make 5gc-install`.
#### Uninstall
   - run `make 5gc-uninstall`

### UPF networking

The UPF has two sides: access (N3, towards the gNBs) and core (N6, towards the
data network). Each side attaches to a *network*, and `core.networks` describes
those networks. `core.upf.instances` lists the UPFs and which network each side
uses. Every field has a default, so with neither key set you get the deployment
OnRamp has always shipped: one UPF, both sides attached as macvlan children of
the interface carrying the host's default route, and this host acting as the
gateway on `192.168.252.0/24` (access) and `192.168.250.0/24` (core).

The install prints the resolved result ("show the resolved UPF networking") so
you can see what the defaults decided before anything is deployed.

```yaml
core:
  networks:
    access:
      ran_subnet: "172.20.0.0/16"   # gNB network; "" derives it from the access interface
  upf:
    instances:
      default:
        ue_ip_pool: "192.168.100.0/24"
```

To put the UPF's sides on different interfaces, name only what differs. Here
the core side moves to a second NIC whose router is not this host:

```yaml
core:
  networks:
    core:
      iface: eno2
      subnet: 10.60.0.0/24
      gateway: 10.60.0.1
```

A network has these fields (all optional):

| field | default | meaning |
|---|---|---|
| `iface` | the default-route interface | host interface the network is reached through |
| `vlan` | none | 802.1Q tag; the UPF attaches to `<iface>.<vlan>`, which `5gc-router-install` creates |
| `subnet` | `192.168.252.0/24` for `access`, `192.168.250.0/24` for `core` | the network, in CIDR form; required for any other network |
| `gateway` | `host` | `host` makes this host the gateway at the subnet's first address: it creates a macvlan interface named after the network, forwards between it and `iface`, routes each UPF's UE pool to that UPF and masquerades the pools on the way out. An address names an external router instead, and the host configures nothing on the network. |
| `attach` | `macvlan` | how the UPF pod attaches in `af_packet` mode. `macvlan` shares the interface; `host-device` moves it into the pod, so the gateway must be external and the interface is absent from the host while the UPF runs. |
| `resource_name` | `intel.com/intel_sriov_vfio_access` / `_core` | SR-IOV pool in `dpdk` mode; required for other networks |
| `ran_subnet` | derived from `iface`'s own subnet | on an access network, the gNB network the UPF routes downlink to. Set it explicitly when the gNBs are not on that interface's L2, or when the interface is moved into the pod by `host-device`. |

A UPF instance has `access` and `core` (each `{network, ip}`, defaulting to the
network of the same name and its third address), `ue_ip_pool` (required except
for `default`, which uses `192.168.100.0/24`) and `mode` (defaults to
`core.upf.mode`). `default` is the built-in UPF deployed with the core and
always exists. Every other instance is deployed by `make 5gc-upf-install` as
its own `bess-upf` release in namespace `aether-upf-<name>`, together with a
unit (`aether-upf-<name>-routes.service`) carrying its UE pool route and NAT.
`make aether-add-upfs` first runs `5gc-router-install`, which builds any
network the new instance needs; `make aether-remove-upfs` removes the
configured additional releases and their units. To drop an instance for good,
run it before removing the entry from `core.upf.instances`, then run
`aether-5gc-install` so networks no longer used are taken down. A second UPF on its own networks:

```yaml
core:
  networks:
    n3b: { iface: eno3, subnet: 10.70.0.0/24 }
    n6b: { iface: eno4, subnet: 10.80.0.0/24, gateway: 10.80.0.1 }
  upf:
    instances:
      edge-2:
        access: { network: n3b, ip: 10.70.0.5 }
        core:   { network: n6b, ip: 10.80.0.5 }
        ue_ip_pool: 172.248.0.0/16
```

The install refuses configurations that cannot work rather than deploying
them: a gateway outside its subnet, `host-device` with the host as gateway,
moving the interface that carries the host's default route (or anything
beneath it) into a pod, a network used by both a `dpdk` and an `af_packet`
UPF, two UPFs sharing an address, overlapping UE pools, and unknown keys. In
`dpdk` mode both sides must be on one interface and `attach` does not apply.
