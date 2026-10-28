# SPDX-FileCopyrightText: 2026-present Intel Corporation
# SPDX-License-Identifier: Apache-2.0
"""Guards on where the RAN roles keep the configs they hand to containers.

A config rendered to /tmp does not survive a reboot: /tmp is a tmpfs on many
hosts and is cleared by systemd-tmpfiles after 10 days on the rest. A
container with `restart_policy: unless-stopped` then restarts with Docker
having created an empty directory at the missing bind source, cannot read its
config, and ends up stopped rather than reporting a missing file.

The ocudu, srsran and oai gNB and UE containers render to /var/lib/<dep>/conf
instead. Three deps have not been migrated and are listed in NOT_MIGRATED with
the reason; the tests fail if any *new* /tmp path appears, so the list can only
shrink.

These tests read the task files as YAML, so none of this needs a host, Docker
or Ansible's runtime.
"""

import glob
import os

import pytest
import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")

# Deps still staging container configs in /tmp. None of these has
# `restart_policy: unless-stopped`, so none reproduces the restart loop that
# motivated the migration, but they keep the reboot-persistence problem.
NOT_MIGRATED = {
    # Rendered on the host, then `docker cp`'d into the container, so there is
    # no bind mount and the container keeps its own copy across a restart.
    "deps/gnbsim/roles/simulator/tasks/start.yml": "staged for docker cp, not bind-mounted",
    # Bind-mounts its config, a generated RSA private key and a certificate
    # from /tmp. The key is generated with `creates:`, so a pre-existing path
    # is adopted rather than regenerated.
    "deps/n3iwf/roles/n3iwf/tasks/start.yml": "config, TLS key and cert still in /tmp",
    # Bind-mounts the /tmp/ueransim directory; custom-ue.yaml carries key
    # material and is rendered without an explicit mode.
    "deps/ueransim/roles/simulator/tasks/start.yml": "config directory still in /tmp",
}

START_TASKS = sorted(glob.glob(os.path.join(ROOT, "deps", "*", "roles", "*", "tasks", "start.yml")))
TEMPLATE_KEYS = ("template", "ansible.builtin.template")


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


MIGRATED = [p for p in START_TASKS if rel(p) not in NOT_MIGRATED]


def tasks(path):
    with open(path) as f:
        return yaml.safe_load(f) or []


def dicts(path):
    return [t for t in tasks(path) if isinstance(t, dict)]


def module(task, keys):
    for key in keys:
        spec = task.get(key)
        if isinstance(spec, dict):
            return spec
    return None


def host_side(volume):
    """The host path of a `host:container[:opts]` bind mount, or None.

    A volume whose left side is not absolute is a named Docker volume.
    """
    if not isinstance(volume, str) or ":" not in volume:
        return None
    host = volume.split(":", 1)[0]
    return host if host.startswith("/") else None


def test_not_migrated_list_does_not_rot():
    for path in NOT_MIGRATED:
        assert os.path.exists(os.path.join(ROOT, path)), "%s is listed but gone" % path


@pytest.mark.parametrize("path", MIGRATED, ids=rel)
def test_no_container_mounts_a_tmp_path(path):
    for task in dicts(path):
        spec = task.get("community.docker.docker_container")
        if not isinstance(spec, dict):
            continue
        for volume in spec.get("volumes") or []:
            host = host_side(volume)
            assert host is None or not host.startswith("/tmp/"), (
                "%s mounts %s from /tmp, which does not survive a reboot" % (rel(path), volume)
            )


@pytest.mark.parametrize("path", MIGRATED, ids=rel)
def test_rendered_configs_do_not_land_in_tmp(path):
    for task in dicts(path):
        spec = module(task, TEMPLATE_KEYS + ("copy", "ansible.builtin.copy"))
        dest = (spec or {}).get("dest")
        assert not (dest or "").startswith("/tmp/"), (
            "%s renders %s into /tmp" % (rel(path), dest)
        )


@pytest.mark.parametrize("path", MIGRATED, ids=rel)
def test_ue_configs_are_not_world_readable(path):
    """A UE config carries milenage k/opc and the IMSI."""
    for task in dicts(path):
        spec = module(task, TEMPLATE_KEYS)
        dest = (spec or {}).get("dest") or ""
        if "ue" not in os.path.basename(dest).lower():
            continue
        assert spec.get("mode") == "0600", (
            "%s renders the UE config %s with mode %r; it carries key material"
            % (rel(path), dest, spec.get("mode"))
        )
