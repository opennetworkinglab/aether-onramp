#### Variables ####

export ROOT_DIR ?= $(PWD)
export UERANSIM_ROOT_DIR ?= $(ROOT_DIR)

export ANSIBLE_NAME ?= ansible-ueransim
export HOSTS_INI_FILE ?= hosts.ini

export EXTRA_VARS ?= ""

#### Start Ansible docker ####

ueransim-ansible:
	export ANSIBLE_NAME=$(ANSIBLE_NAME); \
	sh $(UERANSIM_ROOT_DIR)/scripts/ansible ssh-agent bash

#### a. Debugging ####
ueransim-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### b. Provision docker ####
ueransim-docker-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/docker.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
ueransim-docker-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/docker.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

ueransim-docker-router-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/router.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
ueransim-docker-router-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/router.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

ueransim-docker-start:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/docker.yml --tags start \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
ueransim-docker-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/docker.yml --tags stop \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### c. Provision ueransim ####
ueransim-simulator-run:
	ansible-playbook -i $(HOSTS_INI_FILE) $(UERANSIM_ROOT_DIR)/simulator.yml --tags start \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)


# run ueransim-docker-install before running setup
ueransim-install: ueransim-docker-install ueransim-docker-router-install ueransim-docker-start
ueransim-uninstall:  ueransim-docker-stop ueransim-docker-router-uninstall ueransim-docker-uninstall
