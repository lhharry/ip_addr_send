#!/bin/bash
# Run this script ON the edge device (Jetson, Raspberry Pi, etc.)
# Sets up send_ip.py as a systemd service that runs on every boot
#
# Usage: bash setup_service.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/send_ip.py"
SERVICE_NAME="send_ip"
CURRENT_USER="$(whoami)"

# --- Install dependency ---
echo "==> Installing requests..."
pip3 install requests --quiet || sudo pip3 install requests --quiet

# --- Create systemd service ---
echo "==> Creating systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=Send IP address on boot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
EnvironmentFile=-${SCRIPT_DIR}/.env
ExecStart=/usr/bin/python3 ${SCRIPT_PATH}
User=${CURRENT_USER}
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# --- Enable and start ---
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service
sudo systemctl start ${SERVICE_NAME}.service

echo ""
echo "==> Done! Service status:"
sudo systemctl status ${SERVICE_NAME}.service --no-pager
