# OAI gNB

The `aether-oai` repository allows OAI RAN (both physical and simulated) to work with the Aether SD-Core using Docker.
It has been tested in simulation mode and with USRP X310 as the RAN hardware.

To download the 'aether-oai' repository, use the following command:
```
git clone https://github.com/opennetworkinglab/aether-oai.git
```

## Step-by-Step Installation
To install oai-gNB, follow these steps:

1. Install Docker by running `make oai-docker-install`.
2. Configure the network for oai-gNB:
   - Set the "data_iface" parameter to the network interface name of the machine.
   - Set "network.name" to the name of the Docker network to be created.
   - Set "network.bridge.name" to the name of the interface to be created.
   - Set "subnet", which should correspond to the "ran_subnet" of 5GC (SD-Core) or the machine's subnet.
   - run `make oai-router-install` to create the network.
      - To remove the network, run `make oai-router-uninstall`.
3. Start the OAI-gNB Docker containers:
   - Set the container image "gnb_image" for gNB.
   - Set "simulation" to true to run in simulation mode.
   - Set "gnb_conf" path for corresponding conf file for gNB i.e., for simulation.
   - Set "gnb_ip" for gNB container, it should in same subnet as network.
   - Set "core.amf.ip" with IP address of Aether core.
   - Start docker container using `make oai-gnb-install`.
      - To stop the gNB, run `make oai-gnb-stop`.
4. Start the UE simulation:
   - Set the container image "ue_image" for UeSimulation.
   - Set "network" same as the network name used for gNB.
   - Set "gnb_ip" with the IP address of the gNB container.
   - Set "simulation" to true to run in simulation mode.
   - Set "ue_conf" path for corresponding conf file for UeSimulation.
   - Run `make oai-uesim-start`.
      - To stop the UE simulation, run `make oai-uesim-stop`.
5. Check the results:
   - Enter the UE Docker container using `docker exec -it rfsim5g-oai-nr-ue bash`.
   - Use `ping -I oaitun_ue1 google.com -c 2` to view the success result.

### One-Step Installation
To install OAI gNB in one go, run `make oai-gnb-install`.

### Uninstall
To uninstall OAI gNB, run `make oai-gnb-uninstall`.
