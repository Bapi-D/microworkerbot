import imaplib
import email
import os
import time
import asyncio
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")
CHECK_EVERY_SECONDS = 3
HEARTBEAT_INTERVAL_SECONDS = 3600  # 1 hour

bot = Bot(token=BOT_TOKEN)

IMAP_SERVER = "imap.gmail.com"
LABEL = '"Microworkers"'

async def check_mail():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select(LABEL)

    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()

    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        subject = msg["subject"]

        text_content = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    text_content = part.get_payload(decode=True).decode()
        else:
            text_content = msg.get_payload(decode=True).decode()

        message = f"""
🚨 *New Microworkers Task Alert*

📌 *Title:* {subject}

📩 *Check your Microworkers dashboard to apply*

⏰ *Time:* Just now
        """

        await bot.send_message(
            chat_id=GROUP_ID,
            text=message,
            parse_mode="Markdown"
        )

        mail.store(e_id, '+FLAGS', '\\Seen')

    mail.logout()

async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="HTML")
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

async def send_startup_message():
    """Let channel know bot started"""
    message = f"""
🤖 <b>Bot Started!</b>

✅ Monitoring Microworkers for new tasks
🔄 Checking every {CHECK_EVERY_SECONDS} seconds
📅 {datetime.now().strftime('%d %b %Y, %I:%M %p')}

You'll get instant alerts! 🎯
"""
    if await send_telegram_message(message):
        print("🤖 Startup message sent to channel")
    else:
        print("❌ Failed to send startup message to channel")

async def test_bot():
    """Send a test message to verify bot is running"""
    message = "🧪 <b>Test:</b> Bot is running correctly!"
    if await send_telegram_message(message):
        print("🧪 Test message sent to channel")
    else:
        print("❌ Failed to send test message to channel")

async def main():
    await send_startup_message()
    last_heartbeat = asyncio.get_event_loop().time()
    while True:
        try:
            await check_mail()
            current_time = asyncio.get_event_loop().time()
            if current_time - last_heartbeat >= HEARTBEAT_INTERVAL_SECONDS:
                await send_telegram_message("🟢 Microworkers bot is running normally.")
                last_heartbeat = current_time
            await asyncio.sleep(3)  # check every 3 seconds
        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())

