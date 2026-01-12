"""
MICROWORKERS TELEGRAM BOT - OFFICIAL API VERSION
Uses Microworkers Official API to fetch tasks
"""

import requests
import time
from datetime import datetime
import json
import os

# ===== YOUR SETTINGS =====
BOT_TOKEN = "8294342276:AAG9JabIfGmJLRNNrjzbN3efaQOKa09tGbI"
CHANNEL_ID = "-1003486051893"
MICROWORKERS_API_KEY = "7e922fb6207229efe7b4590897dab8f3cabe5203ceb4a4e76d89864959716c59"
CHECK_EVERY_SECONDS = 3  # Check every 3 seconds

# ===== Microworkers API Class =====
class MW_API:
    def __init__(self, api_key, api_url='https://api.microworkers.com'):
        self.api_key = api_key
        self.api_url = api_url

    def do_request(self, method='', action='', params={}, files={}):
        method = method.lower()
        if method not in ['get', 'put', 'post', 'delete']:
            raise Exception('Method: "' + method + '" is not supported')

        headers = {'MicroworkersApiKey': self.api_key}

        if method == 'get':
            r = requests.get(self.api_url + action, params=params, headers=headers)
        if method == 'put':
            r = requests.put(self.api_url + action, data=params, headers=headers)
        if method == 'post':
            r = requests.post(self.api_url + action, files=files, data=params, headers=headers)
        if method == 'delete':
            r = requests.delete(self.api_url + action, data=params, headers=headers)

        if r.status_code == requests.codes.ok or r.status_code == requests.codes.created:
            try:
                value = r.json()
                return {'type': 'json', 'value': value}
            except ValueError as e:
                return {'type': 'body', 'value': r.content}

        try:
            r.raise_for_status()
        except Exception as e:
            return {'type': 'error', 'value': e}

# ===== Bot Functions =====
sent_tasks_file = "sent_tasks.txt"

def load_sent_tasks():
    """Load list of tasks we already sent"""
    if os.path.exists(sent_tasks_file):
        with open(sent_tasks_file, 'r') as f:
            return set(f.read().splitlines())
    return set()

def save_task_id(task_id):
    """Remember that we sent this task"""
    with open(sent_tasks_file, 'a') as f:
        f.write(f"{task_id}\n")

def send_telegram_message(message):
    """Send message to Telegram channel"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def get_available_campaigns(api):
    """Get available campaigns/tasks from Microworkers API"""
    try:
        print("🔍 Fetching available tasks from Worker API...")
        
        all_tasks = []
        
        # Get Basic Campaign tasks (worker endpoint)
        print("  📋 Checking Basic Campaign tasks...")
        result_b = api.do_request('get', '/worker/b_tasks')
        
        if result_b['type'] == 'json':
            data = result_b['value']
            if data.get('status') == 'SUCCESS':
                tasks_b = data.get('tasks', [])
                print(f"  ✅ Found {len(tasks_b)} Basic Campaign tasks")
                all_tasks.extend(tasks_b)
        
        # Get Hire Group tasks
        print("  📋 Checking Hire Group tasks...")
        result_hg = api.do_request('get', '/worker/hg_tasks')
        
        if result_hg['type'] == 'json':
            data = result_hg['value']
            if data.get('status') == 'SUCCESS':
                tasks_hg = data.get('tasks', [])
                print(f"  ✅ Found {len(tasks_hg)} Hire Group tasks")
                all_tasks.extend(tasks_hg)
        
        if all_tasks:
            print(f"📊 Total tasks found: {len(all_tasks)}")
        else:
            print("ℹ️  No tasks available right now")
        
        return all_tasks
        
    except Exception as e:
        print(f"❌ Error fetching tasks: {e}")
        return []

def format_task_alert(campaign):
    """Create nice looking message for Telegram"""
    # Extract campaign/task info from Worker API response
    campaign_id = campaign.get('cid') or campaign.get('campaign_id') or 'unknown'
    title = campaign.get('c_title') or campaign.get('title') or 'Unnamed Task'
    reward = campaign.get('reward') or campaign.get('c_amount') or 0
    
    # Try to get additional info
    time_estimate = campaign.get('c_ttc') or campaign.get('time_to_complete') or '5-10'
    
    # Create campaign link - adjust based on campaign type
    campaign_type = campaign.get('type', 'b')  # 'b' for basic, 'hg' for hire group
    if campaign_type == 'hg':
        campaign_link = f"https://ttv.microworkers.com/worker/campaign_hg/view/{campaign_id}"
    else:
        campaign_link = f"https://ttv.microworkers.com/worker/campaign_b/view/{campaign_id}"
    
    message = f"""
