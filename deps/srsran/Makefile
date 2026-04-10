#### Variables ####

export ROOT_DIR ?= $(PWD)
export SRSRAN_ROOT_DIR ?= $(ROOT_DIR)

export HOSTS_INI_FILE ?= hosts.ini

export EXTRA_VARS ?= ""

#### a. Debugging ####
srsran-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SRSRAN_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### b. Provision docker ####
srsran-docker-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SRSRAN_ROOT_DIR)/docker.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

srsran-router-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SRSRAN_ROOT_DIR)/router.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
srsran-router-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SRSRAN_ROOT_DIR)/router.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

srsran-gnb-start:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SRSRAN_ROOT_DIR)/gNB.yml --tags start \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
srsran-gnb-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SRSRAN_ROOT_DIR)/gNB.yml --tags stop \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

srsran-uesim-start:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SRSRAN_ROOT_DIR)/uEsimulator.yml --tags start \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
srsran-uesim-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SRSRAN_ROOT_DIR)/uEsimulator.yml --tags stop \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

srsran-gnb-install: srsran-docker-install srsran-router-install srsran-gnb-start
srsran-gnb-uninstall:  srsran-gnb-stop srsran-router-uninstall
