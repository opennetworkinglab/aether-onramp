# ueransim

This blueprint runs UERANSIM in place of gNBsim, providing a second way to direct workload at SD-Core. Of particular note, UERANSIM runs iperf3, making it possible to measure UPF throughput. (In contrast, gNBsim primarily stresses the Core's Control Plane.)

The UERANSIM blueprint includes the following:

Global vars file `vars/main-ueransim.yml` gives the overall blueprint specification.

## Step-by-Step Installation
To install ueransim, follow these steps:
1. Inventory file hosts.ini needs to be modified to identify the server that is to run UERANSIM. Currently, a second server is needed, as UERANSIM and SD-Core cannot be deployed on the same server.
```
[ueransim_nodes]
node2
```
2. Install the UERANSIM container image and host routing
   - Update the config files under `config/` for both UE and gNB.
   - Run `make ueransim-install`.
3. Start the simulation
   - Set "amf.ip" to the IP address of the core machine.
   - Run `make ueransim-run`.

### One-Step Installation
To install ueransim in one go, run `make ueransim-install`.

### Uninstall
To uninstall ueransim, run `make ueransim-uninstall`.
