import feedparser
import requests
import time
import os
import json
from datetime import datetime

# ========== TOKEN ==========
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    TELEGRAM_BOT_TOKEN = "8994858372:AAHnMwrtMyLm2bWWA5cASP3NDtNfz8dv0yY"   # Termux ke liye

# ========== MULTIPLE CHAT IDS (DM + Group) ==========
# Railway me: comma se separate karke daalo, jaise: 6933065522,-1001234567890
_chat_ids_raw = os.environ.get("TELEGRAM_CHAT_ID", "")
if not _chat_ids_raw:
    _chat_ids_raw = "6933065522,-1003918590730"   # Termux ke liye

TELEGRAM_CHAT_IDS = [cid.strip() for cid in _chat_ids_raw.split(",") if cid.strip()]
# ====================================================

RSS_FEEDS = [
    "https://www.nature.com/subjects/zoology.rss",
    "https://www.sciencedaily.com/rss/plants_animals/biology.xml",
    "https://phys.org/rss-feed/biology-news/"
]

SEEN_FILE = "seen_news.json"
CHECK_INTERVAL = 10800


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def format_date(parsed):
    if parsed:
        dt = datetime(*parsed[:6])
        return dt.strftime("%A, %d %B %Y")
    return datetime.now().strftime("%A, %d %B %Y")


def send_msg(text):
    """Saare chat IDs (DM + Group) pe message bhejo"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    success = False
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            r = requests.post(url, data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }, timeout=10)
            if r.ok:
                success = True
                print(f"[SENT] {chat_id}")
            else:
                print(f"[FAILED] {chat_id} → {r.text}")
        except Exception as e:
            print(f"[ERROR] {chat_id}: {e}")
    return success


def check_news():
    seen = load_seen()
    count = 0

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"[ERROR] Feed: {e}")
            continue

        for entry in feed.entries:
            news_id = entry.get("id") or entry.get("link") or entry.get("title", "")
            if news_id in seen:
                continue

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
                time.sleep(1)

    if count > 0:
        save_seen(seen)
        print(f"[INFO] {count} nayi news bheji gayi.")
    else:
        print("[INFO] Koi nayi news nahi mili.")


def main():
    print("[START] Biology News Bot chal raha hai...")
    print(f"[INFO] Har {CHECK_INTERVAL} second me check karega.")
    print(f"[INFO] Chat IDs: {TELEGRAM_CHAT_IDS}")
    while True:
        try:
            check_news()
        except Exception as e:
            print(f"[ERROR] Main loop: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
