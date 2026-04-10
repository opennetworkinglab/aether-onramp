#### Variables ####

export ROOT_DIR ?= $(PWD)
export AMP_ROOT_DIR ?= $(ROOT_DIR)

export ANSIBLE_NAME ?= ansible-amp
export HOSTS_INI_FILE ?= $(AMP_ROOT_DIR)/hosts.ini

export EXTRA_VARS ?= "@$(AMP_ROOT_DIR)/vars/main.yml"

#### a. Debugging ####
amp-debug:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/debug.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

amp-pingall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/pingall.yml \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### b. Provision k8s with AMP ####
# k8s-install
amp-install: roc-install roc-load monitor-install monitor-load
amp-uninstall: monitor-uninstall roc-uninstall

#### c. Provision ROC ####
roc-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/roc.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
roc-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/roc.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

### c.1 Load ROC Models ###
roc-load: # roc-install
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/roc-load.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### d. Provision Monitoring ####
monitor-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/monitor.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
monitor-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/monitor.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### d.1 Load Monitoring Dashboards ####
monitor-load:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/monitor-load.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
