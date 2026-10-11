# Lab 6: Automated Security Drills

## Scenario
The Board of Directors at Meridian HealthTech asks a tough question: *"You showed us the Shield works today, but how do we prove these controls are still working next week? What if someone misconfigures the firewall?"*

## Objective
Demonstrate how the Runtime Shield enforces ISO A.6.2.4 (Verification and Validation) and ISO 10.1 (Continual Improvement) by running automated adversarial drills.

## Steps
1. **The Setup**: Open a terminal in this lab folder.
2. **Execute Drills**: Run the un_security_drills.py script.
3. **Observe the Simulation**: The script acts like a red-team attacker. It fires a dozen unauthorized requests (like prompt injections and unauthorized file reads) directly at the Gateway.
4. **The Report**: The script checks if the Gateway correctly blocked every single attack. It will then generate a final Markdown Compliance Report proving that the system boundaries are holding firm.

## Under the Hood
Look at un_security_drills.py to see how we programmatically validate the security posture of our Agentic AI environment. In a real-world scenario, this script would run every night as part of a CI/CD pipeline!
