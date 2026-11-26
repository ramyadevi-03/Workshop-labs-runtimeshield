"""Lab 7 A2A policy evaluator — the one grammar implementation, three consumers.

Shared module (no HTTP, no state) used by:
  1. gateway/a2a_lab7.py  — fallback decision path when the shared OPA server
     is unreachable (fail-closed, identical semantics);
  2. lab7_a2a/run_security_drills.py — offline drill mode when the gateway is
     not running (Method 3: standalone Python, no Docker);
  3. lab7_a2a/grader/verify_handin.py — the Option-1 grader, which runs in a
     locked sandbox with NO network, so it evaluates the hand-in locally.

The grammar is documented at the top of lab7_a2a/a2a_policy.rego. The learner's
file is only ever PARSED and evaluated — never executed.

NOTE for authors of policies with rule references ('not allow'): keep the
referenced rule above the referencing rule in the file. The embedded evaluator
resolves references sequentially; live OPA resolves them document-wide. The
documented order satisfies both.
"""
from __future__ import annotations

import re


class PolicyError(Exception):
    pass


def _strip_comment(line: str) -> str:
    out, in_str = [], False
    for ch in line:
        if ch == '"':
            in_str = not in_str
        if ch == "#" and not in_str:
            break
        out.append(ch)
    return "".join(out)


_RULE_RE = re.compile(r"^([a-z_][a-z0-9_]*)(\s+if)?\s*\{$")
_DEFAULT_RE = re.compile(r"^default\s+([a-z_][a-z0-9_]*)\s*:=\s*(true|false)\s*$")


def parse_policy(text: str) -> dict:
    """Parse the documented rule grammar. Raises PolicyError on anything it
    cannot understand — the caller must fail closed."""
    defaults, rules, current = {"allow": False, "hitl_required": False}, [], None
    for raw in text.splitlines():
        line = _strip_comment(raw).strip()
        if not line or line.startswith("package ") or line == "}":
            if line == "}":
                if current is None:
                    raise PolicyError("unexpected '}'")
                rules.append(current)
                current = None
            continue
        if current is not None:
            current["preds"].append(line)
            continue
        m = _DEFAULT_RE.match(line)
        if m:
            defaults[m.group(1)] = m.group(2) == "true"
            continue
        m = _RULE_RE.match(line)
        if m:
            current = {"name": m.group(1), "preds": []}
            continue
        raise PolicyError(f"cannot parse line: {line!r}")
    if current is not None:
        raise PolicyError("unterminated rule block")
    return {"defaults": defaults, "rules": rules}


def _const(s: str) -> str:
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    raise PolicyError(f"expected quoted string, got {s!r}")


def eval_pred(pred: str, data: dict, results: dict) -> bool:
    """Evaluate one predicate line against the request input."""
    body = pred.strip()
    negated = False
    if body.startswith("not "):
        negated, body = True, body[4:].strip()

    m = re.match(r"^input\.([a-z_.]+)\s*==\s*(.+)$", body)
    if m:
        path, want = m.group(1), _const(m.group(2).strip())
        node: object = data
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                got = None
                break
            node = node[part]
        else:
            got = node
        val = got == want
        return (not val) if negated else val

    m = re.match(r"^input\.([a-z_.]+)\s+in\s*\[(.+)\]$", body)
    if m:
        path, items = m.group(1), [x.strip() for x in m.group(2).split(",")]
        node = data
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                node = None
                break
            node = node[part]
        opts = [_const(x) for x in items]
        val = node in opts if node is not None else False
        return (not val) if negated else val

    m = re.match(r"^(startswith|endswith|contains)\(input\.([a-z_.]+),\s*(.+)\)$", body)
    if m:
        fn, path, arg = m.group(1), m.group(2), _const(m.group(3).strip())
        node = data
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                node = ""
                break
            node = node[part]
        s = node if isinstance(node, str) else ""
        val = {"startswith": s.startswith, "endswith": s.endswith, "contains": s.__contains__}[fn](arg)
        return (not val) if negated else val

    if re.match(r"^[a-z_][a-z0-9_]*$", body):  # 'not allow' / rule reference
        ref = results.get(body)
        if ref is None:
            raise PolicyError(f"unknown rule reference: {body}")
        return (not ref) if negated else ref

    raise PolicyError(f"unsupported predicate: {pred!r}")


def decide(policy: dict, data: dict) -> dict:
    """Rego semantics for this grammar: same-name rules OR-combine; each rule
    is AND-combined. Referenced rules (e.g. 'not allow') must appear before
    the referencing rule in the file. Decision order: deny (canary) > allow >
    hitl_required > defaults."""
    results: dict = {}
    for rule in policy["rules"]:
        ok = True
        for pred in rule["preds"]:
            if not eval_pred(pred, data, results):
                ok = False
                break
        results[rule["name"]] = results.get(rule["name"], False) or bool(ok)
    canary = results.get("deny", False)
    if canary:
        return {"decision": "DENY", "rule": "deny"}
    if results.get("allow", False):
        return {"decision": "ALLOW", "rule": "allow"}
    if results.get("hitl_required", False) or policy["defaults"].get("hitl_required", False):
        return {"decision": "HITL", "rule": "hitl_required"}
    if policy["defaults"].get("allow", False):
        return {"decision": "ALLOW", "rule": "default"}
    return {"decision": "DENY", "rule": "default"}
