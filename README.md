# Aether OnRamp

Aether OnRamp provides a low-overhead way to bring up a
Kubernetes cluster, deploy a 5G version of SD-Core on that
cluster, and then connect that Core to either an emulated 5G RAN
or a network of physical gNBs. (OnRamp also supports a 4G
configuration that connects physical eNBs.)

To download Aether OnRamp, type:

```
$ git clone https://github.com/opennetworkinglab/aether-onramp.git
```

Taking a quick look at your ``aether-onramp`` directory, you will
find the following.

1. The ``deps`` directory contains vendored Ansible deployment
   specifications for all the Aether subsystems. Each of these
   subdirectories (e.g., ``deps/5gc``) is self-contained, but
   the Makefile in the main OnRamp directory imports the
   per-subsystem Makefiles, meaning all the steps required
   to install Aether can be (and typically should be) managed from
   this main directory.

2. File ``vars/main.yml`` defines all the Ansible variables you will
   potentially need to modify to specify your deployment scenario.
   This file is the union of all the per-component ``var/main.yml``
   files you find in the corresponding ``deps`` directory. This
    top-level variable file overrides the per-component files, so
   you will not need to modify the latter. The ``vars`` directory
   contains several variants of ``main.yml``, each tailored for a
   different deployment scenario, with the default ``main.yml``
   supporting the Quick Start deployment described below.

3. File ``hosts.ini`` specifies the set of servers (physical or
   virtual) that Ansible targets with various playbooks. The
   default version included with OnRamp is simplified to run
   everything on a single server (the one you've cloned the
   repo onto). Example multi-node inventories are commented out.

Aether OnRamp assumes Ansible is installed. (See the
[Aether Guide](https://docs.aetherproject.org/onramp/start.html#prep-environment)
for instructions on doing this, along with additional guidance if this
is your first attempt to install OnRamp.) Then, once you edit ``hosts.ini`` to
match your local details, type the following to verify the setup:

```
$ make aether-pingall
```

## Quick Start

Edit ``vars/main.yml`` to reflect your local scenario. For
the Quick Start deployment, this means setting variable
``data_iface`` to your server's network interface. Note there are
**two** lines that define this variable, one in the ``core`` section
and one in the ``gnbsim`` section. You also need to set the
IP address of the AMF (in the ``core`` section) to your servers's
IP address.

You are now ready to install a one-node Kubernetes cluster. Type:

```
$ make aether-k8s-install
```

Once Kubernetes is running (which you can verify with ``kubectl``),
you are ready to install the 5G version of SD-Core. Type:

```
$ make aether-5gc-install
```

Once the Core is running (which you can verify by using ``kubectl`` to
check the ``omec`` name space), you are ready to emulate a RAN
workload. Type:

```
$ make aether-gnbsim-install
$ make aether-gnbsim-run
```

The second command can be executed multiple times, where the
results of each run are saved in a file within the Docker container
running the test. You can access that file by typing:

```
$ docker exec -it gnbsim-1 cat summary.log
```

Finally, you can bring up the Aether Management Platform (AMP) to view
dashboards showing different aspects of Aether's runtime behavior. Type:

```
$ make aether-amp-install
```

You can access the dashboards for Aether's Runtime Control system and
Aether's Monitoring system at the following URLs:

```
http://<server_ip>:31194
http://<server_ip>:30950
```

You will probably want to rerun ``make aether-gnbsim-run`` to generate
traffic for the monitoring system to display.

When you are ready to tear down your Quick Start deployment of Aether,
execute the following commands:

```
$ make aether-gnbsim-uninstall
$ make aether-amp-uninstall
$ make aether-5gc-uninstall
$ make aether-k8s-uninstall
```

Or alternatively:

```
$ make aether-uninstall
```

## Beyond Quick Start

Being able to support more complex configurations of Aether is whole
point of OnRamp. See the OnRamp documentation available as part of
the [Aether Guide](https://docs.aetherproject.org) for details.

## Deploying Behind a Proxy

If your servers access the Internet through an HTTP proxy, enable proxy
support in ``vars/main.yml``:

```yaml
proxy:
  enabled: true
  http_proxy: "http://proxy.example.com:3128"
  https_proxy: "http://proxy.example.com:3128"
  no_proxy: "localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,10.42.0.0/16,10.43.0.0/16,.svc,.svc.cluster.local,.cluster.local"
```

When ``proxy.enabled`` is ``true``, OnRamp automatically configures
proxy settings for all deployment steps, including:

* Ansible tasks that download packages and scripts (``apt``, ``pip``,
  ``get_url``, ``git``, ``helm``).
* The Docker daemon on nodes that run Docker-based components
  (gNBsim, OAI, srsRAN, etc.), so that ``docker pull`` works
  through the proxy.
* RKE2's embedded containerd runtime on Kubernetes master and worker
  nodes, so that container image pulls work through the proxy.

Adjust ``no_proxy`` to include any additional internal hosts or
domains that should bypass the proxy. The default value covers
localhost, private RFC 1918 subnets, and Kubernetes internal domains.

You might also check the `vars` directory of this repo, where file
`main.yml` specifies global variables used to configure how Aether is
deployed. By default, it is configured for the Quick Start deployment.
The other files define other common configurations, any one of which
you can copy to `main.yml`, and then edit to account for your local
details. These alternative configurations are identified in the README.

## Deploying Offline / On Local Mirrors (Airgap)

Several roles run `apt: update_cache=yes` to refresh the apt cache
before installing packages (`iptables-persistent` in the 5gc/router
and oai/router roles, `python3-software-properties` in
amp/monitor, the docker-ce stack in srsran/ocudu/oai/n3iwf/gnbsim/
oscric docker roles, build deps in ueransim/simulator). On a host
that can't reach upstream apt archives — airgapped sites, baked
images, internal mirrors that don't need upstream refresh — that
refresh hard-fails and aborts the install.

Set the `airgapped` block in `vars/main.yml` (and in any
`vars/main-<flavor>.yml` you `cp` over `main.yml`) to opt out:

```yaml
airgapped:
  enabled: true                 # skip `apt update_cache` for offline / mirror-only sites
```

When `enabled: true`, every gated `apt: update_cache` call site is
skipped. Operators are responsible for ensuring the required
packages are already installed (offline bundle, baked image, or a
local mirror keeping the apt cache fresh out-of-band) before running
the install. The default (`enabled: false`) preserves online
behaviour — apt cache is refreshed as before.
