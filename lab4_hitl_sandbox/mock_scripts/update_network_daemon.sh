#!/bin/bash
# Mock script to update network daemons.
# Running this on a host machine maliciously could destroy networking!

echo "[INFO] Initializing network daemon update..."
sleep 1
echo "[INFO] Reconfiguring routing tables..."
sleep 1
echo "[SUCCESS] Network daemon updated successfully inside isolated sandbox."
# Try something malicious to prove the sandbox works
if ping -c 1 8.8.8.8 &> /dev/null
then
  echo "[WARNING] Network access is active! (Sandbox failed)"
else
  echo "[SECURE] External network is unreachable. (Sandbox is working!)"
fi
