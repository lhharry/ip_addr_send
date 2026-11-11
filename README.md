# ip_addr_send (ip-watch branch)

Watches this Ubuntu machine's IP addresses (DHCP) and posts to Slack whenever they change.
Like the `main` branch, but runs continuously instead of only once at boot.

Install on a new PC:

    git clone -b ip-watch https://github.com/lhharry/ip_addr_send
    cd ip_addr_send

## Setup
1. Create a Slack Incoming Webhook for your channel (api.slack.com/apps → Incoming Webhooks).
2. `cp .env.example .env` and set `SLACK_WEBHOOK_URL`.
3. Test: `set -a; . ./.env; set +a; python3 ip_watch.py --once --send`
4. Install: `bash setup_service.sh`

## Commands
    systemctl status ip_watch
    journalctl -u ip_watch -f
    sudo systemctl disable --now ip_watch
