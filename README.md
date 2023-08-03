# Aether OnRamp

Aether OnRamp provides a low-overhead way to bring up a
Kubernetes cluster, deploy a 5G version of SD-Core on that
cluster, and then connect that Core to either an emulated 5G RAN
or a network of physical gNBs. (OnRamp also supports a 4G
configuration that connects physical eNBs.)

To download Aether OnRamp (and all the submodules it depends on),
type:

```
$ git clone --recursive https://github.com/opennetworkinglab/aether-onramp.git
```

Taking a quick look at your ``aether-onramp`` directory, you will 
find the following.

1. The ``deps`` directory contains Ansible deployment
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
    
Aether OnRamp assumes Ansible is installed. Once you edit
``hosts.ini`` to match your local details, type the following
to verify the setup:

```
$ make aether-pingall
```

## Quick Start

Edit ``vars/main.yml`` to reflect your local scenario. For
the Quick Start deployment, this means setting variable
``data_iface`` to your server's network interface. Note there are
**two** lines that define this variable, one in the ``core`` section
and one in the ``gnbsim`` section.

You are now ready to install a one-node Kubernetes cluster. Type:

```
$ make aether-k8s-install
```

Once Kubernetes is running (which you can verify with ``kubectl``),
you are ready to intall the 5G version of SD-Core. Type:

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
trafffic for the monitoring system to display.

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
the Aether Guide for details:

https://docs.aetherproject.org/master/

You might also check the
[README](https://github.com/opennetworkinglab/aether-onramp/blob/master/vars/README.md).
 in the ``vars`` directory of this
repo, which explains how each of the variants of ``vars/main.yml``
in that directory serves as a general blueprint for the
different configurations of Aether that OnRamp currently supports.

