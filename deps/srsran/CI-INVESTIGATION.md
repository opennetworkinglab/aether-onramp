# srsRAN CI Investigation

## Current status

Upstream `main` was reverted to the `rel-0.4.0` srsRAN images because newer
images were not reliable on the default GitHub-hosted runner.

On June 10, 2026, branch `test/upstream-srsran-rel-0.8.0` retested the latest
`upstream/main` with:

- `aetherproject/srsran-gnb:rel-0.8.0`
- `aetherproject/srsran-ue:rel-0.8.0`

That branch succeeded when run on a larger 8-core GitHub runner.

## What we learned

This materially changes the working hypothesis:

- the `rel-0.8.0` image pair is not universally broken in Aether OnRamp CI;
- the failure depends on the runner environment; and
- runner capacity, CPU topology, scheduling, or related host characteristics
  are now the leading suspects.

In other words, the most recent evidence points to a runner-dependent
execution problem rather than a simple "new srsRAN image is bad" regression.

## Practical implication

For now, `rel-0.4.0` remains the conservative default for standard
GitHub-hosted runners.

The `test/upstream-srsran-rel-0.8.0` branch is a proof point that the latest
srsRAN images can work with the current OnRamp codebase when the runner
environment is sufficiently capable.
