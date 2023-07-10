#### Variables ####

export ROOT_DIR ?= $(PWD)
export PLATFORM_ROOT_DIR ?= $(ROOT_DIR)

export 5GC_ROOT_DIR ?= $(PLATFORM_ROOT_DIR)/deps/5gc
export GNBSIM_ROOT_DIR ?= $(PLATFORM_ROOT_DIR)/deps/gnbsim
export K8S_ROOT_DIR ?= $(5GC_ROOT_DIR)/deps/k8s

export ANSIBLE_NAME ?= ansible-platform0
export ANSIBLE_CONFIG ?= $(PLATFORM_ROOT_DIR)/ansible.cfg
export HOSTS_INI_FILE ?= $(PLATFORM_ROOT_DIR)/hosts.ini

export EXTRA_VARS ?= "@$(PLATFORM_ROOT_DIR)/vars/main.yml"


#### Start Ansible docker ####

ansible:
	export ANSIBLE_NAME=$(ANSIBLE_NAME); \
	sh $(PLATFORM_ROOT_DIR)/scripts/ansible ssh-agent bash

#### a. Debugging ####
platform-debug:
	ansible-playbook -i $(HOSTS_INI_FILE) $(PLATFORM_ROOT_DIR)/debug.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

platform-pingall:
	echo $(PLATFORM_ROOT_DIR)
	ansible-playbook -i $(HOSTS_INI_FILE) $(PLATFORM_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

### NOTE
# run gnbsim-docker-install before running setup
# if first time core gets stuck on 1 pod init state with no reason, use 5gc-core-uninstall and 5gc-core-install

#### b. Provision platform ####

platform-install:
	$(MAKE) 5gc-install;
	$(MAKE) gnbsim-simulator-setup-install

platform-uninstall: gnbsim-simulator-setup-uninstall 5gc-uninstall

resetcore: 
	$(MAKE) 5gc-core-uninstall;
	sleep 5.0;
	$(MAKE) 5gc-core-install;
# sleep 180.0;
# Rules:

#	5gc-install: k8s-install 5gc-router-install 5gc-core-install
#	5gc-uninstall: 5gc-core-uninstall 5gc-router-uninstall k8s-uninstall

# 		run gnbsim-docker-install before running setup
# 	gnbsim-simulator-setup-install: gnbsim-docker-router-install gnbsim-docker-start 
# 	gnbsim-simulator-setup-uninstall:  gnbsim-docker-stop gnbsim-docker-router-uninstall

#	#### b. Provision k8s ####
#	k8s-install
#	k8s-uninstall

#### c. Provision router ####
#	5gc-router-install: 
#	5gc-router-uninstall:

#### d. Provision core ####
#	5gc-core-install: 
#	5gc-core-uninstall:

# #### c. Provision docker ####
# 	gnbsim-docker-install:
# 	gnbsim-docker-uninstall:

# 	gnbsim-docker-router-install:
# 	gnbsim-docker-router-uninstall:

# 	gnbsim-docker-start:
# 	gnbsim-docker-stop:

# #### d. Provision gnbsim ####
# 	gnbsim-simulator-start:


#include at the end so rules are not overwritten
#### Provisioning k8s ####
include $(K8S_ROOT_DIR)/Makefile
include $(GNBSIM_ROOT_DIR)/Makefile
include $(5GC_ROOT_DIR)/Makefile
