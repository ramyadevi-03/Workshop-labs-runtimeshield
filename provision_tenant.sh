#!/bin/bash
# provision_tenant.sh
# Automates the creation of isolated workshop environments for attendees.

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: ./provision_tenant.sh <attendee_name> <starting_port_block>"
  echo "Example: ./provision_tenant.sh anika 10000"
  exit 1
fi

ATTENDEE="$1"
PORT_BASE="$2"

echo "=================================================="
echo " Provisioning Workshop Environment for: $ATTENDEE"
echo "=================================================="

# 1. Create a dedicated workspace for the attendee
TENANT_DIR="../tenants/tenant_$ATTENDEE"
mkdir -p "$TENANT_DIR"

# 2. Copy the Master Labs and Service definitions into the tenant's workspace
echo "[*] Cloning master labs into tenant workspace..."
cp -r ./lab1_rbac "$TENANT_DIR/"
cp -r ./lab2_prompt_injection "$TENANT_DIR/"
cp -r ./lab3_auth_drift "$TENANT_DIR/"
cp -r ./lab4_hitl_sandbox "$TENANT_DIR/"
cp -r ./lab5_telemetry "$TENANT_DIR/"
cp -r ./lab6_security_drills "$TENANT_DIR/"
cp -r ./gateway "$TENANT_DIR/"
cp -r ./chat_ui "$TENANT_DIR/"
cp docker-compose.yml "$TENANT_DIR/"

# 3. Configure the environment variables with unique ports
echo "[*] Configuring network boundaries and ports..."
cat <<EOF > "$TENANT_DIR/.env"
TENANT_ID=$ATTENDEE
GATEWAY_PORT=$((PORT_BASE + 0))
OPA_PORT=$((PORT_BASE + 1))
KC_PORT=$((PORT_BASE + 2))
UI_PORT=$((PORT_BASE + 3))
EOF

# 4. Spin up the tenant
echo "[*] Booting isolated container stack..."
# cd "$TENANT_DIR" && docker compose up -d --build

echo "=================================================="
echo " ✅ Provisioning Complete!"
echo " Attendee UI URL:   http://localhost:$((PORT_BASE + 3))"
echo " Gateway API URL:   http://localhost:$((PORT_BASE + 0))"
echo " Keycloak Admin:    http://localhost:$((PORT_BASE + 2))"
echo " OPA Policy Engine: http://localhost:$((PORT_BASE + 1))"
echo "=================================================="
