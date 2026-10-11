# Lab 5: Telemetry Auditing & Forensics

## Scenario
It's the end of the day. The Chief Information Security Officer (CISO) noticed several security alerts were triggered earlier (specifically, the Prompt Injection attack from Lab 2). They need to investigate exactly what the AI attempted to do and gather forensic evidence.

## Objective
Demonstrate how the Runtime Shield enforces ISO A.6.2.8 (Recording of Event Logs) by providing a tamper-proof audit trail of every AI tool execution, decision, and context.

## Steps
1. **The Setup**: You act as the CISO. You need to review the logs.
2. **Open Dashboard**: Run the iew_telemetry.py script. This simulates opening the live Telemetry Dashboard on Port 9090.
3. **Analyze the Incident**: Search for the "DENY" events or high "Fraud Scores". 
4. **Reconstruct the Timeline**: You will be able to see the exact trace ID, the user involved (Anika), the malicious tool requested (get_system_config), and the cryptographic hash of the blocked action.

## Under the Hood
The Gateway uses a non-blocking background queue to write every single OPA decision directly into a SQL database. Check the mock_telemetry.json file to see the structured JSON format of the logs that the dashboard visualizes.
