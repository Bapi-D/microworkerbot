import cloudscraper
import time
import random
import os
import threading
from flask import Flask
from bs4 import BeautifulSoup

# --- 1. KOYEB HEALTH CHECK ---
app = Flask(__name__)
@app.route('/')
def home(): return "Pro Scraper is Active", 200

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

# --- 2. THE CLOUDFLARE BYPASS SCRAPER ---
TOKEN = "8294342276:AAG9JabIfGmJLRNNrjzbN3efaQOKa09tGbI"
CHAT_ID = "-1003486051893"
COOKIE_VAL = "4q0kejkv3nsgen87e1uolh2h9l"

def scrape_jobs():
    # Create a scraper instance that bypasses Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # Manually set your cookie so you stay logged in
    scraper.cookies.set("PHPSESSID", COOKIE_VAL, domain="www.microworkers.com")
    
    last_seen_jobs = set()
    print("Locked in and Cloudflare-ready. Starting scraper...")

    while True:
        try:
            # Scrape the Job Area
            url = "https://www.microworkers.com/jobs.php"
            response = scraper.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find all jobs in the list (MW usually uses 'job_item' classes)
                job_items = soup.select('.job_item') 
                
                for job in job_items:
                    job_id = job.get('id')
                    # Find the text of the job title
                    title_elem = job.select_one('.job_title')
                    if title_elem and job_id not in last_seen_jobs:
                        title_text = title_elem.get_text(strip=True)
                        msg = f"🔔 **NEW JOB DETECTED**\n\n📌 {title_text}\n🆔 {job_id}\n🔗 [Open Job]({url})"
                        
                        # Send alert via Telegram
                        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                     params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                        
                        last_seen_jobs.add(job_id)

            # Prevent memory overflow: only keep 100 most recent IDs
            if len(last_seen_jobs) > 100: last_seen_jobs.clear()

            # IMPORTANT: Wait randomly to look human
            time.sleep(random.randint(50, 200)) # 3 to 5 minutes

        except Exception as e:
            print(f"Bypass Error: {e}")
            time.sleep(600) # Wait 10 minutes if blocked

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    scrape_jobs()
