#### Variables ####

export ROOT_DIR ?= $(PWD)
export OAI_ROOT_DIR ?= $(ROOT_DIR)

export HOSTS_INI_FILE ?= hosts.ini

export EXTRA_VARS ?= ""

#### a. Debugging ####
oai-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OAI_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### b. Provision docker ####
oai-docker-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OAI_ROOT_DIR)/docker.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

oai-router-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OAI_ROOT_DIR)/router.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
oai-router-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OAI_ROOT_DIR)/router.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

oai-gnb-start:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OAI_ROOT_DIR)/gNb.yml --tags start \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
oai-gnb-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OAI_ROOT_DIR)/gNb.yml --tags stop \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

oai-uesim-start:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OAI_ROOT_DIR)/uEsimulator.yml --tags start \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
oai-uesim-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OAI_ROOT_DIR)/uEsimulator.yml --tags stop \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

# run oai-docker-install before running setup
oai-gnb-install: oai-docker-install oai-router-install oai-gnb-start
oai-gnb-uninstall:  oai-gnb-stop oai-router-uninstall
