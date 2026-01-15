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
    # 2026 Stealth Config: Mimic a modern Windows Chrome browser perfectly
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # Crucial: Apply the cookie to the scraper session
    scraper.cookies.set("PHPSESSID", COOKIE_VAL, domain="www.microworkers.com")
    
    last_seen_jobs = set()
    print("Anti-Cloudflare Deep Scan Started...")

    while True:
        try:
            # We add a common 'Referer' header so it looks like we clicked a link
            headers = {
                'Referer': 'https://www.google.com/',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            url = "https://www.microworkers.com/jobs.php"
            response = scraper.get(url, headers=headers, timeout=30)
            
            # DEBUG: If the size is small, we know we are blocked
            char_count = len(response.text)
            
            if char_count < 15000:
                print(f"⚠️ Blocked by Cloudflare (Size: {char_count}). Trying to recover...")
                # Small trick: visit the home page first to get a clearance cookie
                scraper.get("https://www.microworkers.com/")
                time.sleep(10)
                continue 

            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for ANY link that has 'apply' in it
            job_links = soup.find_all('a', href=lambda x: x and ('jobs/apply' in x or 'apply.php' in x))
            
            print(f"✅ Success! Page Size: {char_count}. Found {len(job_links)} jobs.")

            for link in job_links:
                href = link['href']
                job_id = href.split('/')[-1].split('?')[-1].replace('id=', '')
                job_name = link.get_text(strip=True) or "Micro Task"
                
                if job_id not in last_seen_jobs:
                    msg = f"🚀 **NEW JOB**\n\n📝 {job_name}\n🆔 ID: {job_id}\n🔗 [Apply]({url})"
                    scraper.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                    last_seen_jobs.add(job_id)

            if len(last_seen_jobs) > 500: last_seen_jobs.clear()
            
            # Wait 4-7 minutes to avoid "bot-like" patterns
            time.sleep(random.randint(10, 70))

        except Exception as e:
            print(f"Scrape Error: {e}")
            time.sleep(120)
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    scrape_jobs()
