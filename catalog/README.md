# Aether OnRamp Component Catalog

This directory contains YAML catalog entries that describe the deployable
Aether OnRamp components and the shape of the corresponding `vars/main.yml`
sections.

These files are intended to be consumed by external tooling such as
`aether-ops`. OnRamp itself does not currently load them at runtime.

## Catalog entry shape

Every entry starts with the format identifiers:

- `apiVersion` — catalog format version. Currently `onramp.aetherproject.org/v1`.
- `kind` — always `Component` for entries in this directory.

The remaining top-level fields are:

- `name`, `description` — identity and human-readable summary.
- `repo_url`, `docs_url` — external references.
- `status` — lifecycle stage (see below).
- `ui_visible` — whether external UIs should expose this component.
- `group` — high-level taxonomy (`core`, `platform`, `ran`, `simulator`,
  `network`, `meta`).
- `vars_key` — top-level key in `vars/main.yml` populated by this component.
  Omitted for meta entries that do not own a vars section.
- `install_tier` — integer hint for install ordering. Lower tiers install
  first (`k8s` is `0`).
- `blueprint_file` — optional non-default blueprint under `vars/`
  (e.g. `main-oai.yml`). Omitted when the component uses the default
  `main.yml`.
- `actions` — Makefile targets exposed to operators. Each action declares
  a `name`, `description`, and `target` (the `make` target).
- `dependencies.requires` / `dependencies.required_by` — direct relationships
  only. Transitive dependencies are not listed.
- `probe` — optional health-check hint (see below).
- `schema` — JSON-Schema-style description of the component's
  `vars/main.yml` section. Field shape and operator-facing descriptions only;
  defaults are included only where stable across shipped configurations.

### `status` values

- `active` — currently supported and recommended.
- `deprecated` — still functional but no longer maintained or recommended for
  new deployments.

### `probe.type` values

Probes are advisory hints for consumers that want to render health state.
OnRamp itself does not execute them.

- `kubectl_nodes` — cluster nodes report Ready via `kubectl get nodes`.
  No additional fields.
- `namespace_pods` — pods in `namespace` are running. Requires `namespace`.
- `helm_release` — a Helm release is installed in `namespace`. Requires
  `namespace`.
- `docker_container` — a Docker container named `container` is running.
  Requires `container`.
- `none` — no probe defined.

## Components

The current catalog covers:

- `k8s`
- `5gc`
- `amp`
- `sdran`
- `oscric`
- `gnbsim`
- `ueransim`
- `oai`
- `srsran`
- `ocudu`
- `n3iwf`
- `cluster`
