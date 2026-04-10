# 4gc

The 4gc repository builds a standalone Aether core with a physical RAN setup.
It depends a k8 cluster which can be deployed using k8 repository that can help to create a multi-node cluster.

To set up the 4gc repository, you need to provide the following:

1. Node configurations with IP addresses in the host.ini file.
   - You can specify both master and worker nodes.
2. Aether configuration parameters, such as RAN_Interface, in the ./var/main.yaml file.

To download the 4gc repository, use the following command:
```
git clone https://gitlab.com/onf-internship/4gc.git
git clone https://gitlab.com/onf-internship/k8s.git
```
### Step-by-Step Installation
To install the 4g-core, follow these steps:
1. Set the configuration variables in the vars/main.yaml file.
   - Set the "standalone" parameter to deploy the core independently from roc.
   - Specify the "data_iface" parameter as the network interface name of the machine.
   - Set the "values_file" parameter:
     - Use "sdcore-4g-values.yaml"
   - The "custom_ran_subnet" parameter, if left empty, core will use the subnet of "data_iface" for UPF.
2. Add the hosts to the init file.
3. Run `make ansible`.
4. In the running Ansible docker terminal:
   - Make sure you have dployed a k8 cluster using `k8s-install` from k8s repo.
   - run `make 4gc-install`
   - It creates networking interfaces for UPF, such as access/core, using `4gc-router-install`.
   - Finally, it installs the 5g core using the values specified in `4gc-core-install`.
     - The installation process may take up to 3 minutes.

#### One-Step Installation
To install 4gc in one go, run `make 4gc-install`.
#### Uninstall
   - run `make 4gc-uninstall`
