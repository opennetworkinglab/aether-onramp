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
amp-install: amp-roc-install amp-roc-load amp-monitor-install amp-monitor-load
amp-uninstall: amp-monitor-uninstall amp-roc-uninstall

#### c. Provision ROC ####
amp-roc-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/roc.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
amp-roc-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/roc.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

### c.1 Load ROC Models ###
amp-roc-load:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/roc-load.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### d. Provision Monitoring ####
amp-monitor-install:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/monitor.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
amp-monitor-uninstall:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/monitor.yml --tags uninstall \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)

#### d.1 Load Monitoring Dashboards ####
amp-monitor-load:
	ansible-playbook -i $(HOSTS_INI_FILE) $(AMP_ROOT_DIR)/monitor-load.yml --tags install \
		--extra-vars "ROOT_DIR=$(ROOT_DIR)" --extra-vars $(EXTRA_VARS)
