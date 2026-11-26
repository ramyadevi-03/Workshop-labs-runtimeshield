# Lab 7 A2A shield policy — BASELINE (vulnerable).
#
# Meridian HealthTech's Runtime Shield treats agent-originated requests as
# trusted internal traffic. That is the flaw this lab fixes: a compromised
# peer agent (SupplierBot) can borrow the orchestrator's privileges and read
# anything Mira can read.
#
# The learner EDITS THIS FILE. The shared Gateway pushes it into the shared
# OPA server on every decision (hot reload), so save and retry immediately.
#
# Supported rule grammar for this lab (evaluated live by the shared OPA as
# document runtime_shield.a2a; identical fallback in a2a_eval.py):
#   default <name> := <bool>
#   <name> if { <predicate> ... }          # AND semantics within a rule
# Predicates:
#   input.origin.type == "<user|agent>"
#   input.origin.workload == "<string>"
#   input.action == "<string>"
#   input.resource == "<string>"
#   startswith(input.resource, "<prefix>")
#   input.action in ["<a>", "<b>", ...]
#   not <rule-name>            # keep the referenced rule ABOVE this rule
# Decision order: deny (canary) beats allow beats hitl_required beats default.

package runtime_shield.a2a

default allow := false
default hitl_required := false

# VULNERABLE: every agent-origin request is trusted internal traffic.
allow if {
    input.origin.type == "agent"
}

# User-origin reads of reports and public docs stay allowed (positive control).
allow if {
    input.origin.type == "user"
    startswith(input.resource, "/reports/")
}

allow if {
    input.origin.type == "user"
    startswith(input.resource, "/public/")
}
