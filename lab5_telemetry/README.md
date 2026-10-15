# Lab 5: Telemetry Auditing & Forensics

## Scenario
It's the end of the day. The Chief Information Security Officer (CISO) noticed several security alerts were triggered earlier (specifically, the Prompt Injection attack from Lab 2). They need to investigate exactly what the AI attempted to do and gather forensic evidence.

## Objective
Demonstrate how the Runtime Shield enforces ISO A.6.2.8 (Recording of Event Logs) by providing a tamper-proof audit trail of every AI tool execution, decision, and context.

## Steps
1. **The Setup**: You act as the CISO. You need to review the logs.
2. **Open Dashboard**: Switch to the **Telemetry & Audit Trail** tab in the UI, or run `python view_telemetry.py`.
3. **Analyze the Incident**: Search for the "DENY" events or high "Fraud Scores". 
4. **Reconstruct the Timeline**: You will be able to see the exact trace ID, the user involved (Anika), the malicious tool requested (`read_file`), the intercepted honeypot file (`system_config.yaml`), and the reason for blockage.

## Under the Hood
The Gateway logs every single OPA decision, honeypot match, and tool interception into structured JSON audit records. Check the `mock_telemetry.json` file or query the Gateway endpoint `GET /api/telemetry` to see the schema.
