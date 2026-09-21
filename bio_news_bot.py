import feedparser
import requests
import time
import os
import json
from datetime import datetime

# ========== ENV VARIABLES (Railway + Termux dono me chalega) ==========
# Railway pe Variables tab se aayega, Termux pe .env file se ya hardcoded fallback se
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Agar Termux me chalana ho aur env variable set na ho, to yahan directly daal do
if not TELEGRAM_BOT_TOKEN:
    TELEGRAM_BOT_TOKEN = "8994858372:AAHnMwrtMyLm2bWWA5cASP3NDtNfz8dv0yY"   # <-- Termux ke liye yahan daalo
if not TELEGRAM_CHAT_ID:
    TELEGRAM_CHAT_ID = "6933065522"        # <-- Termux ke liye yahan daalo
# =====================================================================

# Biology RSS Feeds (har roz nayi news aati hai)
RSS_FEEDS = [
    "https://www.nature.com/subjects/zoology.rss",
    "https://www.sciencedaily.com/rss/plants_animals/biology.xml",
    "https://phys.org/rss-feed/biology-news/"
]

SEEN_FILE = "seen_news.json"
CHECK_INTERVAL = 10   # har 10 second me check karega


def load_seen():
    """Purani bheji hui news ki IDs load karo"""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    """Nayi bheji hui news ki IDs save karo"""
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def format_date(parsed):
    """Date ko 'Monday, 22 September 2026' format me badlo"""
    if parsed:
        dt = datetime(*parsed[:6])
        return dt.strftime("%A, %d %B %Y")
    return datetime.now().strftime("%A, %d %B %Y")


def send_msg(text):
    """Telegram pe message bhejo"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }, timeout=10)
        return r.ok
    except Exception as e:
        print(f"[ERROR] Telegram send: {e}")
        return False


def check_news():
    """Saare feeds check karo, nayi news bhejo"""
    seen = load_seen()
    count = 0

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"[ERROR] Feed parse: {e}")
            continue

        for entry in feed.entries:
            news_id = entry.get("id") or entry.get("link") or entry.get("title", "")
            if news_id in seen:
                continue   # purani news, skip karo

            title = entry.get("title", "No Title")
            link = entry.get("link", "")
            summary = entry.get("summary", "")[:300]
            date_str = format_date(entry.get("published_parsed"))

            msg = (
                f"🧬 *{title}*\n\n"
                f"📅 *Date:* {date_str}\n\n"
                f"📝 {summary}...\n\n"
                f"🔗 [Read Full Article]({link})"
            )

            if send_msg(msg):
                seen.add(news_id)
                count += 1
                print(f"[SENT] {title}")
                time.sleep(1)   # Telegram rate limit se bachne ke liye

    if count > 0:
        save_seen(seen)
        print(f"[INFO] {count} nayi news bheji gayi.")
    else:
        print("[INFO] Koi nayi news nahi mili.")


def main():
    print("[START] Biology News Bot chal raha hai...")
    print(f"[INFO] Har {CHECK_INTERVAL} second me check karega.")
    while True:
        try:
            check_news()
        except Exception as e:
            print(f"[ERROR] Main loop: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
