#!/bin/bash
# provision_tenant.sh
# Automates the creation of isolated workshop environments for attendees.

if [ -z "$1" ]; then
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

# 2. Copy the Master Labs into the tenant's workspace
echo "[*] Cloning master labs into tenant workspace..."
cp -r ./lab1_rbac "$TENANT_DIR/"
cp -r ./lab2_prompt_injection "$TENANT_DIR/"
cp -r ./lab3_auth_drift "$TENANT_DIR/"
cp -r ./lab4_hitl_sandbox "$TENANT_DIR/"
cp -r ./lab5_telemetry "$TENANT_DIR/"
cp -r ./lab6_security_drills "$TENANT_DIR/"

# 3. Configure the Docker Compose file with unique ports
echo "[*] Configuring network boundaries and ports..."
cat docker-compose.yml | \
sed "s/\{TENANT_ID}/$ATTENDEE/g" | \
sed "s/\	enant_gateway/gateway_$ATTENDEE/g" | \
sed "s/\	enant_opa/opa_$ATTENDEE/g" | \
sed "s/\	enant_keycloak/keycloak_$ATTENDEE/g" | \
sed "s/\	enant_ui/ui_$ATTENDEE/g" | \
sed "s/\{GATEWAY_PORT}/$((PORT_BASE + 0))/g" | \
sed "s/\{OPA_PORT}/$((PORT_BASE + 1))/g" | \
sed "s/\{KC_PORT}/$((PORT_BASE + 2))/g" | \
sed "s/\{UI_PORT}/$((PORT_BASE + 3))/g" > "$TENANT_DIR/docker-compose.yml"

# 4. Spin up the tenant
echo "[*] Booting isolated container stack..."
# cd "$TENANT_DIR" && docker-compose up -d

echo "=================================================="
echo " ? Provisioning Complete!"
echo " Attendee UI URL:   http://localhost:$((PORT_BASE + 3))"
echo " Gateway API URL:   http://localhost:$((PORT_BASE + 0))"
echo " Keycloak Admin:    http://localhost:$((PORT_BASE + 2))"
echo "=================================================="
