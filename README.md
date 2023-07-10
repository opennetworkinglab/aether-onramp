# aetherOnRamp

run `make ansible`

## to Make it multiNode to single Node
1. Destroy cluster using `make platform-uninstall`
2. update host.ini file 
3. Deploy cluster using `5gc-install` 
    a. After 5gc-install check if all pods are running
    b. if not then reset the core using `make resetcore`
4. Setup gNbSim
    a. check amf ip address is set to core ip adddes 
    b. run `gnbsim-simulator-setup-install`
### Run Experiment
1. make sure cluster in up
2. make sure gnbpods are up on gnb VMs .. i.e `make gnbsim-simulator-setup-install` 
    a. change in number of pods in var/main.yaml file
3. run `pytyhon3 


### To setup Gnbsim on same machine as Core
 set SameMachineAsCore = true
 make sure gnbsim.subnet_prefix has same prefix value core.custome_ran_subnet

