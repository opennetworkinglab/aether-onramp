export ROOT_DIR ?= $(PWD)
export SDRAN_ROOT_DIR ?= $(ROOT_DIR)
export HOSTS_INI_FILE ?= $(SDRAN_ROOT_DIR)/hosts.ini

export EXTRA_VARS ?= "@$(SDRAN_ROOT_DIR)/vars/default.yml"


# Provision sdran

sdran-install: sdran-platform-install sdran-suite-install

sdran-platform-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SDRAN_ROOT_DIR)/platform.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

sdran-suite-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SDRAN_ROOT_DIR)/sdran.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

# Uninstall sdran

sdran-uninstall: sdran-suite-uninstall sdran-platform-uninstall

sdran-platform-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SDRAN_ROOT_DIR)/platform.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

sdran-suite-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(SDRAN_ROOT_DIR)/sdran.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
