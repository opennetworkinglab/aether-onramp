#### Variables ####

export ROOT_DIR ?= $(PWD)
export AETHER_ROOT_DIR ?= $(ROOT_DIR)

export SDRAN_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/sdran
export 5GC_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/5gc
export 4GC_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/4gc
export AMP_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/amp
export GNBSIM_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/gnbsim
export UERANSIM_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/ueransim
export K8S_ROOT_DIR ?= $(AETHER_ROOT_DIR)/deps/k8s

export ANSIBLE_NAME ?= ansible-aether
export ANSIBLE_CONFIG ?= $(AETHER_ROOT_DIR)/ansible.cfg
export HOSTS_INI_FILE ?= $(AETHER_ROOT_DIR)/hosts.ini

export EXTRA_VARS ?= "@$(AETHER_ROOT_DIR)/vars/main.yml"


#### Start Ansible docker (no longer supported) ####

ansible:
	export ANSIBLE_NAME=$(ANSIBLE_NAME); \
	sh $(AETHER_ROOT_DIR)/scripts/ansible ssh-agent bash

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

#### Shortcut for QuickStart Only ####
aether-install: k8s-install 5gc-install gnbsim-install amp-install
aether-uninstall: monitor-uninstall roc-uninstall gnbsim-uninstall 5gc-uninstall k8s-uninstall

#### Provision AETHER for 4G ####
#### 4G/5G share router role ####
aether-4gc-install: 4gc-core-install 5gc-router-install
aether-4gc-uninstall: 4gc-core-uninstall 5gc-router-uninstall

#### Other Useful Targets ####
aether-resetcore: 5gc-core-uninstall 5gc-core-install
aether-reset4gcore: 4gc-core-uninstall 4gc-core-install
aether-gnbsim-run: gnbsim-simulator-run
aether-add-upfs: 5gc-upf-install
aether-remove-upfs: 5gc-upf-uninstall
aether-ueransim-run: ueransim-run

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
include $(5GC_ROOT_DIR)/Makefile
include $(4GC_ROOT_DIR)/Makefile
include $(AMP_ROOT_DIR)/Makefile
include $(SDRAN_ROOT_DIR)/Makefile
include $(UERANSIM_ROOT_DIR)/Makefile
