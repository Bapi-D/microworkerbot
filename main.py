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
    # Use a real-looking browser header
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    scraper.cookies.set("PHPSESSID", COOKIE_VAL, domain="www.microworkers.com")
    
    last_seen_jobs = set()
    print("Deep-Scan 2026 Logic Started...")

    while True:
        try:
            url = "https://www.microworkers.com/jobs.php"
            response = scraper.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # SEARCH #1: Look for the specific 'jobs/apply' links in all forms
                found_links = []
                all_links = soup.find_all('a', href=True)
                
                for l in all_links:
                    href = l['href']
                    # Look for the job pattern like 'jobs/apply/12345' or '?id=12345'
                    if '/jobs/apply/' in href or 'apply.php?id=' in href:
                        found_links.append(l)

                print(f"Status: Page Loaded. {len(all_links)} total links on page. Found {len(found_links)} potential jobs.")

                for link in found_links:
                    href = link['href']
                    # Clean the ID from the URL (removes extra text)
                    job_id = href.split('/')[-1].split('?')[0].replace('apply.phpid=', '')
                    job_name = link.get_text(strip=True) or "New Micro Task"
                    
                    if job_id and job_id not in last_seen_jobs:
                        msg = f"🚀 **NEW JOB ALERT**\n\n📝 {job_name}\n🆔 ID: {job_id}\n🔗 [Apply Here]({url})"
                        
                        # Send alert
                        scraper.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                    params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                        
                        last_seen_jobs.add(job_id)
                        print(f"Sent Alert for: {job_id}")

                if not found_links:
                    print("Debug: No jobs found. They might be in a 'Hire Group' or hidden by a script.")

            else:
                print(f"Login failed? Status code: {response.status_code}")

            # Stay safe: check every 3-5 mins
            time.sleep(random.randint(10, 70))

        except Exception as e:
            print(f"Bot Error: {e}")
            time.sleep(60)
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    scrape_jobs()
