# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Aether OnRamp project.

## Quickstart Workflow

The `quickstart.yml` workflow replicates the functionality of the Jenkins groovy workflow found at [opennetworkinglab/aether-jenkins](https://github.com/opennetworkinglab/aether-jenkins/blob/master/quickstart.groovy).

The quickstart-family workflows are implemented as thin callers around
the reusable workflow ``.github/workflows/reusable-quickstart.yml``.
Each caller passes blueprint-specific configuration, validation, and
log-collection commands while sharing the common CI job structure.

### Workflow Stages

1. **Checkout repository**: Clones the repo with all submodules
1. **Set up Python**: Installs Python and creates a virtual environment with Ansible, then exports the virtualenv bin directory to later workflow steps
1. **Configure OnRamp**: Sets up SSH keys, generates hosts.ini via a shared helper script, configures vars/main.yml
1. **Install Aether**: Installs Kubernetes, 5GC core, and gNBsim
1. **Run gNBsim**: Executes the gNBsim test with retry logic (2 attempts)
1. **Validate Results**: Checks that tests passed using the same validation pattern as Jenkins
1. **Retrieve Logs**: Collects logs from all components, using shared helper scripts for common 5GC logs
10. **Archive Artifacts**: Uploads logs as workflow artifacts
11. **Cleanup**: Uninstalls all components (always runs, even on failure), using a shared helper for repeated make cleanup targets
12. **Notify on Failure**: Logs failure information (can be extended with Slack notifications)

### Triggering the Workflow

The workflow has the following triggers:

1. **Manual Dispatch**: Go to Actions → Aether OnRamp Quickstart → Run workflow
1. **Push to main**: Automatically runs on pushes to the main branch

### Differences from Jenkins Workflow

The GitHub Actions workflow includes the following changes from the original Jenkins groovy script:

1. **Runtime Installation**: Python virtualenv and deployment dependencies are installed at runtime instead of relying on pre-installed tools
1. **Local Execution**: Ansible runs with `ansible_connection=local` instead of SSH, since the workflow runs directly on the runner
1. **Self-Contained**: All dependencies are installed fresh for each run
1. **Error Handling**: Enhanced with conditional steps and proper cleanup

### Caveats

Not all workflows will successfully run in the standard GitHub runners, presumably due to a lack of disk space (only 14GB).  The following workflows cannot run in a standard runner but should succeed in a self-hosted runner (e.g., a CloudLab node):

- `quickstart-amp.yml`
- `quickstart-sdran.yml`

### Troubleshooting

If the workflow fails:

1. Check the workflow run logs in the Actions tab
1. Download the archived logs artifacts for detailed component logs
1. Ensure the runner has sufficient resources (disk space, memory)
1. Check that network configuration is correct for your environment
