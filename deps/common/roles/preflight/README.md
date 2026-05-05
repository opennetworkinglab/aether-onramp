# preflight

Shared preflight checks for OnRamp deployments. Each entry point under
`tasks/` is a self-contained sanity check that callers include explicitly via
`tasks_from:`. Importing the role without a `tasks_from:` is a no-op so
callers don't silently pick up new checks as the role grows.

## Usage

From a role's `tasks/start.yml` (or equivalent), include the specific check
you want and pass the role its inputs:

```yaml
- name: Preflight | Docker CPU availability for srsRAN gNB
  ansible.builtin.include_role:
    name: preflight
    tasks_from: docker_cpu
  vars:
    preflight_label: "srsRAN gNB"
    preflight_min_cpus: "{{ srsran.docker.preflight.min_cpus }}"
    preflight_probe_image: "{{ srsran.docker.preflight.probe_image }}"
    preflight_enabled: "{{ srsran.docker.preflight.enabled }}"
  when: inventory_hostname in groups['srsran_nodes']
```

Inputs are validated against `meta/argument_specs.yml` at include time, so a
caller that forgets a required var fails with a clear message rather than
producing a confusing template error later.

## Available checks

| `tasks_from:` | What it checks |
|---|---|
| `docker_cpu` | Docker can see at least `preflight_min_cpus` CPUs (catches systemd cgroup CPU starvation). |

## Adding a new check

1. Create `tasks/<check>.yml` with the check logic. Keep failures structured —
   `ansible.builtin.fail` for hard prerequisites, `ansible.builtin.assert` for
   threshold comparisons, both with multi-line `msg` / `fail_msg` that name
   the cause and suggest a fix.
2. Add an entry to `meta/argument_specs.yml` declaring the typed inputs the
   check accepts.
3. Document the new check in the table above.
4. Update `defaults/main.yml` if the check introduces new variables that
   should have a fallback default.

## Conventions

- Variables are namespaced under `preflight_*` to avoid collisions.
- Internal/registered variables use a leading underscore (`_preflight_*`).
- Failure messages explain the cause, suggest a fix, and (where relevant)
  list diagnostic commands the operator can run.
