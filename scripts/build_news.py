# build_news.py
import feedparser
import requests
import json
import os
from datetime import datetime

# ---------------------------------------------------------
#  RSS KAYNAKLARI (Kategori kategori)
# ---------------------------------------------------------
RSS_MAP = {
    "ekonomi": [
        "https://www.abc.net.au/news/feed/45918/rss.xml",
        "https://www.afr.com/rss",
    ],
    "hukumet": [
        "https://www.abc.net.au/news/politics/feed/2940/rss.xml",
    ],
    "emlak": [
        "https://www.domain.com.au/news/feed/",
        "https://www.realestate.com.au/news/feed/",
    ],
    "goc": [
        "https://immi.homeaffairs.gov.au/news-media/archive?format=feed&type=rss",
    ],
    "spor": [
        "https://www.trtspor.com.tr/manset.rss",
        "https://www.fanatik.com.tr/rss",
    ],
    "gelismeler": [
        "https://www.abc.net.au/news/justin/rss",
    ],
    "sosyalist": [
        "https://redflag.org.au/rss.xml",
    ],
    "istihdam": [
        "https://www.abc.net.au/news/business/jobs/feed/286/rss.xml",
    ]
}

# ---------------------------------------------------------
# Sabitler
# ---------------------------------------------------------
OUTPUT_FILE = os.path.join("data", "news.json")
MAX_ITEMS = 15
USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}
PLACEHOLDER = "https://via.placeholder.com/600x400?text=Haber"

# ---------------------------------------------------------
def fetch_feed(url):
    try:
        r = requests.get(url, headers=USER_AGENT, timeout=10)
        return feedparser.parse(r.content)
    except:
        return {"entries": []}

# ---------------------------------------------------------
def extract_image(entry):
    try:
        if "media_thumbnail" in entry:
            return entry.media_thumbnail[0]["url"]
        if "media_content" in entry:
            return entry.media_content[0]["url"]
        if "image" in entry:
            return entry.image.get("url")
        if "links" in entry:
            for l in entry.links:
                if l.get("type", "").startswith("image"):
                    return l.get("href")
    except:
        pass
    return PLACEHOLDER

# ---------------------------------------------------------
def process_feed(entries, source_name):
    items = []
    for e in entries[:MAX_ITEMS]:
        img = extract_image(e)
        published = e.get("published", "") or e.get("updated", "")

        item = {
            "title": e.get("title", "Başlıksız Haber"),
            "link": e.get("link", ""),
            "summary": e.get("summary", "")[:350],
            "published": published,
            "image": img,
            "source": source_name,
            "slug": e.get("title", "").lower().replace(" ", "-")[:40]
        }
        items.append(item)

    return items

# ---------------------------------------------------------
def build():
    all_data = {}
    
    for category, feeds in RSS_MAP.items():
        merged = []
        for url in feeds:
            f = fetch_feed(url)
            source_name = url.split("/")[2]
            merged.extend(process_feed(f.get("entries", []), source_name))

        # En yeni haberler üste
        merged.sort(key=lambda x: x["published"], reverse=True)

        # JSON'a ekle
        all_data[category] = merged

    # Son metadata
    all_data["generated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Klasör yoksa oluştur
    os.makedirs("data", exist_ok=True)

    # Kaydet
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("✅ Haber JSON üretildi:", OUTPUT_FILE)

# ---------------------------------------------------------
if __name__ == "__main__":
    build()
