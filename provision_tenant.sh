
#!/bin/bash
# provision_tenant.sh
# Automates the creation of isolated workshop environments for attendees.

set -euo pipefail

if [ -z "${1:-}" ] || [ -z "${2:-}" ]; then
  echo "Usage: ./provision_tenant.sh <attendee_name> <starting_port_block>"
  echo "Example: ./provision_tenant.sh anika 10000"
  exit 1
fi

ATTENDEE="$1"
PORT_BASE="$2"

# Validate attendee name and port number
if [[ ! "$ATTENDEE" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "ERROR: Invalid attendee name." >&2
  exit 1
fi

if [[ ! "$PORT_BASE" =~ ^[0-9]+$ ]] ||
   (( 10#$PORT_BASE < 1 || 10#$PORT_BASE > 65532 )); then
  echo "ERROR: Invalid starting port block." >&2
  exit 1
fi

PORT_BASE=$((10#$PORT_BASE))

echo "=================================================="
echo " Provisioning Workshop Environment for: $ATTENDEE"
echo "=================================================="

# 1. Create a dedicated workspace for the attendee
TENANT_DIR="../tenants/tenant_$ATTENDEE"
mkdir -p "$TENANT_DIR"

# 2. Copy the Master Labs and Service definitions
echo "[*] Cloning master labs into tenant workspace..."

cp -r ./lab1_rbac "$TENANT_DIR/"
cp -r ./lab2_prompt_injection "$TENANT_DIR/"
cp -r ./lab3_auth_drift "$TENANT_DIR/"
cp -r ./lab4_hitl_sandbox "$TENANT_DIR/"
cp -r ./lab5_telemetry "$TENANT_DIR/"
cp -r ./lab6_security_drills "$TENANT_DIR/"

# Lab 7 - Agent-to-Agent Security
cp -r ./lab7_a2a "$TENANT_DIR/"

# Exclude instructor-only grading files
rm -rf "$TENANT_DIR/lab7_a2a/grader"

# Copy shared services
cp -r ./gateway "$TENANT_DIR/"
cp -r ./chat_ui "$TENANT_DIR/"
cp docker-compose.yml "$TENANT_DIR/"

# 3. Configure environment variables and secure tenant secret
echo "[*] Configuring network boundaries and ports..."

# Generate a cryptographically secure 256-bit secret.
# If both generators fail, abort provisioning.
if ! LAB7_SECRET=$(
  python3 -c 'import secrets; print(secrets.token_hex(32))' 2>/dev/null ||
  openssl rand -hex 32 2>/dev/null
); then
  echo "ERROR: Secure LAB7_AGENT_SECRET generation failed." >&2
  exit 1
fi

# Ensure the secret is valid and not empty
if [[ ! "$LAB7_SECRET" =~ ^[0-9a-fA-F]{64}$ ]]; then
  echo "ERROR: Invalid or empty LAB7_AGENT_SECRET." >&2
  exit 1
fi

# Restrict permissions for newly created files
umask 077

cat <<EOF > "$TENANT_DIR/.env"
TENANT_ID=$ATTENDEE
GATEWAY_PORT=$((PORT_BASE + 0))
OPA_PORT=$((PORT_BASE + 1))
KC_PORT=$((PORT_BASE + 2))
UI_PORT=$((PORT_BASE + 3))
LAB7_AGENT_SECRET=$LAB7_SECRET
EOF

echo "[*] Secure tenant configuration created."

# 4. Spin up the tenant
echo "[*] Docker startup is currently disabled."

# Uncomment the following line when ready to launch:
# (cd "$TENANT_DIR" && docker compose up -d --build)

echo "=================================================="
echo " Provisioning Configuration Complete!"
echo "=================================================="
echo " Attendee UI URL:   http://localhost:$((PORT_BASE + 3))"
echo " Gateway API URL:   http://localhost:$((PORT_BASE + 0))"
echo " Keycloak Admin:    http://localhost:$((PORT_BASE + 2))"
echo " OPA Policy Engine: http://localhost:$((PORT_BASE + 1))"
echo "=================================================="
echo " Note: URLs become available after Docker starts."
