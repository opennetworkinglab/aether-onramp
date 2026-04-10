#### Variables ####

export ROOT_DIR ?= $(PWD)
export UERANSIM_ROOT_DIR ?= $(ROOT_DIR)

export ANSIBLE_NAME ?= ansible-ueransim
export HOSTS_INI_FILE ?= hosts.ini

export EXTRA_VARS ?= ""

#### Start Ansible ####
ueransim-ansible:
	export ANSIBLE_NAME=$(ANSIBLE_NAME); \
	sh $(UERANSIM_ROOT_DIR)/scripts/ansible ssh-agent bash

#### a. Debugging ####
ueransim-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/pingall.yml \
		--extra-vars $(EXTRA_VARS)

#### b. Provision ueransim ####
ueransim-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/simulator.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)"  --extra-vars $(EXTRA_VARS) -v

#### c. Start the simulator
ueransim-run:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/simulator.yml --tags start  \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)"  --extra-vars $(EXTRA_VARS)

#### d. Stop the simulator
ueransim-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/simulator.yml --tags stop  \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)"  --extra-vars $(EXTRA_VARS)

#### e. Remove ueransim ####
ueransim-uninstall: ueransim-stop
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/simulator.yml --tags uninstall  \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)"   --extra-vars $(EXTRA_VARS)
