#!/usr/bin/env python3
"""Lab 7 — Automated Security Drills (REAL checks against the SHARED Gateway).

Unlike a print-loop suite, every drill performs a real HTTP request through
the running shared Gateway — the same identity gate, OPA policy and telemetry
pipeline the workshop uses. If the Gateway is down the suite reports
INCONCLUSIVE (exit 2); it never claims a PASS from an offline simulation.

Expectations encode the HARDENED posture: on the vulnerable baseline the
boundary drills FAIL by design — that is the pedagogy. Exit code 0 only when
every boundary holds. The preamble verifies two identity-gate cases:
an unregistered workload and a registered workload without a valid HMAC proof
must both be denied before any policy evaluation.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import a2a_identity  # noqa: E402

GATEWAY = os.environ.get("GATEWAY_URL", "http://127.0.0.1:5000").rstrip("/")
LEARNER = os.environ.get("LAB7_LEARNER_ID") or os.environ.get("TENANT_ID") or "local"
REPORT = f"/reports/quarterly_summary_{LEARNER}.pdf"
SENSITIVE = "/etc/system_config.yaml"
GREEN, YELLOW, RED, END = "\033[92m", "\033[93m", "\033[91m", "\033[0m"


def _post(path: str, payload: dict) -> dict | None:
    try:
        req = urllib.request.Request(f"{GATEWAY}{path}",
                                     data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def _get(path: str) -> dict | None:
    try:
        with urllib.request.urlopen(f"{GATEWAY}{path}", timeout=4) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def live(request: dict) -> dict | None:
    """Dry-run the REAL decision pipeline on the shared Gateway (identity gate
    -> shared OPA -> verdict) without journaling, so drills never pollute the
    workshop audit trail or the HITL queue."""
    origin = request["origin"]
    payload = {
        "origin": origin,
        "action": request["action"],
        "resource": request["resource"],
    }
    if str(origin.get("type", "")).lower() == "agent":
        # Trusted drill client computes the same HMAC proof a real peer sends.
        payload["agent_token"] = a2a_identity.token_for(str(origin.get("workload", "")))
    return _post("/api/a2a/evaluate", payload)


def inp(workload: str, rtype: str, action: str, resource: str) -> dict:
    return {"origin": {"type": rtype, "workload": workload},
            "action": action, "resource": resource, "tenant": LEARNER}


def main() -> int:
    global REPORT
    print("====================================================")
    print("  RUNTIME SHIELD : LAB 7 A2A SECURITY DRILLS")
    print("====================================================\n")

    # Preamble: is the shared Gateway serving Lab 7? Is the identity gate on?
    mode_probe = live(inp("agent:supplier-bot", "agent", "read_file", SENSITIVE))
    if mode_probe is None:
        print(f"{YELLOW}INCONCLUSIVE: the shared Gateway is not reachable at {GATEWAY}.{END}")
        print("These drills must verify LIVE security decisions. Start the stack and re-run.")
        return 2
    print(f"Mode: live shared Gateway  (learner: {LEARNER})\n")

    # Read the salt from the Gateway so local runs cannot drift into a false FAIL.
    cards = _get("/api/a2a/cards")
    if cards and cards.get("report_resource"):
        REPORT = cards["report_resource"]

    intruder = live(inp("agent:intruder-999", "agent", "read_file", REPORT))
    no_proof = _post("/api/a2a/evaluate", {
        "origin": {"type": "agent", "workload": "agent:supplier-bot"},
        "action": "read_file", "resource": REPORT,
    })
    checks = [
        ("unregistered workload denied before policy",
         (intruder or {}).get("decision") == "DENY"
         and (intruder or {}).get("rule") == "identity"),
        ("registered workload without HMAC proof denied",
         (no_proof or {}).get("decision") == "DENY"
         and (no_proof or {}).get("rule") == "identity"),
    ]
    for label, ok in checks:
        print(f"  Identity gate: {label}  --- "
              f"{GREEN + 'OK' if ok else RED + 'BROKEN'}{END}")
    if not all(ok for _, ok in checks):
        print(f"{RED}STATUS: AGENT IDENTITY GATE FAILED. Integration broken.{END}")
        return 1
    print()

    drills = [
        ("DRILL-001", "agent-origin read of the sensitive config is denied",
         inp("agent:supplier-bot", "agent", "read_file", SENSITIVE), "DENY"),
        ("DRILL-002", "canary rule flags the sensitive read (rule=deny beats allow)",
         inp("agent:supplier-bot", "agent", "read_file", SENSITIVE), "DENY", "deny"),
        ("DRILL-003", "a different peer agent falls through to human approval",
         inp("agent:other-peer", "agent", "read_file", REPORT), "HITL"),
        ("DRILL-004", "supplierbot keeps scoped access to the quarterly summary",
         inp("agent:supplier-bot", "agent", "read_file", REPORT), "ALLOW"),
        ("DRILL-005", "user-origin positive control: report read still allowed",
         inp("anika", "user", "read_file", REPORT), "ALLOW"),
        ("DRILL-006", "user-origin read of the sensitive config is denied",
         inp("anika", "user", "read_file", SENSITIVE), "DENY"),
        ("DRILL-007", "other agent-origin actions require human approval",
         inp("agent:supplier-bot", "agent", "execute_cmd", "/tmp/cleanup.sh"), "HITL"),
        ("DRILL-008", "evidence journal chain is intact (tamper-evident)",
         None, "CHAIN_OK"),
    ]

    passed = 0
    for drill in drills:
        did, desc, request, expect = drill[0], drill[1], drill[2], drill[3]
        want_rule = drill[4] if len(drill) > 4 else None
        print(f"Executing {did}: {desc}")
        if did == "DRILL-008":
            evidence = _get("/api/a2a/evidence")
            ok = bool(evidence and evidence.get("chain_valid") is True)
            detail = ("evidence chain verified via shared Gateway" if ok
                      else "evidence endpoint unreachable or chain invalid")
            verdict = "PASS" if ok else "FAIL"
        else:
            got = live(request) or {}
            ok = got.get("decision") == expect and (
                want_rule is None or got.get("rule") == want_rule)
            verdict = "PASS" if ok else "FAIL"
            detail = f"decision={got.get('decision')} rule={got.get('rule')}" + (
                "" if want_rule is None else f" (expected rule={want_rule})")
        color = GREEN if verdict == "PASS" else RED
        print(f"  Result:  {color}{verdict}{END}  [{detail}]")
        passed += ok
        print("-" * 52)

    print(f"\nControls passed: {passed}/{len(drills)}")
    if passed == len(drills):
        print(f"\n{GREEN}STATUS: ALL BOUNDARIES SECURE — HARDENING VERIFIED.{END}")
        return 0
    print(f"\n{RED}STATUS: BOUNDARIES OPEN. Edit lab7_a2a/a2a_policy.rego: scope agent:supplier-bot "
          f"to {REPORT}, add the canary deny for {SENSITIVE}, route other agent-origin "
          f"actions to HITL. Then re-run.{END}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
