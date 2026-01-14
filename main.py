import requests
import time
import threading
from flask import Flask
import os
import random

# --- 1. WEB SERVER FOR KOYEB HEALTH CHECKS ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Microworkers Bot is Online & Running Safely!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

# --- 2. THE MONITORING SYSTEM ---
TOKEN = "8294342276:AAG9JabIfGmJLRNNrjzbN3efaQOKa09tGbI"
CHAT_ID = "-1003486051893"
COOKIE = "PHPSESSID=lvpc839hmvcl1hf245nnnpb7b0"

# List of different browser identities to mimic different devices
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

def send_alert(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Telegram alert failed: {e}")

def monitor():
    last_job = ""
    print("Safe Monitor started... Randomized checking enabled.")
    while True:
        try:
            # Pick a random browser identity for each request
            headers = {
                "Cookie": COOKIE, 
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9"
            }
            
            r = requests.get("https://www.microworkers.com/jobs.php", headers=headers, timeout=20)
            
            if "Job ID:" in r.text:
                current_job = r.text.split("Job ID:")[1][:15].strip().split()[0]
                
                if current_job != last_job:
                    send_alert(f"🚀 New Job! ID: {current_job}\nhttps://www.microworkers.com/jobs.php")
                    last_job = current_job
            
            # 🛑 THE SAFETY FIX: 
            # Instead of exactly 30s, we wait between 90 and 180 seconds (1.5 to 3 minutes).
            # This variation prevents the "5-minute restriction."
            wait_time = random.randint(90, 180)
            print(f"Checked successfully. Next check in {wait_time} seconds...")
            time.sleep(wait_time)

        except Exception as e:
            print(f"Check failed: {e}")
            # If the site blocks us or fails, wait 5 minutes before trying again
            time.sleep(300) 

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    monitor()
