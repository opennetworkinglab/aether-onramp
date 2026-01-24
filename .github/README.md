# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Aether OnRamp project.

## Quickstart Workflow

The `quickstart.yml` workflow replicates the functionality of the Jenkins groovy workflow found at [opennetworkinglab/aether-jenkins](https://github.com/opennetworkinglab/aether-jenkins/blob/master/quickstart.groovy).

### Workflow Stages

1. **Checkout repository**: Clones the repo with all submodules
1. **Set up Python**: Installs Python and creates a virtual environment with Ansible
1. **Install kubectl**: Uses Azure's setup-kubectl action (default/latest version as specified in requirements)
1. **Install Helm**: Uses Azure's setup-helm action (default/latest version as specified in requirements)
1. **Configure OnRamp**: Sets up SSH keys, generates hosts.ini, configures vars/main.yml
1. **Install Aether**: Installs Kubernetes, 5GC core, and gNBsim
1. **Run gNBsim**: Executes the gNBsim test with retry logic (2 attempts)
1. **Validate Results**: Checks that tests passed using the same validation pattern as Jenkins
1. **Retrieve Logs**: Collects logs from all components
10. **Archive Artifacts**: Uploads logs as workflow artifacts
11. **Cleanup**: Uninstalls all components (always runs, even on failure)
12. **Notify on Failure**: Logs failure information (can be extended with Slack notifications)

### Triggering the Workflow

The workflow can be triggered in three ways:

1. **Manual Dispatch**: Go to Actions → Aether OnRamp Quickstart → Run workflow
1. **Push to main**: Automatically runs on pushes to the main branch

### Differences from Jenkins Workflow

The GitHub Actions workflow includes the following changes from the original Jenkins groovy script:

1. **Runtime Installation**: kubectl, helm, and Python virtualenv are installed at runtime instead of relying on pre-installed tools
1. **Local Execution**: Ansible runs with `ansible_connection=local` instead of SSH, since the workflow runs directly on the runner
1. **Self-Contained**: All dependencies are installed fresh for each run
1. **Error Handling**: Enhanced with conditional steps and proper cleanup

### Troubleshooting

If the workflow fails:

1. Check the workflow run logs in the Actions tab
1. Download the archived logs artifacts for detailed component logs
1. Ensure the runner has sufficient resources (disk space, memory)
1. Check that network configuration is correct for your environment
