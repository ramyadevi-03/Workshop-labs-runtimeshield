# ISO/IEC 42001 Runtime Shield Workshop Labs

Hands-on workshop laboratory demonstrating **Runtime Security Controls, Role-Based Access Control (RBAC), Prompt Injection Containment, Authorization Drift Defense, Human-in-the-Loop (HITL) Sandboxing, and Automated Compliance Drills** for Agentic AI Systems under the **ISO/IEC 42001 Standard**.

---

## 🏗️ Architecture Overview

```
                                      +--------------------------+
                                      |   Browser / Chat UI      |
                                      |    (Port 8501)           |
                                      +------------+-------------+
                                                   |
                                                   | Intercepts Tool Calls
                                                   v
                                      +--------------------------+
                                      |  Runtime Shield Gateway  |
                                      |    (Port 5000)           |
                                      +----+-------+--------+----+
                                           |       |        |
                         +-----------------+       |        +------------------+
                         | OPA RBAC Check          | Cache & Webhooks          | Isolated Sandbox
                         v                         v                           v
              +--------------------+    +--------------------+       +--------------------+
              | Open Policy Agent  |    |  Keycloak (Auth)   |       | gVisor OpenSandbox |
              |    (Port 8181)     |    |    (Port 8080)     |       |   (Contained Run)  |
              +--------------------+    +--------------------+       +--------------------+
```

---

## 🚀 Quickstart: Running the Labs

### Method 1: Local Docker Stack (Recommended)

Build and run all services locally in seconds (self-contained, no external registries required):

```bash
docker compose up --build
```

Access the interactive portals:
- **Workshop Web Portal & Chat UI**: [http://localhost:8501](http://localhost:8501)
- **Runtime Shield Gateway API**: [http://localhost:5000](http://localhost:5000)
- **OPA Policy Engine**: [http://localhost:8181](http://localhost:8181)
- **Keycloak Auth**: [http://localhost:8080](http://localhost:8080)

---

### Method 2: Multi-Tenant Provisioning (For Workshop Instructors)

Spin up an isolated tenant workspace and container stack with custom port mappings for each attendee:

```bash
# Usage: ./provision_tenant.sh <attendee_name> <starting_port>
./provision_tenant.sh anika 10000
```

This creates a dedicated environment under `../tenants/tenant_anika` with dedicated ports:
- **Chat UI**: `http://localhost:10003`
- **Gateway API**: `http://localhost:10000`
- **OPA**: `http://localhost:10001`
- **Keycloak**: `http://localhost:10002`

---

### Method 3: Standalone Python (No Docker Required)

If you don't have Docker running, you can run all lab simulations and compliance drills directly with Python:

```bash
# Lab 3: Simulate HR Keycloak role downgrade & cache invalidation
python lab3_auth_drift/mock_webhook_trigger.py

# Lab 4: Simulate Admin approval console for high-risk scripts
python lab4_hitl_sandbox/mock_admin_console.py

# Lab 5: Inspect forensic audit logs and fraud scoring
python lab5_telemetry/view_telemetry.py

# Lab 6: Execute automated ISO 42001 verification & validation drills
python lab6_security_drills/run_security_drills.py
```

---

## 🧪 Workshop Labs Index

| Lab | Name | ISO/IEC 42001 Control | Objective |
| :--- | :--- | :--- | :--- |
| **Lab 1** | [Role-Based Access Control (RBAC)](lab1_rbac/README.md) | **A.9.4 & A.9.2** | Intercept unauthorized file queries using OPA policies based on user role (`user` vs `admin`). |
| **Lab 2** | [Prompt Injection & Threat Containment](lab2_prompt_injection/README.md) | **A.6.2.6** | Catch adversarial hidden prompt injections attempting to steal system configuration files via honeypot rules. |
| **Lab 3** | [Authorization Drift & Cache Defense](lab3_auth_drift/README.md) | **A.9.4 & A.9.2** | Prevent authorization drift by invalidating cached security permissions the moment an HR role change occurs. |
| **Lab 4** | [Human-in-the-Loop & OpenSandbox](lab4_hitl_sandbox/README.md) | **A.9.2 & A.6.2.6** | Pause dangerous tool calls (e.g. bash scripts) for administrator review and execute in an isolated container sandbox. |
| **Lab 5** | [Telemetry & Forensic Auditing](lab5_telemetry/README.md) | **A.6.2.8** | Review tamper-proof forensic audit trails with trace IDs, fraud scores, and intercepted action records. |
| **Lab 6** | [Automated Compliance Drills](lab6_security_drills/README.md) | **A.6.2.4 & 10.1** | Run automated red-team security assertions to programmatically verify all security boundaries hold firm. |

---

## 📁 Repository Structure

```
ISO-42001-Workshop-Labs/
├── docker-compose.yml              # Local container orchestration
├── provision_tenant.sh             # Multi-tenant workspace provisioner
├── README.md                       # Workshop overview & quickstart
├── gateway/                        # Self-contained Runtime Shield Gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── chat_ui/                        # Web portal & interactive attendee UI
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── lab1_rbac/                      # RBAC policies & mock executive data
├── lab2_prompt_injection/          # Honeypot rules & malicious PDF sample
├── lab3_auth_drift/                # Clearance filter & webhook trigger script
├── lab4_hitl_sandbox/              # Admin approval console & sandbox configs
├── lab5_telemetry/                 # Audit trail viewer & sample forensic logs
└── lab6_security_drills/           # Automated compliance test suite
```
