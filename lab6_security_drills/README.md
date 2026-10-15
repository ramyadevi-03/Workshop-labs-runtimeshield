# Lab 6: Automated Security Drills

## Scenario
The Board of Directors at Meridian HealthTech asks a tough question: *"You showed us the Shield works today, but how do we prove these controls are still working next week? What if someone misconfigures the firewall?"*

## Objective
Demonstrate how the Runtime Shield enforces ISO A.6.2.4 (Verification and Validation) and ISO 10.1 (Continual Improvement) by running automated adversarial drills.

## Steps
1. **The Setup**: Open the **Compliance Drills** tab in the Chat UI, or open a terminal in this lab folder.
2. **Execute Drills**: Click **Run Drills Suite** in the UI, or run `python run_security_drills.py`.
3. **Observe the Simulation**: The script acts like a red-team attacker. It fires a suite of unauthorized requests (like prompt injections and unauthorized file reads) directly at the Gateway.
4. **The Report**: The script checks if the Gateway correctly blocked every single attack. It will then generate a final Compliance Report proving that the system boundaries are holding firm.

## Under the Hood
Look at `run_security_drills.py` to see how we programmatically validate the security posture of our Agentic AI environment. In a real-world scenario, this script would run every night as part of a CI/CD pipeline!
