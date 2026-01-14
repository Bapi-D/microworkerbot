import requests
import time
import threading
from flask import Flask
import os

# --- 1. WEB SERVER FOR KOYEB HEALTH CHECKS ---
app = Flask(__name__)

@app.route('/')
def home():
    # When Koyeb visits your URL, it gets this message and knows the bot is alive.
    return "Microworkers Bot is Online 24/7!", 200

def run_flask():
    # We change this to 8000 to match Koyeb's default health check port
    port = int(os.environ.get("PORT", 8000))
    # Using '0.0.0.0' allows the cloud server to see the app
    app.run(host='0.0.0.0', port=port)

# --- 2. THE MONITORING SYSTEM ---
TOKEN = "8294342276:AAG9JabIfGmJLRNNrjzbN3efaQOKa09tGbI"
CHAT_ID = "-1003486051893"
COOKIE = "PHPSESSID=lvpc839hmvcl1hf245nnnpb7b0"

def send_alert(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Telegram alert failed: {e}")

def monitor():
    last_job = ""
    print("Monitor started... Checking Microworkers every 2 seconds.")
    while True:
        try:
            headers = {
                "Cookie": COOKIE, 
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            }
            r = requests.get("https://www.microworkers.com/jobs.php", headers=headers, timeout=15)
            
            if "Job ID:" in r.text:
                # Extracts the job number from the page
                current_job = r.text.split("Job ID:")[1][:15].strip().split()[0]
                
                if current_job != last_job:
                    send_alert(f"🚀 New Job Detected! ID: {current_job}\nhttps://www.microworkers.com/jobs.php")
                    last_job = current_job
        except Exception as e:
            print(f"Check failed: {e}")
            
        time.sleep(2) # Wait 2 seconds

if __name__ == "__main__":
    # Start the "I am alive" web server in a separate thread
    threading.Thread(target=run_flask).start()
    # Start the monitoring loop
    monitor()
