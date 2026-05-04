import requests
import subprocess
import time
import os

# --- CONFIGURATION ---
# Set the SLACK_WEBHOOK_URL environment variable, or paste it in a .env file
WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')

def get_ipv4():
    cmd = "hostname -I | cut -d' ' -f1"
    try:
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    except Exception:
        return None

def get_ipv6():
    cmd = "ip -6 addr show scope global | grep -oP '(?<=inet6 )[\da-f:]+' | head -1"
    try:
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    except Exception:
        return None

def send_to_slack(ipv4, ipv6):
    lines = ["🚀 *Jetson Online!*", "*Hostname:* `aries`"]
    if ipv4:
        lines.append(f"*IPv4:* `{ipv4}`")
    if ipv6:
        lines.append(f"*IPv6:* `{ipv6}`")
    data = {
        "text": "\n".join(lines),
        "username": "Jetson Orin Nano"
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 200:
            print("Message sent to Slack!")
    except Exception as e:
        print(f"Error: {e}")

# Wait 15 seconds for WiFi to fully stabilize
time.sleep(15)
ipv4 = get_ipv4()
ipv6 = get_ipv6()
if ipv4 or ipv6:
    send_to_slack(ipv4, ipv6)