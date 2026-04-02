# ip_addr_send

Automatically sends your edge device's local IP address to a Slack channel on boot. Useful for headless devices (Jetson Nano, Raspberry Pi, etc.) where you need to know the IP without a monitor.

## How it works

On startup, the script waits 15 seconds for WiFi to stabilize, fetches the local IP, and posts it to a Slack channel via an Incoming Webhook.

## Setup

### 1. Create a Slack Webhook

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Under **Incoming Webhooks**, toggle it ON
3. Click **Add New Webhook to Workspace**, pick a channel, and copy the URL

### 2. Configure the script

Copy `.env.example` to `.env` and paste your webhook URL:

```bash
cp .env.example .env
```

Then edit `.env`:

```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

The `.env` file is gitignored and will never be committed.

### 3. Deploy on the device

Copy the files onto the device, then run:

```bash
bash setup_service.sh
```

This registers `send_ip.py` as a systemd service that runs automatically on every boot after the network is up.

## Useful commands

```bash
sudo systemctl status send_ip    # check if it ran
sudo systemctl disable send_ip   # remove from boot
journalctl -u send_ip            # view logs
```

## Requirements

- Python 3
- `requests` library (installed automatically by `setup_service.sh`)
