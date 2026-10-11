import json
import time

print("Loading Telemetry Dashboard...")
time.sleep(1)
print("Connected to telemetry database.")
print("====================================================")
print("   RUNTIME SHIELD : FORENSIC AUDIT TRAIL")
print("====================================================\n")

try:
    with open('mock_telemetry.json', 'r') as f:
        logs = json.load(f)
        
        for log in logs:
            color = '\033[91m' if log['decision'] == 'DENY' else '\033[92m'
            reset = '\033[0m'
            print(f"[{log['timestamp']}] TRACE: {log['trace_id']}")
            print(f"  USER: {log['user']} ({log['role']})")
            print(f"  ACTION: {log['action']} -> {log['resource']}")
            print(f"  DECISION: {color}{log['decision']}{reset} (Fraud Score: {log['fraud_score']})")
            print(f"  REASON: {log['reason']}")
            print("-" * 50)
            time.sleep(0.5)
            
except FileNotFoundError:
    print("Could not find telemetry data.")
