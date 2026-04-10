# srsRAN gNB

The `aether-srsran` repository allows srsRAN (both physical and simulated) to work with the Aether SD-Core using Docker.
It has been tested in simulation mode and with USRP X310 as the RAN hardware.

To download the 'aether-srsran' repository, use the following command:
```
git clone https://github.com/opennetworkinglab/aether-srsran.git
```

## Step-by-Step Installation
To install srsRAN-gNB, follow these steps:

1. Install Docker by running `make srsran-docker-install`.
   Note: If docker already installed then ignore this step
2. Configure the network for srsRAN-gNB:
   - Set "network.name" to the name of the Docker network to be created.
   - run `make srsran-router-install` to create the network.
   - To remove the network, run `make srsran-router-uninstall`.
3. Start the srsRAN-gNB Docker containers:
   - Set the container image "gnb_image" for gNB.
   - Set "simulation" to true to run in simulation mode.
   - Set "gnb_conf" path for corresponding gNB config file.
   - Set "gnb_ip" for gNB host/container connectivity.
   - Set "core.amf.ip" with IP address of Aether core.
   - Start docker container using `make srsran-gnb-install`.
      - To stop the gNB, run `make srsran-gnb-stop`.
4. Start the UE simulation:
   - Set the container image "ue_image" for UeSimulation.
   - Set "network" same as the network name used for gNB.
   - Set "gnb_ip" with the IP address of the gNB host/container.
   - Set "simulation" to true to run in simulation mode.
   - Set "ue_conf" path for corresponding UE simulation config file.
   - Run `make srsran-uesim-start`.
      - To stop the UE simulation, run `make srsran-uesim-stop`.
5. Run additional tests (ping):
   - Enter the UE Docker container using `docker exec -it rfsim5g-srsran-nr-ue bash`.
   - Use `ip netns exec ue1 ping -c 5 192.168.250.1` to view the success result.

### One-Step Installation
To install srsRAN gNB in one go, run `make srsran-gnb-install`.

### Uninstall
To uninstall srsRAN gNB, run `make srsran-gnb-uninstall`.
