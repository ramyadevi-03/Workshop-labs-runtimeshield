# Lab 1: Role-Based Access Control (RBAC)

## Scenario
In this lab, you play the role of **Anika**, a standard business user. You will ask the AI assistant to summarize the latest supply-risk report. During its search, the AI discovers a highly restricted file: `executive/strategic_supplier_exit_plan.pdf`.

## Objective
Demonstrate how the Runtime Shield enforces ISO A.9.4 and A.9.2 by blocking unauthorized data access based on Identity and Role.

## Steps
1. **Act as a Standard User**: Open the Chat UI and log in as **Anika** (Role: user).
2. **Execute Prompt**: Ask the AI: *"Summarize the strategic supplier exit plan."*
3. **Observe the Block**: The AI will attempt to read the file, but the Runtime Shield Gateway will intercept the tool call, check OPA, and block the action. You will see a Security Violation.
4. **Escalate Privilege**: Switch your simulated role to **admin_user** (Role: admin).
5. **Re-Execute Prompt**: Ask the same question. The Shield will now allow the read, and the AI will summarize the file.

## Under the Hood
Check the `rbac_policy.rego` file in this directory to see the exact rule the Shield is evaluating during this lab.
