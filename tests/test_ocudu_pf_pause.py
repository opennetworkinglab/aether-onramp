# SPDX-FileCopyrightText: 2026-present Intel Corporation
# SPDX-License-Identifier: Apache-2.0
"""Guards on 802.3x pause on the OCUDU fronthaul PF.

The PF neither sends nor honours pause. A 7.2 fronthaul frame that is held
back misses its reception window, and pause halts the PTP on the same port.
On an E810 PF with an SR-IOV VF, sending pause also stops the VF's transmit
for good once the port asserts XOFF.

The verifier's pause check is run against canned `ethtool -a` output, in the
tab-separated layout ethtool prints, with ethtool stubbed on PATH, so none of
this needs a NIC or a host.
"""

import os
import re
import subprocess

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
DPDK_ROLE = os.path.join(ROOT, "deps", "ocudu", "roles", "dpdk")
TEMPLATE = os.path.join(DPDK_ROLE, "templates", "pf-tuning.service.j2")
VERIFIER = os.path.join(DPDK_ROLE, "files", "verify-dpdk-services.sh")

PF = "ens1f0"


def ethtool_a(rx, tx, negotiated=None):
    """Formats `ethtool -a` output as ethtool 6.7 prints it."""
    lines = [
        f"Pause parameters for {PF}:",
        f"Autonegotiate:\t{'on' if negotiated else 'off'}",
        f"RX:\t\t{rx}",
        f"TX:\t\t{tx}",
    ]
    if negotiated:
        lines += [f"RX negotiated:\t{negotiated[0]}", f"TX negotiated:\t{negotiated[1]}"]
    return "\n".join(lines) + "\n"


def pause_verdict(tmp_path, pause_output):
    """Runs check_pf_tuning with stubbed tools and returns its pause line."""
    stubs = tmp_path / "bin"
    stubs.mkdir()
    (tmp_path / "pause").write_text(pause_output)
    for name, body in {
        "ethtool": f'[ "$1" = "-a" ] && cat "{tmp_path / "pause"}"\nexit 0\n',
        "tc": "exit 0\n",
        "ip": "exit 0\n",
    }.items():
        stub = stubs / name
        stub.write_text("#!/bin/sh\n" + body)
        stub.chmod(0o755)

    # Everything but the closing `main "$@"`, so the functions load without running.
    with open(VERIFIER) as f:
        functions = f.read().rsplit('main "$@"', 1)[0]
    result = subprocess.run(
        ["bash", "-c", functions + f"\ncheck_pf_tuning {PF}\n"],
        capture_output=True,
        text=True,
        env={"PATH": f"{stubs}:{os.environ['PATH']}"},
        check=True,
    )
    lines = [line for line in result.stdout.splitlines() if "pause" in line]
    assert len(lines) == 1, result.stdout
    return lines[0]


def test_pf_tuning_turns_pause_off():
    with open(TEMPLATE) as f:
        commands = [line for line in f if re.match(r"ExecStart=ethtool -A ", line)]
    assert len(commands) == 1
    assert commands[0].split()[-4:] == ["rx", "off", "tx", "off"]


@pytest.mark.parametrize(
    "output, verdict",
    [
        (ethtool_a("off", "off"), "PASS"),
        (ethtool_a("off", "off", negotiated=("on", "on")), "PASS"),
        (ethtool_a("on", "on"), "FAIL"),
        (ethtool_a("on", "off"), "FAIL"),
        (ethtool_a("off", "on"), "FAIL"),
        ("", "WARN"),
    ],
    ids=["rx-off-tx-off", "negotiated-lines-ignored", "rx-on-tx-on", "rx-on-tx-off", "rx-off-tx-on", "no-output"],
)
def test_verifier_pause_check(tmp_path, output, verdict):
    assert pause_verdict(tmp_path, output).startswith(f"{verdict}:")
