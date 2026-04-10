#### Variables ####

export ROOT_DIR ?= $(PWD)
export 4GC_ROOT_DIR ?= $(ROOT_DIR)

export HOSTS_INI_FILE ?= $(4GC_ROOT_DIR)/hosts.ini

# export EXTRA_VARS ?= "@$(4GC_ROOT_DIR)/vars/main.yml"

#### a. Debugging ####

4gc-debug:
	ansible-playbook -i $(HOSTS_INI_FILE) $(4GC_ROOT_DIR)/debug.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

4gc-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(4GC_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### b. Provision k8s ####
4gc-install: 4gc-router-install 4gc-core-install
4gc-uninstall: 4gc-core-uninstall 4gc-router-uninstall

#### c. Provision router ####
4gc-router-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(4GC_ROOT_DIR)/router.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
4gc-router-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(4GC_ROOT_DIR)/router.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### d. Provision core ####
4gc-core-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(4GC_ROOT_DIR)/core.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
4gc-core-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(4GC_ROOT_DIR)/core.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
