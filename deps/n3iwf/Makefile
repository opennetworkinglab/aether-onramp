#### Variables ####

export ROOT_DIR ?= $(PWD)
export N3IWF_ROOT_DIR ?= $(ROOT_DIR)

export HOSTS_INI_FILE ?= hosts.ini

export EXTRA_VARS ?= ""

#### a. Debugging ####
n3iwf-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(N3IWF_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### b. Provision docker ####
n3iwf-docker-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(N3IWF_ROOT_DIR)/docker.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### c. Provision router ####
n3iwf-router-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(N3IWF_ROOT_DIR)/router.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
n3iwf-router-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(N3IWF_ROOT_DIR)/router.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### d. Provision n3iwf ####
n3iwf-start:
	ansible-playbook -i $(HOSTS_INI_FILE) $(N3IWF_ROOT_DIR)/n3iwf.yml --tags start \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
n3iwf-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(N3IWF_ROOT_DIR)/n3iwf.yml --tags stop \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

n3iwf-install: n3iwf-docker-install n3iwf-router-install n3iwf-start
n3iwf-uninstall:  n3iwf-stop n3iwf-router-uninstall
