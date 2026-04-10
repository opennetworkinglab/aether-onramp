## K8:

The K8 repository builds a multi-node K8 cluster using rke2 and installs Helm.
To set up the K8 repository, you need to provide the following:

1. Node configurations with IP addresses in the hosts.ini file.
   - You can specify both master and worker nodes.

2. rke2 configuration parameters, such as the rke2 version, in the vars/main.yml file.
3. Rke2 cluster parameters file and path set in /vars/main.yml
4. run `make k8s-install`

The repository will build a multi-node cluster. To check the cluster, run the
following command:
```kubectl get nodes```
