import feedparser
import requests
import time
import os
import json
from datetime import datetime

# ========== YAHAN APNI DETAILS DAALO ==========
TELEGRAM_BOT_TOKEN = "8994858372:AAHnMwrtMyLm2bWWA5cASP3NDtNfz8dv0yY"
TELEGRAM_CHAT_ID = "6933065522"
# ==============================================

RSS_FEEDS = [
    "https://www.nature.com/subjects/zoology.rss",
    "https://www.sciencedaily.com/rss/plants_animals/biology.xml",
    "https://phys.org/rss-feed/biology-news/"
]

SEEN_FILE = "seen_news.json"
CHECK_INTERVAL = 10


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
        print(f"[ERROR] {e}")
        return False


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
                print(f"[SENT] {title}")
                time.sleep(1)

    if count > 0:
        save_seen(seen)
        print(f"[INFO] {count} new news bheji gayi.")
    else:
        print("[INFO] Koi nayi news nahi mili.")


def main():
    print("[START] Biology News Bot chal raha hai...")
    while True:
        try:
            check_news()
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
