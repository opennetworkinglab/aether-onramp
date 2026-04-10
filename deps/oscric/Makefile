#### Variables ####

export ROOT_DIR ?= $(PWD)
export OSCRIC_ROOT_DIR ?= $(ROOT_DIR)

export HOSTS_INI_FILE ?= hosts.ini

export EXTRA_VARS ?= ""

#### a. Debugging ####
oscric-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OSCRIC_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### b. Provision docker ####
oscric-docker-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OSCRIC_ROOT_DIR)/docker.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

oscric-ric-deploy:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OSCRIC_ROOT_DIR)/ric.yml --tags deploy \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
oscric-ric-remove:
	ansible-playbook -i $(HOSTS_INI_FILE) $(OSCRIC_ROOT_DIR)/ric.yml --tags remove \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

oscric-ric-install: oscric-docker-install oscric-ric-deploy
oscric-ric-uninstall: oscric-ric-remove
