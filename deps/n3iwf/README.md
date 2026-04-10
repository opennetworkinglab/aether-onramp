# aether-n3iwf

The `aether-n3iwf` repository allows to deploy the Non-3GPP Interworking
Function (N3IWF) using Docker and work with the Aether SD-Core.

To download the 'aether-n3iwf' repository, use the following command:
```
git clone https://github.com/opennetworkinglab/aether-n3iwf.git
```

## Step-by-Step Installation
To install N3IWF, follow these steps:

1. Install Docker by running `make n3iwf-docker-install`.
   Note: If docker already installed then ignore this step
2. Configure the network for N3IWF:
   - Set "network.name" to the name of the Docker network to be created.
   - run `make n3iwf-router-install` to create the network.
      - To remove the network, run `make n3iwf-router-uninstall`.
3. Start the N3IWF Docker container:
   - Set the container image for N3IWF.
   - Set "conf_file" path for corresponding conf file for N3IWF.
   - Set "n2_ip", "n3_ip", and "n3iwf_ip" addresses for N3IWF container. Note
   that the "n3iwf_ip" is the IP address for the interface that will be used as
   parent interface for the `ipsec` tunnel(s) towards the UE(s)
   - Set "core.amf.ip" with IP address of Aether core.
   - Start docker container using `make n3iwf-start`.
      - To stop the N3IWF, run `make n3iwf-stop`.

### One-Step Installation
To install/deploy N3IWF in a single step, run `make n3iwf-install`.

### Uninstall
To uninstall/remove N3IWF, run `make n3iwf-uninstall`.
