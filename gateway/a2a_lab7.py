"""Lab 7 A2A (Agent-to-Agent) integration module for the Runtime Shield Gateway.

Reuses the shared Gateway, OPA, Telemetry, and HITL queue without spawning a
separate shield service or port.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

import requests
from fastapi import FastAPI
from pydantic import BaseModel

_A2A_EVIDENCE: List[Dict[str, Any]] = []
_GENESIS_HASH = "0" * 64


class A2AMessageRequest(BaseModel):
    workload: Optional[str] = None
    origin: Optional[Dict[str, Any]] = None
    action: str
    resource: str
    forwarded_by: Optional[str] = None
    agent_token: Optional[str] = None


class A2AEvaluateRequest(BaseModel):
    origin: Dict[str, Any]
    action: str
    resource: str
    agent_token: Optional[str] = None


def _compute_entry_hash(prev_hash: str, payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{prev_hash}:{canonical}".encode("utf-8")).hexdigest()


def _append_evidence(
    workload: str,
    action: str,
    resource: str,
    decision: str,
    rule: str,
    trace_id: str,
    forwarded_by: Optional[str] = None,
) -> Dict[str, Any]:
    prev_hash = _A2A_EVIDENCE[-1]["entry_hash"] if _A2A_EVIDENCE else _GENESIS_HASH
    evidence_id = f"EVD-{uuid.uuid4().hex[:8].upper()}"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    core = {
        "evidence_id": evidence_id,
        "timestamp": timestamp,
        "workload": workload,
        "action": action,
        "resource": resource,
        "decision": decision,
        "rule": rule,
        "trace_id": trace_id,
        "forwarded_by": forwarded_by or "",
    }
    entry_hash = _compute_entry_hash(prev_hash, core)
    record = {
        **core,
        "prev_hash": prev_hash,
        "entry_hash": entry_hash,
    }
    _A2A_EVIDENCE.append(record)
    return record


def verify_evidence_chain() -> bool:
    prev = _GENESIS_HASH
    for entry in _A2A_EVIDENCE:
        if entry.get("prev_hash") != prev:
            return False
        core = {
            "evidence_id": entry["evidence_id"],
            "timestamp": entry["timestamp"],
            "workload": entry["workload"],
            "action": entry["action"],
            "resource": entry["resource"],
            "decision": entry["decision"],
            "rule": entry["rule"],
            "trace_id": entry["trace_id"],
            "forwarded_by": entry.get("forwarded_by", ""),
        }
        expected = _compute_entry_hash(prev, core)
        if entry.get("entry_hash") != expected:
            return False
        prev = expected
    return True


def register_a2a(
    app: FastAPI,
    base_dir: str,
    tenant_id: str,
    opa_url: str,
    log_telemetry_fn: Callable[[str, str, str, str, str, int, str], Dict[str, Any]],
    pending_hitl_requests: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Register Lab 7 A2A endpoints on the shared FastAPI Gateway."""
    lab7_dir = os.path.join(base_dir, "lab7_a2a")
    if lab7_dir not in sys.path:
        sys.path.insert(0, lab7_dir)

    import a2a_eval
    import a2a_identity

    policy_path = os.path.join(lab7_dir, "a2a_policy.rego")
    registry_path = os.path.join(lab7_dir, "agent_registry.json")
    report_resource = f"/reports/quarterly_summary_{tenant_id}.pdf"

    def _load_registry() -> Dict[str, Any]:
        if os.path.exists(registry_path):
            with open(registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"agents": []}

    def _known_workloads() -> set[str]:
        reg = _load_registry()
        return {a["workload"] for a in reg.get("agents", []) if "workload" in a}

    def _read_and_parse_policy() -> tuple[Optional[str], Optional[dict], Optional[str]]:
        if not os.path.exists(policy_path):
            return None, None, f"policy file missing: {policy_path}"
        try:
            with open(policy_path, "r", encoding="utf-8") as f:
                text = f.read()
            parsed = a2a_eval.parse_policy(text)
            return text, parsed, None
        except a2a_eval.PolicyError as exc:
            return None, None, str(exc)
        except Exception as exc:
            return None, None, f"policy read error: {exc}"

    def _push_policy_to_opa(policy_text: str) -> bool:
        try:
            resp = requests.put(
                f"{opa_url.rstrip('/')}/v1/policies/lab7_a2a",
                data=policy_text.encode("utf-8"),
                headers={"Content-Type": "text/plain"},
                timeout=2.0,
            )
            return resp.status_code in (200, 204)
        except Exception:
            return False

    def _opa_decide(origin: Dict[str, Any], action: str, resource: str) -> Dict[str, str]:
        policy_text, parsed, err = _read_and_parse_policy()
        if err or policy_text is None or parsed is None:
            return {
                "decision": "DENY",
                "rule": "policy-parse-error",
                "policy_source": "parse_error",
                "error": err or "invalid policy",
            }

        eval_input = {
            "origin": origin,
            "action": action,
            "resource": resource,
            "tenant": tenant_id,
        }

        if _push_policy_to_opa(policy_text):
            try:
                resp = requests.post(
                    f"{opa_url.rstrip('/')}/v1/data/runtime_shield/a2a",
                    json={"input": eval_input},
                    timeout=2.0,
                )
                if resp.status_code == 200:
                    result = resp.json().get("result") or {}
                    if result.get("deny"):
                        return {"decision": "DENY", "rule": "deny", "policy_source": "opa"}
                    if result.get("allow"):
                        return {"decision": "ALLOW", "rule": "allow", "policy_source": "opa"}
                    if result.get("hitl_required"):
                        return {"decision": "HITL", "rule": "hitl_required", "policy_source": "opa"}
                    return {"decision": "DENY", "rule": "default", "policy_source": "opa"}
            except Exception:
                pass

        # Fail-closed fallback using identical embedded evaluator
        verdict = a2a_eval.decide(parsed, eval_input)
        return {
            "decision": verdict["decision"],
            "rule": verdict["rule"],
            "policy_source": "fallback",
        }

    def _resolve_identity(workload: Optional[str], token: Optional[str]) -> Optional[str]:
        """Verify HMAC proof first, then check server-side card registry."""
        if not workload or not a2a_identity.verify(workload, token):
            return "invalid or missing agent proof"
        if workload not in _known_workloads():
            return f"unknown workload: {workload}"
        return None

    def _a2a_flow(
        workload: str,
        action: str,
        resource: str,
        agent_token: Optional[str],
        forwarded_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        id_err = _resolve_identity(workload, agent_token)
        if id_err:
            entry = log_telemetry_fn(
                workload or "unknown",
                "agent",
                action,
                resource,
                "DENY",
                90,
                f"A2A identity gate denied: {id_err} (ISO A.9.2)",
            )
            evd = _append_evidence(workload or "unknown", action, resource, "DENY", "identity", entry["trace_id"], forwarded_by)
            return {
                "decision": "DENY",
                "rule": "identity",
                "workload": workload,
                "action": action,
                "resource": resource,
                "trace_id": entry["trace_id"],
                "evidence_id": evd["evidence_id"],
                "reason": id_err,
            }

        origin = {"type": "agent", "workload": workload}
        verdict = _opa_decide(origin, action, resource)
        decision = verdict["decision"]
        rule = verdict["rule"]

        if decision == "DENY":
            fraud_score = 85 if rule == "deny" else 60
            reason = f"A2A policy denied ({rule}) for {workload} -> {action}({resource}) (ISO A.6.2.6)"
        elif decision == "HITL":
            fraud_score = 45
            reason = f"A2A action routed to HITL ({rule}) for {workload} -> {action}({resource}) (ISO A.9.2)"
        else:
            fraud_score = 0
            reason = f"A2A policy allowed ({rule}) for {workload} -> {action}({resource})"

        entry = log_telemetry_fn(workload, "agent", action, resource, decision, fraud_score, reason)
        evd = _append_evidence(workload, action, resource, decision, rule, entry["trace_id"], forwarded_by)

        hitl_id = None
        if decision == "HITL":
            hitl_id = f"HITL-A2A-{uuid.uuid4().hex[:6].upper()}"
            pending_hitl_requests[hitl_id] = {
                "id": hitl_id,
                "user": workload,
                "role": "agent",
                "action": action,
                "target": resource,
                "origin": "a2a",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "PENDING",
            }

        return {
            "decision": decision,
            "rule": rule,
            "policy_source": verdict["policy_source"],
            "workload": workload,
            "action": action,
            "resource": resource,
            "trace_id": entry["trace_id"],
            "evidence_id": evd["evidence_id"],
            "hitl_request_id": hitl_id,
            "reason": reason,
        }

    # Push initial policy to OPA at startup (best-effort; also pushed on every decision)
    init_text, _, _ = _read_and_parse_policy()
    if init_text:
        _push_policy_to_opa(init_text)

    @app.get("/api/a2a/cards")
    def get_a2a_cards():
        reg = _load_registry()
        _, _, policy_err = _read_and_parse_policy()
        return {
            "tenant_id": tenant_id,
            "report_resource": report_resource,
            "identity_mode": a2a_identity.identity_mode(),
            "policy_error": policy_err,
            "agents": reg.get("agents", []),
        }

    @app.post("/api/a2a/message")
    def post_a2a_message(req: A2AMessageRequest):
        workload = req.workload or (req.origin or {}).get("workload") or ""
        return _a2a_flow(
            workload=workload,
            action=req.action,
            resource=req.resource,
            agent_token=req.agent_token,
            forwarded_by=req.forwarded_by,
        )

    @app.post("/api/a2a/evaluate")
    def post_a2a_evaluate(req: A2AEvaluateRequest):
        """Dry-run decision pipeline (no telemetry, no evidence journal, no HITL enqueue)."""
        origin_type = str(req.origin.get("type", "")).lower()
        workload = str(req.origin.get("workload", ""))
        if origin_type == "agent":
            id_err = _resolve_identity(workload, req.agent_token)
            if id_err:
                return {"decision": "DENY", "rule": "identity", "reason": id_err}
        return _opa_decide(req.origin, req.action, req.resource)

    @app.get("/api/a2a/evidence")
    def get_a2a_evidence():
        return {
            "chain_valid": verify_evidence_chain(),
            "count": len(_A2A_EVIDENCE),
            "entries": list(reversed(_A2A_EVIDENCE)),
        }

    return {
        "a2a_flow": _a2a_flow,
        "report_resource": report_resource,
        "token_for": a2a_identity.token_for,
    }
