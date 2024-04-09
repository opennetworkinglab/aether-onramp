# OnRamp Variables

File `main.yml` specifies global variables used to configure how Aether is deployed.
By default, it is configured for the Quick Start deployment. The other files define
common configurations (also called blueprints), any one of which you can copy to
`main.yml`, and then edit to account for your local details. The current set of
blueprints include:

* `main-quickstart.yml`: Configures the RAN emulator (gNBsim) to run in the same
   server as the Core. Equivalent to `main.yml` by default. Details documented
   [here](https://docs.aetherproject.org/master/onramp/start.html).

* `main-gnbsim.yml`: Configures the RAN emulator (gNBsim) to run in one or more
   servers, independent of the Core. Details documented
   [here](https://docs.aetherproject.org/master/onramp/gnbsim.html).

* `main-gNB.yml`: Configures the Core to work with an external 5G radio (gNB), with
   the Core running independent of AMP. (Change variable `standalone` to false to have
   the Core running under AMP's control.) Details documented
   [here](https://docs.aetherproject.org/master/onramp/gnb.html).

* `main-eNB.yml`: Configures the Core to work with an external 4G radio (eNB), with
   the Core running independent of AMP. (Change variable `standalone` to false to have
   the Core running under AMP's control.) Details documented
   [here](https://docs.aetherproject.org/master/onramp/gnb.html#support-for-enbs).

* `main-upf.yml`: Configures the Core with two UPFs and programs AMP
   with two slices, each associated with a distinct UPF. Depends on variable
   `standalone` being set to false so the Core runs under AMP's control.
   Details documented
   [here](https://docs.aetherproject.org/master/onramp/blueprints.html#multiple-upfs).

* `main-sdran.yml`: Configures the Core and SD-RAN in tandem, with
  RANSIM (running in the same Kubernetes namespace as SD-RAN)
  emulating various RAN elements. Details documented
  [here](https://docs.aetherproject.org/master/onramp/blueprints.html#sd-ran).

* `main-ueransim.yml`: Configures UERANSIM in place of gNBsim,
  providing a second way to direct workload at the Core. Details documented
  [here](https://docs.aetherproject.org/master/onramp/blueprints.html#ueransim).
