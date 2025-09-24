#### Variables ####

export ROOT_DIR ?= $(PWD)
export AETHER_ROOT_DIR ?= $(ROOT_DIR)

export SDRAN_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/sdran
export 5GC_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/5gc
export 4GC_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/4gc
export AMP_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/amp
export GNBSIM_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/gnbsim
export OAI_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/oai
export OSCRIC_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/oscric
export SRSRAN_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/srsran
export UERANSIM_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/ueransim
export N3IWF_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/n3iwf
export K8S_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/k8s

export ANSIBLE_NAME ?= ansible-aether
export ANSIBLE_CONFIG ?= $(AETHER_ROOT_DIR)/ansible.cfg
export HOSTS_INI_FILE ?= $(AETHER_ROOT_DIR)/hosts.ini

export EXTRA_VARS ?= "@$(AETHER_ROOT_DIR)/vars/main.yml"


#### Validate Ansible Configuration ####
aether-pingall:
	echo $(AETHER_ROOT_DIR)
	ansible-playbook -i $(HOSTS_INI_FILE) $(AETHER_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### Provision AETHER Components for 5G ####
aether-k8s-install: k8s-install
aether-k8s-uninstall: k8s-uninstall
aether-5gc-install: 5gc-install
aether-5gc-uninstall: 5gc-uninstall
aether-gnbsim-install: gnbsim-install
aether-gnbsim-uninstall: gnbsim-uninstall
aether-amp-install: amp-install
aether-amp-uninstall: amp-uninstall
aether-sdran-install: sdran-install
aether-sdran-uninstall: sdran-uninstall
aether-ueransim-install: ueransim-install
aether-ueransim-uninstall: ueransim-uninstall
aether-oai-gnb-install: oai-gnb-install
aether-oai-gnb-uninstall: oai-gnb-uninstall
aether-oai-uesim-start: oai-uesim-start
aether-oai-uesim-stop: oai-uesim-stop
aether-srsran-gnb-install: srsran-gnb-install
aether-srsran-gnb-uninstall: srsran-gnb-uninstall
aether-srsran-uesim-start: srsran-uesim-start
aether-srsran-uesim-stop: srsran-uesim-stop
aether-oscric-ric-install: oscric-ric-install
aether-oscric-ric-uninstall: oscric-ric-uninstall
aether-n3iwf-install: n3iwf-install
aether-n3iwf-uninstall: n3iwf-uninstall

#### Shortcut for QuickStart Only ####
aether-install: k8s-install 5gc-install gnbsim-install amp-install
aether-uninstall: monitor-uninstall roc-uninstall gnbsim-uninstall 5gc-uninstall k8s-uninstall

#### Provision AETHER for 4G ####
#### 4G/5G share router role ####
aether-4gc-install: 4gc-core-install 5gc-router-install
aether-4gc-uninstall: 4gc-core-uninstall 5gc-router-uninstall

#### Other Useful Targets ####
aether-5gc-reset: 5gc-core-reset
aether-4gc-reset: 4gc-core-uninstall 4gc-core-install
aether-gnbsim-run: gnbsim-simulator-run
aether-add-upfs: 5gc-upf-install
aether-remove-upfs: 5gc-upf-uninstall
aether-ueransim-run: ueransim-run
aether-ueransim-stop: ueransim-stop

# Rules:
#	amp-install: roc-install roc-load monitor-install monitor-load
#	amp-uninstall: monitor-uninstall roc-uninstall

#	5gc-install: 5gc-router-install 5gc-core-install
#	5gc-uninstall: 5gc-core-uninstall 5gc-router-uninstall

## run gnbsim-docker-install before running setup
#	gnbsim-install: gnbsim-docker-router-install gnbsim-docker-start
#	gnbsim-uninstall:  gnbsim-docker-stop gnbsim-docker-router-uninstall


###  Provision k8s ####
#	k8s-install
#	k8s-uninstall

### Provision router ####
#	5gc-router-install
#	5gc-router-uninstall

### Provision core ####
#	5gc-core-install
#	5gc-core-uninstall
#	5gc-core-reset

### Provision  AMP ####
# amp-install: k8s-install roc-install roc-load monitor-install monitor-load
# amp-uninstall: monitor-uninstall roc-uninstall k8s-uninstall

### Provision and load ROC ###
# roc-install
# roc-load
# roc-uninstall

### Provision and load Monitoring ###
# monitor-install
# monitor-load
# monitor-uninstall

### Provision and run gnbsim ###
# 	gnbsim-docker-install
# 	gnbsim-docker-uninstall

# 	gnbsim-docker-router-install
# 	gnbsim-docker-router-uninstall

# 	gnbsim-docker-start
# 	gnbsim-docker-stop

# 	gnbsim-simulator-start

### Provision and run ueransim     ###
# 	ueransim-install
# 	ueransim-run
# 	ueransim-uninstall


#include at the end so rules are not overwritten
include $(K8S_ROOT_DIR)/Makefile
include $(GNBSIM_ROOT_DIR)/Makefile
include $(OAI_ROOT_DIR)/Makefile
include $(SRSRAN_ROOT_DIR)/Makefile
include $(5GC_ROOT_DIR)/Makefile
include $(4GC_ROOT_DIR)/Makefile
include $(AMP_ROOT_DIR)/Makefile
include $(SDRAN_ROOT_DIR)/Makefile
include $(UERANSIM_ROOT_DIR)/Makefile
include $(OSCRIC_ROOT_DIR)/Makefile
include $(N3IWF_ROOT_DIR)/Makefile
