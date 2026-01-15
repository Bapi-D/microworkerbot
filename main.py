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
    print("Smarter 2026 Link-Scraper Started...")

    while True:
        try:
            url = "https://www.microworkers.com/jobs.php"
            response = scraper.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 2026 UPDATE: Try 3 different ways to find job links
                # 1. Search for new 'job_title' class
                # 2. Search for the 'dot' links inside the job table
                # 3. Search for any href containing 'jobs/apply'
                links = soup.select('a.job_title') or \
                        soup.select('td a[href*="/jobs/apply/"]') or \
                        soup.find_all('a', href=lambda x: x and '/jobs/apply/' in x)
                
                print(f"Page loaded: {len(response.text)} chars. Found {len(links)} jobs.")

                for link in links:
                    href = link.get('href', '')
                    job_id = href.split('/')[-1].split('?')[0] # Clean ID
                    job_name = link.get_text(strip=True) or "Micro Task"
                    
                    if job_id and job_id not in last_seen_jobs:
                        msg = f"🔔 **NEW TASK**\n\n📝 {job_name}\n🆔 ID: {job_id}\n🔗 [Open Jobs Page]({url})"
                        
                        # Send to Telegram
                        scraper.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                    params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                        
                        last_seen_jobs.add(job_id)
                        print(f"Alert sent: {job_id}")

                if not links:
                    print("Detection Failed. I see the page but can't find the 'Apply' links.")

            else:
                print(f"Site Error: {response.status_code}")

            if len(last_seen_jobs) > 500: last_seen_jobs.clear()
            time.sleep(random.randint(10, 70))

        except Exception as e:
            print(f"Scrape Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    scrape_jobs()
