# AMP

## Aether Management Platform

The amp repository builds the Aether Management Platform with Aether-ROC and Monitoring. It relies on a k8s cluster that can be created from the k8s repository.

To download the AMP repository, use the following command:
```
git clone https://github.com/omec-project/aether-amp.git
```
### Step-by-Step Installation
To install AMP, follow these steps:
1. Install a k8s cluster
   - Provision a Kubernetes cluster before installing AMP. Use the companion k8s repository or another supported cluster provisioning workflow.
2. Install ROC
   - Specify Helm chart settings for `atomix`, `onosproject`, and `aether_roc`.
   - Run `make amp-roc-install`.
3. Install Monitoring
   - Specify Helm chart settings for `monitor` and `monitor_crd`.
   - Run `make amp-monitor-install`.

#### One-Step Installation
To install AMP in one go, run `make amp-install`.
#### Uninstall
   - Run `make amp-uninstall`.
