import time

print("--- Admin Approval Console ---")
print("Waiting for pending Gateway requests...")
time.sleep(2)
print("\n[ALERT] New pending execution request!")
print("User: Anika")
print("Action: bash_execution")
print("Target: mock_scripts/update_network_daemon.sh")
print("Risk Level: HIGH")

choice = input("\nDo you [A]pprove or [D]eny this action? ")

if choice.lower() == 'a':
    print("\nSending APPROVAL to Gateway...")
    print("Gateway routing execution to OpenSandbox (gVisor)...")
else:
    print("\nSending DENY to Gateway...")
    print("Execution blocked.")
