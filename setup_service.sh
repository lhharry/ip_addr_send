#!/bin/bash
# Installs ip_watch.py as a systemd service that runs on boot and keeps
# watching for IP changes.   Usage: bash setup_service.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="ip_watch"
CURRENT_USER="$(whoami)"
CURRENT_HOME="$HOME"

if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "!! $SCRIPT_DIR/.env not found. Run: cp .env.example .env  and fill in SLACK_WEBHOOK_URL"
    exit 1
fi

echo "==> Creating systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=Watch IP address changes and notify Slack
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=${SCRIPT_DIR}/.env
Environment=HOME=${CURRENT_HOME}
ExecStart=/usr/bin/python3 -u ${SCRIPT_DIR}/ip_watch.py
User=${CURRENT_USER}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service
sudo systemctl restart ${SERVICE_NAME}.service

echo ""
echo "==> Done! Service status:"
sudo systemctl status ${SERVICE_NAME}.service --no-pager
