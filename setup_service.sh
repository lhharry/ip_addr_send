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
VENV_DIR="$SCRIPT_DIR/.venv"

# --- Ensure python3-venv is available (Debian/Ubuntu/Raspberry Pi OS/JetPack) ---
if ! python3 -m venv --help &>/dev/null; then
    echo "==> Installing python3-venv..."
    sudo apt-get install -y python3-venv
fi

# --- Create virtual environment and install dependency ---
echo "==> Creating virtual environment..."
python3 -m venv "$VENV_DIR"

echo "==> Installing requests..."
"$VENV_DIR/bin/pip" install requests --quiet

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
ExecStart=${VENV_DIR}/bin/python ${SCRIPT_PATH}
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
