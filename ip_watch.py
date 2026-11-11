#!/usr/bin/env python3
"""Watch this machine's IP addresses and post to Slack whenever they change.

Only uses the Python standard library (no pip install needed).
Config comes from environment variables (systemd loads them from .env):

  SLACK_WEBHOOK_URL   required, Slack Incoming Webhook URL
  CHECK_INTERVAL      seconds between checks (default 30)
  IGNORE_IFACES       comma-separated interface name prefixes to ignore
                      (default: lo,docker,br-,veth,virbr,vmnet,tun,tailscale,zt)
  INCLUDE_IPV6        1/0, include global IPv6 addresses (default 1)
  STATE_FILE          where the last-sent IPs are stored
                      (default ~/.local/state/ip_watch/last_ips.json)
  SEND_ON_START       1/0, always send once when the service starts (default 1)
  DEVICE_NAME         name shown in Slack (default: system hostname)
"""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "30"))
IGNORE_IFACES = [p.strip() for p in os.environ.get(
    "IGNORE_IFACES", "lo,docker,br-,veth,virbr,vmnet,tun,tailscale,zt").split(",") if p.strip()]
INCLUDE_IPV6 = os.environ.get("INCLUDE_IPV6", "1") == "1"
SEND_ON_START = os.environ.get("SEND_ON_START", "1") == "1"
STATE_FILE = Path(os.environ.get(
    "STATE_FILE", Path.home() / ".local/state/ip_watch/last_ips.json")).expanduser()

HOSTNAME = os.environ.get("DEVICE_NAME", "").strip() or socket.gethostname()


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def get_ips():
    """Return {ifname: sorted list of addresses} for relevant interfaces."""
    out = subprocess.check_output(["ip", "-j", "addr", "show"], text=True)
    result = {}
    for iface in json.loads(out):
        name = iface.get("ifname", "")
        if any(name.startswith(p) for p in IGNORE_IFACES):
            continue
        addrs = []
        for a in iface.get("addr_info", []):
            if a.get("scope") != "global":
                continue  # skip link-local / loopback
            if a.get("family") == "inet":
                addrs.append(a["local"])
            elif a.get("family") == "inet6" and INCLUDE_IPV6:
                # IPv6 privacy (temporary) addresses rotate often -> skip to avoid spam
                if a.get("temporary") or a.get("deprecated"):
                    continue
                addrs.append(a["local"])
        if addrs:
            result[name] = sorted(addrs)
    return result


def format_ips(ips):
    if not ips:
        return "_(no IP address)_"
    lines = []
    for name, addrs in sorted(ips.items()):
        for addr in addrs:
            kind = "IPv6" if ":" in addr else "IPv4"
            lines.append(f"• `{name}` {kind}: `{addr}`")
    return "\n".join(lines)


def send_to_slack(title, old, new):
    text = f"{title}\n*Hostname:* `{HOSTNAME}`\n*Time:* {datetime.now():%Y-%m-%d %H:%M:%S}\n"
    text += f"*Current:*\n{format_ips(new)}"
    if old is not None:
        text += f"\n*Previous:*\n{format_ips(old)}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(WEBHOOK_URL, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Slack returned HTTP {resp.status}")


def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_state(ips):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(ips, indent=2))


def main():
    if not WEBHOOK_URL:
        log("ERROR: SLACK_WEBHOOK_URL is not set (check .env)")
        sys.exit(1)

    last_sent = load_state()
    first_round = True
    log(f"Started. interval={CHECK_INTERVAL}s, last known={last_sent}")

    while True:
        try:
            current = get_ips()
            if current != last_sent or (first_round and SEND_ON_START):
                if first_round and current == last_sent:
                    title = "🟢 *Machine online* (IP unchanged)"
                elif last_sent is None:
                    title = "🟢 *Machine online*"
                else:
                    title = "🔄 *IP address changed!*"
                send_to_slack(title, last_sent if current != last_sent else None, current)
                log(f"Sent to Slack: {current}")
                last_sent = current
                save_state(current)  # only saved after a successful send -> retries on failure
            first_round = False
        except Exception as e:
            # Network may be down right now; we'll retry on the next round
            log(f"Error: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    if "--once" in sys.argv:  # quick manual test
        print(format_ips(get_ips()))
        if "--send" in sys.argv:
            send_to_slack("🧪 *Test message*", None, get_ips())
            print("sent")
    else:
        main()
