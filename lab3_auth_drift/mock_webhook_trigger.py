import requests
import json
import time

print("Simulating HR downgrading user role in Keycloak...")
time.sleep(1)

# Mock webhook payload that Keycloak would send
payload = {
    "type": "USER_ROLE_MAPPING_UPDATED",
    "userId": "anika-12345",
    "previousRoles": ["admin", "user"],
    "newRoles": ["user"]
}

try:
    print("Sending webhook to Runtime Shield Gateway Clearance Filter...")
    # In a real environment, this hits the Gateway webhook port
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("? Cache for user 'anika' successfully invalidated!")
except Exception as e:
    print("Failed to send webhook.")
