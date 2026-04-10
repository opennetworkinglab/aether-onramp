#### Variables ####

export OCUDU_ROOT_DIR ?= $(PWD)

export HOSTS_INI_FILE ?= hosts.ini

export EXTRA_VARS ?= ""

#### a. Debugging ####
ocudu-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OCUDU_ROOT_DIR)/pingall.yml \
		--extra-vars $(EXTRA_VARS)

#### b. Provision docker ####
ocudu-docker-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OCUDU_ROOT_DIR)/docker.yml --tags install \
		--extra-vars $(EXTRA_VARS)

ocudu-router-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OCUDU_ROOT_DIR)/router.yml --tags install \
		--extra-vars $(EXTRA_VARS)
ocudu-router-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OCUDU_ROOT_DIR)/router.yml --tags uninstall \
		--extra-vars $(EXTRA_VARS)

ocudu-gnb-start:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OCUDU_ROOT_DIR)/gNB.yml --tags start \
		--extra-vars $(EXTRA_VARS)
ocudu-gnb-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OCUDU_ROOT_DIR)/gNB.yml --tags stop \
		--extra-vars $(EXTRA_VARS)

ocudu-uesim-start:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OCUDU_ROOT_DIR)/uEsimulator.yml --tags start \
		--extra-vars $(EXTRA_VARS)
ocudu-uesim-stop:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OCUDU_ROOT_DIR)/uEsimulator.yml --tags stop \
		--extra-vars $(EXTRA_VARS)

ocudu-gnb-install: ocudu-docker-install ocudu-router-install ocudu-gnb-start
ocudu-gnb-uninstall:  ocudu-gnb-stop ocudu-router-uninstall
