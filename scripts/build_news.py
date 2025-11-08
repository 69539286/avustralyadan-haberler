# build_news.py

import feedparser
import requests
import json
import os
from datetime import datetime

# ------------------------------------------------
#   RSS KAYNAKLARI (KATEGORİLİ)
# ------------------------------------------------

RSS_SOURCES = {
    "ekonomi": [
        "https://news.google.com/rss/search?q=Australia+economy&hl=en-AU&gl=AU&ceid=AU:en",
        "https://www.reuters.com/markets/australia/rss",
        "https://www.abc.net.au/news/feed/51120/rss.xml"
    ],
    "hukumet": [
        "https://news.google.com/rss/search?q=Australia+government&hl=en-AU&gl=AU&ceid=AU:en",
        "https://www.reuters.com/world/asia-pacific/rss",
        "https://www.abc.net.au/news/politics/feed.xml"
    ],
    "emlak": [
        "https://news.google.com/rss/search?q=Australia+housing+market&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "goc": [
        "https://news.google.com/rss/search?q=Australia+immigration&hl=en-AU&gl=AU&ceid=AU:en",
        "https://www.abc.net.au/news/topic/migration/feed.xml"
    ],
    "spor": [
        "https://www.trtspor.com.tr/rss/anasayfa.rss"
    ],
    "gelismeler": [
        "https://news.google.com/rss/search?q=Australia+breaking+news&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "sosyalist": [
        "https://news.google.com/rss/search?q=Australia+socialist+movement&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "istihdam": [
        "https://news.google.com/rss/search?q=Australia+jobs&hl=en-AU&gl=AU&ceid=AU:en"
    ]
}

OUTPUT_FILE = "data/news.json"
PLACEHOLDER_IMAGE = "https://via.placeholder.com/600x400?text=Haber"
MAX_ITEMS = 20


# ------------------------------
#   GÖRSEL ALMA FONKSİYONU
# ------------------------------

def get_image(entry):
    try:
        if "media_thumbnail" in entry:
            return entry.media_thumbnail[0]["url"]
        if "media_content" in entry:
            return entry.media_content[0]["url"]
        if "links" in entry:
            for l in entry.links:
                if l.get("type", "").startswith("image/"):
                    return l.get("href", PLACEHOLDER_IMAGE)
    except:
        pass
    return PLACEHOLDER_IMAGE


# ------------------------------
#   TEK FEED OKUMA
# ------------------------------

def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        return feed.entries
    except:
        return []


# ------------------------------
#   TÜM KATEGORİLERİ İŞLE
# ------------------------------

def build():
    output = {}

    for kategori, urls in RSS_SOURCES.items():
        all_items = []

        print(f"Kategori işleniyor: {kategori}")

        for url in urls:
            try:
                entries = fetch_feed(url)
                for e in entries:
                    item = {
                        "title": e.get("title", ""),
                        "link": e.get("link", ""),
                        "published": e.get("published", ""),
                        "summary": e.get("summary", "")[:300],
                        "image": get_image(e),
                        "source": url
                    }
                    all_items.append(item)
            except Exception as err:
                print("Feed hatası:", err)

        # En yeni haberler önde
        all_items.sort(key=lambda x: x.get("published", ""), reverse=True)
        output[kategori] = all_items[:MAX_ITEMS]

    # JSON ek bilgisi
    output["generated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Kayıt
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ Haber JSON üretildi:", OUTPUT_FILE)


# ------------------------------
#   ÇALIŞTIR
# ------------------------------

if __name__ == "__main__":
    build()
