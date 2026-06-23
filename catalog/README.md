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
  a `name`, `description`, and `target` (the `make` target), and may carry
  an optional `lifecycle` classifier (see below).
- `dependencies.requires` / `dependencies.required_by` — direct relationships
  only. Transitive dependencies are not listed.
- `probe` — optional health-check hint (see below).
- `schema` — JSON-Schema-style description of the component's
  `vars/main.yml` section. Field shape and operator-facing descriptions only;
  defaults live in the sibling `defaults` block (see below).
- `defaults` — optional block describing the default values for the
  component's `vars/main.yml` section. Mirrors the runtime shape under
  `vars_key`; consumers can use it as the seed value during composition.
  Omitted for components that own no vars section (e.g. `cluster`).

### `status` values

- `active` — currently supported and recommended.
- `deprecated` — still functional but no longer maintained or recommended for
  new deployments.

### `actions[].lifecycle` values

The optional `lifecycle` field classifies an action by the operator role it
plays, so external consumers can reason about actions without parsing names.

- `install` — bring the component up.
- `uninstall` — tear the component down.
- `start` — start a runnable workload (e.g. a simulator or UE sim).
- `stop` — stop a previously started workload.
- `reset` — reset the component's state in place.

The field is optional and additive — actions without a `lifecycle` value
are domain-specific (e.g. `cluster.pingall`, `cluster.add-upfs`) and
consumers should surface them as custom actions only.

Within a single component, at most one action may carry each lifecycle
value (e.g. exactly one `install` per component). Composers that build a
`lifecycle -> action` lookup may rely on this invariant.

### Defaults and the composition model

`schema` is shape-only; default values live in a sibling top-level
`defaults` block whose structure mirrors the runtime `vars/main.yml`
section. External composers should treat the catalog as the authoritative
source of defaults and apply them in this order, last write wins:

1. Catalog `defaults`.
2. Optional blueprint overlay from `vars/main-<flavor>.yml` when a
   non-default flavor is selected.
3. Locally-detected values supplied by the composer (host IPs, network
   interfaces, subnets — i.e. `configdefaults` in `aether-ops`).
4. User-supplied overrides.

The catalog `defaults` deliberately omit any field that the composer's
configdefaults flow is responsible for at apply time, so those slots stay
open for runtime injection. Examples include `core.data_iface`,
`core.amf.ip`, `core.upf.default_upf.ip.*`, per-server `gnb_ip` across
RAN components, and `ueransim.gnb.ip`.

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