🎯 <b>NEW TASK AVAILABLE!</b>

📋 <b>Task:</b> {title}

💰 <b>Pay:</b> ${float(reward):.2f}

⏱ <b>Time:</b> {time_estimate} min

🔗 <b>Link:</b> {campaign_link}

⚡️ <b>Grab it fast before someone else does!</b>
"""
    return message

def send_startup_message():
    """Let channel know bot started"""
    message = f"""
🤖 <b>Bot Started!</b>

✅ Monitoring Microworkers for new tasks
🔄 Checking every {CHECK_EVERY_SECONDS} seconds
📅 {datetime.now().strftime('%d %b %Y, %I:%M %p')}

You'll get instant alerts! 🎯
"""
    if send_telegram_message(message):
        print("🤖 Startup message sent to channel")
    else:
        print("❌ Failed to send startup message to channel")

def test_bot():
    """Send a test message to verify bot is running"""
    message = "🧪 <b>Test:</b> Bot is running correctly!"
    if send_telegram_message(message):
        print("🧪 Test message sent to channel")
    else:
        print("❌ Failed to send test message to channel")

def test_api_connection(api):
    """Test if API key is valid"""
    print("🔑 Testing API connection...")
    try:
        # Try to get account info
        result = api.do_request('get', '/account/get_info')
        
        if result['type'] == 'json':
            print("✅ API connection successful!")
            data = result['value']
            if data.get('status') == 'SUCCESS':
                print(f"👤 Account: {data.get('username', 'N/A')}")
                print(f"💰 Balance: ${data.get('balance', 0)}")
            return True
        elif result['type'] == 'error':
            print(f"❌ API Error: {result['value']}")
            return False
        else:
            print("⚠️  Unexpected API response type")
            return True  # Continue anyway
            
    except Exception as e:
        print(f"⚠️  API test failed: {e}")
        return True  # Continue anyway, might still work

def main():
    """Main bot loop - runs forever"""
    print("=" * 50)
    print("🚀 MICROWORKERS ALERT BOT STARTED")
    print("=" * 50)
    print(f"📢 Channel: {CHANNEL_ID}")
    print(f"⏰ Check interval: {CHECK_EVERY_SECONDS} seconds")
    print("=" * 50)
    
    # Initialize Microworkers API
    mw_api = MW_API(MICROWORKERS_API_KEY)
    
    # Test API connection
    test_api_connection(mw_api)
    
    # Send startup notification
    send_startup_message()
    
    # Send test message
    test_bot()
    
    # Load previously sent tasks
    sent_tasks = load_sent_tasks()
    print(f"📝 Loaded {len(sent_tasks)} previously sent tasks")
    
    # Main loop
    loop_count = 0
    while True:
        try:
            loop_count += 1
            current_time = datetime.now().strftime('%I:%M:%S %p')
            print(f"\n⏰ [{current_time}] Check #{loop_count}")
            
            # Get available campaigns
            campaigns = get_available_campaigns(mw_api)
            
            if campaigns:
                print(f"✅ Found {len(campaigns)} campaigns")
                
                # Check each campaign
                new_count = 0
                for campaign in campaigns:
                    campaign_id = str(campaign.get('cid') or campaign.get('campaign_id', 'unknown'))
                    
                    # Skip if already sent
                    if campaign_id in sent_tasks:
                        continue
                    
                    # Send alert
                    message = format_task_alert(campaign)
                    if send_telegram_message(message):
                        title = campaign.get('c_title') or campaign.get('title', 'Unknown')
                        print(f"  📤 Sent: {title[:50]}...")
                        sent_tasks.add(campaign_id)
                        save_task_id(campaign_id)
                        new_count += 1
                        time.sleep(2)  # Small delay between messages
                
                if new_count > 0:
                    print(f"✨ Sent {new_count} new task alerts!")
                else:
                    print("ℹ️  No new campaigns (all already sent)")
            else:
                print("ℹ️  No campaigns available right now")
            
            # Wait before next check
            print(f"💤 Sleeping for {CHECK_EVERY_SECONDS} seconds...")
            time.sleep(CHECK_EVERY_SECONDS)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("⏳ Waiting 2 minutes before retry...")
            time.sleep(120)

if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("❌ Missing 'requests' library!")
        print("📦 Install it with: pip install requests")
        exit(1)
    
    print("\n💡 TIP: Press Ctrl+C to stop the bot\n")
    
    # Start the bot
    main()