# OCUDU

OCUDU provisions and runs the OCUDU gNB and the optional srsRAN UE simulator
against Aether SD-Core using Ansible and Docker. The repository includes
playbooks for Docker bootstrap, routing changes required on OCUDU nodes, gNB
lifecycle management, and UE simulation.

## Clone

```bash
git clone https://github.com/opennetworkinglab/aether-ocudu.git
cd aether-ocudu
```

## Repository Layout

- `Makefile`: convenience targets for the Ansible playbooks
- `hosts.ini`: inventory for OCUDU and core hosts
- `vars/main.yml`: default runtime variables used by the playbooks
- `docker.yml`: installs Docker on hosts in the `ocudu_nodes` group
- `router.yml`: applies or removes routing and sysctl changes on OCUDU nodes
- `dpdk.yml`: prepares DPDK prerequisites on OCUDU nodes when `ocudu.servers[n].dpdk.enabled` is true for that node
- `gNB.yml`: starts and stops the OCUDU gNB container
- `uEsimulator.yml`: starts and stops the UE simulator container

## Prerequisites

- Ansible installed on the control machine
- Reachability from the control machine to every host in `hosts.ini`
- Docker-capable Ubuntu hosts for the `ocudu_nodes` group
- A reachable Aether SD-Core AMF address
- For simulated UE runs, valid UPF-related values for `core.upf.default_upf.ue_ip_pool` and `core.upf.core_subnet`

The playbooks use `community.docker` and `ansible.posix` modules. Make sure
those collections are available in the Ansible environment used to run the
targets.

The checked-in `ansible.cfg` keeps SSH host key checking enabled and does not
enable agent forwarding. If you are bringing up disposable lab machines and
need the previous relaxed behavior, provide those SSH options through a local
Ansible config override instead of committing them in-repo.

## Inventory

Update `hosts.ini` to match your deployment.

- `ocudu_nodes`: machines that run Docker, the gNB container, and the optional UE simulator
- `master_nodes`: core-side nodes used to avoid adding the OCUDU static route on the core host itself

The number of entries under `ocudu.servers` in `vars/main.yml` must match the
number of hosts in `ocudu_nodes`. The playbooks fail early if those counts differ.

## Configuration

Most deployment settings live in `vars/main.yml`.

Example defaults:

```yaml
ocudu:
   docker:
      container:
         gnb_image: aetherproject/ocudu:rel-0.8.2
         ue_image: aetherproject/srsran-ue:rel-0.8.2
      network:
         name: host
   simulation: true
   servers:
      0:
         gnb_ip: "10.76.28.115"
         gnb_conf: gnb_zmq.yaml
         ue_conf: ue_zmq.conf
         dpdk:
            enabled: false
            hugepages: 2
            pf_iface: "ens6f0"
            vf_bdf: "0000:18:00.1"
            du_mac_addr: "d0:8e:79:f1:d1:39"
            ru_mac_addr: "70:b3:d5:e1:5e:7e"

core:
   upf:
      access_subnet: "192.168.252.1/24"
      multihop_gnb: false
   amf:
      ip: "10.76.28.113"
```

Override `core.amf.ip` to the actual SD-Core AMF address in your environment when
you are not using the checked-in OCUDU blueprint values.

Key variables:

- `ocudu.docker.container.gnb_image`: gNB container image
- `ocudu.docker.container.ue_image`: UE simulator image
- `ocudu.docker.network.name`: Docker network used by the containers. The checked-in defaults use `host`.
- `ocudu.simulation`: must be `true` to run the UE simulator
- `ocudu.servers[n].gnb_ip`: bind address used by the gNB for NGAP traffic
- `ocudu.servers[n].gnb_conf`: gNB template name or path resolvable by Ansible's template lookup for that OCUDU node. The checked-in default uses the role's `templates/` directory.
- `ocudu.servers[n].ue_conf`: UE simulator template name or path resolvable by Ansible's template lookup for that OCUDU node. The checked-in default uses the role's `templates/` directory.
- `ocudu.servers[n].dpdk.enabled`: enables the DPDK prerequisite playbook for that OCUDU node
- `ocudu.servers[n].dpdk.hugepages`: number of 1 GB hugepages allocated on that host before starting a DPDK gNB
- `ocudu.servers[n].dpdk.pf_iface`: fronthaul PF interface used to create VF 0 for that OCUDU node
- `ocudu.servers[n].dpdk.vf_bdf`: optional VF PCI BDF override; when omitted the role discovers VF 0's PCI address from sysfs
- `ocudu.servers[n].dpdk.du_mac_addr`: optional VF MAC override used in the DPDK gNB config; when omitted the role discovers VF 0's current MAC after SR-IOV creation
- `ocudu.servers[n].dpdk.ru_mac_addr`: RU fronthaul MAC address rendered into the DPDK gNB config; defaults to the checked-in Benetel example value
- `core.amf.ip`: AMF address used by the gNB and routing playbooks
- `core.upf.access_subnet`: subnet used to install the OCUDU-side route toward the UPF
- `core.upf.multihop_gnb`: disables the static route task when set to `true`

Additional UE simulator variables are required by `roles/uEsimulator/tasks/start.yml`:

- `core.upf.default_upf.ue_ip_pool`
- `core.upf.core_subnet`

If those values are not defined in `vars/main.yml`, provide them with `EXTRA_VARS` when invoking `make`.

## gNB Templates

The repository includes templates for both simulated and hardware-backed deployments:

