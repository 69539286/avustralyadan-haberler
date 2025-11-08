# build_news.py
import feedparser
import requests
import json
import os
from datetime import datetime

# --- RSS KAYNAKLARI (GARANTİ ÇALIŞANLAR) ---
RSS = {
    "ekonomi": [
        "https://www.abc.net.au/news/business/feed/2942/rss.xml",
        "https://www.reuters.com/business/australia/rss"
    ],
    "hukumet": [
        "https://www.abc.net.au/news/politics/feed/53120/rss.xml"
    ],
    "emlak": [
        "https://www.abc.net.au/news/topic/real-estate/feed/rss"
    ],
    "goc": [
        "https://www.sbs.com.au/language/english/topic/migration?view=trt&format=rss"
    ],
    "spor": [
        "https://www.trtspor.com.tr/manset.rss",
        "https://www.haberturk.com/rss/manset.xml"
    ],
    "gelismeler": [
        "https://www.abc.net.au/news/justin/rss"
    ],
    "sosyalist": [
        "https://redflag.org.au/rss.xml"
    ],
    "istihdam": [
        "https://www.abc.net.au/news/business/jobs/feed/286/rss.xml"
    ]
}

OUTPUT_FILE = os.path.join("data", "news.json")
PLACEHOLDER_IMAGE = "https://via.placeholder.com/600x400?text=Haber"

def extract_image(entry):
    if 'media_thumbnail' in entry:
        return entry.media_thumbnail[0]['url']
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    if 'image' in entry:
        return entry.image.get('url')
    if 'links' in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image"):
                return link.get("href")
    return PLACEHOLDER_IMAGE

def fetch_category(feeds):
    items = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
                "source": feed.feed.get("title", ""),
                "image": extract_image(entry)
            })
    items.sort(key=lambda x: x["published"], reverse=True)
    return items[:30]  # max 30

def build():
    data = {}
    for cat, feeds in RSS.items():
        print(f"Kategori işleniyor: {cat}")
        data[cat] = fetch_category(feeds)

    data["generated_at"] = datetime.utcnow().isoformat() + "Z"

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Haber JSON üretildi:", OUTPUT_FILE)

if __name__ == "__main__":
    build()
