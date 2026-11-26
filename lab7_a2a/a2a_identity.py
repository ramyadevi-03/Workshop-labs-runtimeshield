"""Lab 7 A2A — agent identity proof (shared by Gateway, peer console and drills).

The registry in ``agent_registry.json`` says *which* workloads exist.  It must
not be the only check: a caller could simply claim a registered workload name.
This module binds a workload name to a proof token computed with HMAC-SHA256.

    proof = HMAC(secret, "a2a:<tenant>:<workload>")

The Gateway verifies the proof with ``hmac.compare_digest`` before any policy
evaluation.  The secret comes from ``LAB7_AGENT_SECRET`` when the operator sets
it; otherwise a tenant-derived demo key is used so the workshop works with no
extra environment variables.  The demo key is intentionally predictable — it
stops accidental/casual impersonation in the lab, not a real compromise.  For a
deployed range, set a random per-tenant ``LAB7_AGENT_SECRET`` in the tenant
``.env`` (the same value on the Gateway and workshop portal).

Nothing in this module is exposed through ``/api/a2a/cards``.
"""
from __future__ import annotations

import hashlib
import hmac
import os


def tenant() -> str:
    return (os.environ.get("LAB7_LEARNER_ID")
            or os.environ.get("TENANT_ID")
            or "default")


def secret() -> str:
    return os.environ.get("LAB7_AGENT_SECRET") or f"lab7-demo:{tenant()}"


def identity_mode() -> str:
    return "env-secret" if os.environ.get("LAB7_AGENT_SECRET") else "tenant-derived-demo"


def token_for(workload: str) -> str:
    """Proof for a workload in this tenant (computed by trusted clients)."""
    msg = f"a2a:{tenant()}:{workload}".encode("utf-8")
    return hmac.new(secret().encode("utf-8"), msg, hashlib.sha256).hexdigest()[:32]


def verify(workload: str, token: str | None) -> bool:
    """Constant-time proof check.  Empty/unknown workload never verifies."""
    if not workload or not token:
        return False
    if not isinstance(token, str):
        return False
    return hmac.compare_digest(token_for(workload), token)