- `roles/gNB/templates/gnb_zmq.yaml`: ZMQ-based simulated radio path
- `roles/gNB/templates/gnb_uhd_b210.yaml`: UHD configuration for B210
- `roles/gNB/templates/gnb_uhd_x310.yaml`: UHD configuration for X310
- `roles/gNB/templates/gnb_dpdk_benetel.yaml`: DPDK plus Open Fronthaul configuration for Benetel RU deployments

## Common Commands

All commands are exposed through the `Makefile`.

### Connectivity Check

```bash
make ocudu-pingall
```

### Install Docker on OCUDU Nodes

```bash
make ocudu-docker-install
```

### Apply Routing Changes

```bash
make ocudu-router-install
```

Remove the routing changes:

```bash
make ocudu-router-uninstall
```

### Prepare DPDK Prerequisites

```bash
make ocudu-dpdk-install
```

This target is only effective for OCUDU nodes where `ocudu.servers[n].dpdk.enabled` is `true`.
Run this as a separate step before `make ocudu-gnb-start` or `make ocudu-gnb-install` when DPDK is enabled. The first run may reboot the host to activate the realtime kernel and CPU isolation settings.

Use the quick readiness check when you only need to know whether each OCUDU node can proceed to DPDK gNB startup:

```bash
make ocudu-dpdk-status
```

This reports one status per OCUDU host:

- `dpdk-ready`: DPDK is enabled for that host and `/var/lib/ocudu/dpdk-ready` exists
- `dpdk-not-ready`: DPDK is enabled for that host but the readiness marker is still absent
- `dpdk-not-enabled`: DPDK is not enabled for that host

This is a lightweight gate only. It does not inspect the live systemd, hugepage, VF binding, or NIC/PTP runtime state.

Use the full validation pass when you want to confirm that the DPDK host preparation actually landed correctly on each DPDK-enabled OCUDU node:

```bash
make ocudu-dpdk-verify
```

The verifier checks:

- `/var/lib/ocudu/dpdk-ready`
- `pf-tuning.service`, `ocudu-ptp4l.service`, and `ocudu-phc2sys.service` are enabled and active
- conflicting time synchronization services are disabled
- 1G hugepages are present
- a VF is bound to `vfio-pci`
- the PF interface tuning from `pf-tuning.service` is visible on the live interface

Use this when `ocudu-dpdk-status` says `dpdk-ready` but you still need confidence that the runtime host state is correct, or when you are debugging a DPDK bring-up issue.

The playbook fans out to each DPDK-enabled OCUDU host through role-backed task files under `roles/dpdk/tasks/`, uploads `roles/dpdk/files/verify-dpdk-services.sh` transiently via Ansible, and runs it there with the PF interface derived from `vars/main.yml`.

If you want to run the same checks directly on a single OCUDU host for debugging, use the script locally:

```bash
./roles/dpdk/files/verify-dpdk-services.sh --pf <pf_iface>
```

### Start the gNB

```bash
make ocudu-gnb-start
```

When DPDK is enabled for an OCUDU host, this target now runs the same readiness
gate as `make ocudu-dpdk-status` before continuing. If the host is still
`dpdk-not-ready`, the playbook stops there with a message telling you to run
`make ocudu-dpdk-install` first.

Stop the gNB:

```bash
make ocudu-gnb-stop
```

### Start the UE Simulator

```bash
make ocudu-uesim-start
```

Stop the UE simulator:

```bash
make ocudu-uesim-stop
```

### One-Step gNB Bring-Up

This target installs Docker, applies the router changes, and starts the gNB:

When `ocudu.servers[n].dpdk.enabled` is `true`, run `make ocudu-dpdk-install` first as a separate step. The gNB start path now refuses to continue until that prerequisite has been applied.

```bash
make ocudu-gnb-install
```

Tear it down:

```bash
make ocudu-gnb-uninstall
```

## Passing Overrides

The `Makefile` supports overriding the inventory, root paths, and Ansible variables:

```bash
make ocudu-uesim-start \
   HOSTS_INI_FILE=hosts.ini \
   EXTRA_VARS='{"core":{"upf":{"default_upf":{"ue_ip_pool":"10.250.0.0"},"core_subnet":"192.168.250.1/24"}}}'
```

Relevant environment variables:

- `HOSTS_INI_FILE`: inventory file passed to `ansible-playbook`
- `OCUDU_ROOT_DIR`: location of this repository when called from another workspace
- `EXTRA_VARS`: raw extra vars string forwarded to Ansible

## Runtime Notes

- The gNB container is created as `ocudu-gnb`.
- The UE simulator container is created as `rfsim5g-nr-ue`.
- The gNB start playbook mounts `/dev/hugepages` and `/dev/vfio` and runs the container in privileged mode.
- The router playbook updates ARP and reverse-path filtering sysctls on OCUDU nodes.
- The UE simulator start playbook adds a default route inside `ue1` and runs a ping test after startup.

## Quick Start

For a single-node simulated setup, the minimum flow is:

1. Update `hosts.ini` and `vars/main.yml` for your hosts and AMF address.
2. Ensure `ocudu.servers` contains one entry per OCUDU node.
3. Provide `core.upf.default_upf.ue_ip_pool` and `core.upf.core_subnet` if you plan to run the UE simulator.
4. Run `make ocudu-gnb-install`.
5. Run `make ocudu-uesim-start`.

If you only want the gNB, or if `ocudu.simulation` is `false`, stop after step 4.
In that case, do not run step 5 because the UE simulator playbook aborts when
simulation is disabled.
