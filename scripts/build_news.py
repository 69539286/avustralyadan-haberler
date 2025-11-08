import feedparser
import json
import os
from datetime import datetime

RSS_SOURCES = {
    "ekonomi": [
        "https://news.google.com/rss/search?q=Australia+economy&hl=en-AU&gl=AU&ceid=AU:en",
        "https://www.abc.net.au/news/feed/51120/rss.xml"
    ],
    "hukumet": [
        "https://news.google.com/rss/search?q=Australia+government&hl=en-AU&gl=AU&ceid=AU:en",
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
        "https://www.trtspor.com.tr/rss/anasayfa.rss",
        "https://news.google.com/rss/search?q=Turkey+football&hl=tr&gl=TR&ceid=TR:tr"
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

def get_image(entry):
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0]["url"]
    if "media_content" in entry:
        return entry.media_content[0]["url"]
    return PLACEHOLDER_IMAGE

def parse_feed(url):
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries:
        items.append({
            "title": e.get("title", ""),
            "link": e.get("link", ""),
            "summary": e.get("summary", ""),
            "published": e.get("published", ""),
            "source": feed.feed.get("title", ""),
            "image": get_image(e)
        })
    return items

def build():
    output = {"generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}

    for kategori, urls in RSS_SOURCES.items():
        all_items = []
        for url in urls:
            try:
                all_items.extend(parse_feed(url))
            except:
                pass

        all_items.sort(key=lambda x: x.get("published", ""), reverse=True)
        output[kategori] = all_items[:20]

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ Haber JSON üretildi:", OUTPUT_FILE)

if __name__ == "__main__":
    build()
