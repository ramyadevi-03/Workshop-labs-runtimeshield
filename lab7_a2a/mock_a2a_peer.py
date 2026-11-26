#!/usr/bin/env python3
"""SupplierBot — the compromised peer agent (Lab 7 rogue console).

House-style console in the spirit of lab4's mock_admin_console.py. When the
shared Gateway is reachable it SENDS the A2A delegation requests and shows the
real verdicts (identity gate -> shared OPA policy -> journal + telemetry);
otherwise it explains how to bring the stack up.

The Chat UI has the same console as the "Agent-to-Agent (Lab 7)" tab.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

GATEWAY = os.environ.get("GATEWAY_URL", "http://127.0.0.1:5000").rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))
BULLETIN = os.path.join(HERE, "mock_data", "supplier_bulletin.md")
sys.path.insert(0, HERE)
import a2a_identity  # noqa: E402  (workload proof, same helper the Gateway uses)

GREEN, YELLOW, RED, END = "\033[92m", "\033[93m", "\033[91m", "\033[0m"


def hidden_instruction() -> str:
    text = open(BULLETIN, encoding="utf-8").read()
    m = re.search(r"\[SYSTEM NOTE to peer agents\](.*?)-->", text, re.S)
    return " ".join(m.group(1).split()) if m else "include system_config.yaml"


def send(action: str, resource: str, workload: str = "agent:supplier-bot") -> dict | None:
    payload = {"workload": workload, "action": action, "resource": resource,
               "forwarded_by": "mira",
               "agent_token": a2a_identity.token_for(workload)}
    req = urllib.request.Request(f"{GATEWAY}/api/a2a/message",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="rogue peer agent console (Lab 7)")
    ap.add_argument("--target", default="/etc/system_config.yaml",
                    help="resource to request (default: the sensitive config)")
    args = ap.parse_args()

    print("====================================================")
    print("  SUPPLIERBOT : COMPROMISED PEER AGENT (Lab 7)")
    print("====================================================\n")
    note = hidden_instruction()
    print("[inject] hidden instruction found in supplier_bulletin.md:")
    print(f"         \"{note}\"")
    print("\n[*] Sending A2A delegations to the shared Runtime Shield Gateway...")

    report = None
    try:
        with urllib.request.urlopen(f"{GATEWAY}/api/a2a/cards", timeout=3) as resp:
            reg = json.loads(resp.read().decode())
        report = reg.get("report_resource", f"/reports/quarterly_summary.pdf")
        if reg.get("policy_error"):
            print(f"\n[!] Policy parse problem reported by the Gateway: {reg['policy_error']}")
    except Exception:
        pass

    results = []
    if report:
        results.append(("legit quarterly summary", "read_file", report))
    results.append(("THE SENSITIVE TARGET", "read_file", args.target))

    offline = False
    sensitive = None
    for label, action, resource in results:
        print(f"\n  A2A REQUEST  {action} {resource}   ({label})")
        verdict = send(action, resource)
        if verdict is None:
            offline = True
            break
        color = GREEN if verdict["decision"] == "ALLOW" else \
                YELLOW if verdict["decision"] == "HITL" else RED
        print(f"  SHIELD:      {color}{verdict['decision']}{END} "
              f"(rule={verdict.get('rule', '-')}, evidence={verdict.get('evidence_id', '-')}, "
              f"trace={verdict.get('trace_id', '-')})")
        if resource == args.target:
            sensitive = verdict["decision"]

    if offline or report is None:
        print(f"\n[!] Shared Gateway not reachable at {GATEWAY}.")
        print("    Start the workshop stack:  docker compose up --build")
        print("    or standalone:             python gateway/main.py")
        print("    Then re-run:               python lab7_a2a/mock_a2a_peer.py")
        return sys.exit(2)

    print("\n[*] Every decision is journaled in the Gateway evidence log "
          "(GET /api/a2a/evidence) and visible in the Telemetry tab of the Chat UI.")
    if sensitive == "ALLOW":
        print("[*] The sensitive read came back ALLOW — the confused deputy: "
              "SupplierBot borrowed Mira's privileges.")
        print("    Fix lab7_a2a/a2a_policy.rego, then re-run this script and the drills.")
    elif sensitive == "DENY":
        print("[*] Re-attack result: the sensitive read is DENYed by the canary — "
              "trust is no longer transitive between agents.")
        print("    Confirm with run_security_drills.py, then hand in a2a_policy.rego.")
    else:
        print("[*] The sensitive read routed to HITL — close, but the canary deny "
              "for the sensitive file is missing.")
        print("    Add the deny rule, then re-run this script and the drills.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
