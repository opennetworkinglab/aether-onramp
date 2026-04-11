#### Variables ####

export ROOT_DIR ?= $(PWD)
export 5GC_ROOT_DIR ?= $(ROOT_DIR)

export HOSTS_INI_FILE ?= $(5GC_ROOT_DIR)/hosts.ini

export EXTRA_VARS ?= "@$(5GC_ROOT_DIR)/vars/main.yml"

#### a. Debugging ####

5gc-debug:
	ansible-playbook -i $(HOSTS_INI_FILE) $(5GC_ROOT_DIR)/debug.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

5gc-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(5GC_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### b. Provision k8s ####
5gc-install: 5gc-router-install 5gc-core-install
5gc-uninstall: 5gc-core-uninstall 5gc-router-uninstall

#### c. Provision router ####
5gc-router-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(5GC_ROOT_DIR)/router.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
5gc-router-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(5GC_ROOT_DIR)/router.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### d. Provision core ####
5gc-core-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(5GC_ROOT_DIR)/core.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
5gc-core-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(5GC_ROOT_DIR)/core.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
5gc-core-reset: 5gc-core-uninstall 5gc-core-install


#### e. Provision Multiple UPF ###
5gc-upf-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(5GC_ROOT_DIR)/upf.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
5gc-upf-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(5GC_ROOT_DIR)/upf.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
