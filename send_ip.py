import requests
import subprocess
import time
import os

# --- CONFIGURATION ---
# Set the SLACK_WEBHOOK_URL environment variable, or paste it in a .env file
WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')

def get_ip():
    # Gets the local IP address
    cmd = "hostname -I | cut -d' ' -f1"
    return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

def send_to_slack(ip):
    data = {
        "text": f"🚀 **Jetson Online!**\n**Hostname:** `aries`\n**Local IP:** `{ip}`",
        "username": "Jetson Orin Nano"
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("Message sent to Slack!")
    except Exception as e:
        print(f"Error: {e}")

# Wait 15 seconds for WiFi to fully stabilize
time.sleep(15)
current_ip = get_ip()
if current_ip:
    send_to_slack(current_ip)