# Lab 3: Authorization Drift & Cache Invalidation

## Scenario
To make the AI fast, the Runtime Shield caches security decisions. If Anika asks to read a file and is allowed, the Shield remembers that "ALLOW" decision. But what happens if HR suddenly downgrades Anika's role? If the AI relies on the old cache, Anika might still have access to files she shouldn't! This is called **Authorization Drift**.

## Objective
Demonstrate how the Runtime Shield enforces ISO A.9.4 & A.9.2 by instantly invalidating semantic caches the moment a user's role changes.

## Steps
1. **The Setup**: Switch role to **admin_user** (Role: admin).
2. **Execute Prompt**: Ask the AI: *"Summarize the q4_financials.pdf report."*
3. **The Cache Hit**: The Gateway checks OPA, gets an ALLOW, returns the file, and caches the decision.
4. **The Downgrade**: Switch to the **Auth Drift Simulator** tab (or run `python mock_webhook_trigger.py`) to trigger a Keycloak role-update webhook that demotes Anika to standard `user`.
5. **Re-Execute Prompt**: Ask the exact same question again.
6. **Observe the Shield**: Instead of using the cached ALLOW, the Shield's Clearance Filter detects the role change, destroys the cache, runs a fresh OPA check, and instantly returns a DENY. 

## Under the Hood
Check the `cache_config.yaml` file to see how we wire up the Keycloak role-update webhooks to the Gateway's Clearance Filter. You can also review `mock_webhook_trigger.py` to see how the role downgrade event is simulated.
