# Lab 4: Human-in-the-Loop & OpenSandbox

## Scenario
Mira, the AI assistant, is extremely capable. Sometimes she needs to run bash scripts to fix IT issues. However, letting an AI run scripts directly on the host server is highly dangerous! To protect the infrastructure, the Runtime Shield enforces two controls: **Human-in-the-Loop (HITL) approval** and **Isolated Execution (OpenSandbox)**.

## Objective
Demonstrate how the Runtime Shield enforces ISO A.9.2 (Human oversight) and A.6.2.6 (Secure execution) by pausing risky commands for approval and running them in a sandboxed container.

## Steps
1. **The Setup**: Log in to the Chat UI. Open a second browser tab to the Admin Approval Dashboard (or use the mock python script provided).
2. **Execute Prompt**: Ask the AI: *"Please fix the network configuration by running the update_network_daemon script."*
3. **The Pause**: The AI will attempt to execute a ash_command tool. The Runtime Shield detects this is a high-risk tool and returns a PENDING state. In your Chat UI, you will see *"Action pending administrator approval."*
4. **The Approval**: Switch to the Admin Dashboard and click **APPROVE**.
5. **The Execution**: Once approved, the Shield does NOT run the script on the host. Instead, it spins up an isolated gVisor OpenSandbox container, runs the script inside it, and securely streams the output back to the chat.

## Under the Hood
Look at mock_scripts/update_network_daemon.sh to see the script the AI is trying to run. Check sandbox_config.yaml to see how the Gateway routes approved commands to the gVisor container instead of the local machine shell.
