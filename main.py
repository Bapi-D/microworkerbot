import cloudscraper, time, random, os, threading
from flask import Flask
from bs4 import BeautifulSoup

app = Flask(__name__)
@app.route('/')
def home(): 
    return "Bot is Active. Searching for any job links...", 200

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8294342276:AAG9JabIfGmJLRNNrjzbN3efaQOKa09tGbI"
CHAT_ID = "-1003486051893"
COOKIE_VAL = os.environ.get("MY_COOKIE", "default")

def scrape_jobs():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    scraper.cookies.set("PHPSESSID", COOKIE_VAL, domain="www.microworkers.com")
    
    last_seen_jobs = set()
    print("Smarter Link-Scraper Started...")

    while True:
        try:
            url = "https://www.microworkers.com/jobs.php"
            response = scraper.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # We find the links FIRST
                job_links = soup.find_all('a', href=lambda x: x and '/jobs/apply/' in x)
                
                # Now we print the status
                print(f"I see {len(response.text)} characters. Found {len(job_links)} jobs.")
                
                if not job_links:
                    print("No job links found. Your cookie might be expired.")

                for link in job_links:
                    href = link['href']
                    job_id = href.split('/')[-1]
                    job_name = link.get_text(strip=True) or "Micro Task"
                    
                    # CHANGE "PASTE_OLD_ID_HERE" to an actual ID if you want to test
                    if job_id not in last_seen_jobs:
                        msg = f"🔔 **NEW TASK DETECTED**\n\n📝 {job_name}\n🆔 ID: {job_id}\n🔗 [Apply on MW]({url})"
                        
                        # Send to Telegram
                        scraper.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                    params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                        
                        last_seen_jobs.add(job_id)
                        print(f"Alert sent for Job: {job_id}")

            # Safety: Keep set size small
            if len(last_seen_jobs) > 500: last_seen_jobs.clear()
            
            # FIXED: Wait between 3 to 5 minutes (180 to 300 seconds)
            time.sleep(random.randint(5, 10))

        except Exception as e:
            print(f"Scrape Error: {e}")
            time.sleep(60) # Wait 1 minute before retrying on error

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    scrape_jobs()
