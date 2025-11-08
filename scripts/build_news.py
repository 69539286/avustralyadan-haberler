# build_news.py
import feedparser
import requests
import json
import os
from datetime import datetime

# --- Ayarlar ---
RSS_SOURCES = [
    "https://www.abc.net.au/news/feed/51120/rss.xml",     # ABC Australia News
    "https://www.smh.com.au/rss/feed.xml",               # Sydney Morning Herald
    # Daha fazla RSS ekle (senin istediğin “Ekonomi”, “Emlak”, “Göçmenlik”, vb.)
]

OUTPUT_FILE = os.path.join("data", "news.json")
MAX_ITEMS = 30     # en fazla kaç haber çekilsin

# Basit görsel alma: Eğer feedde görsel varsa kullan, yoksa placeholder kullan
PLACEHOLDER_IMAGE = "https://via.placeholder.com/600x400?text=Haber"

def fetch_feed(url):
    feed = feedparser.parse(url)
    return feed

def extract_image(entry):
    # Basit kontrol: entry.media_thumbnail ya da entry.enclosures olabilir
    if 'media_thumbnail' in entry:
        return entry.media_thumbnail[0]['url']
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    # Bazı feedlerde “thumbnail” ya da “image” tag’ları olabilir
    if 'image' in entry:
        return entry.image.get('url')
    # yoksa placeholder döner
    return PLACEHOLDER_IMAGE

def process_entries(feed):
    items = []
    for entry in feed.entries[:MAX_ITEMS]:
        try:
            image_url = extract_image(entry)
        except Exception:
            image_url = PLACEHOLDER_IMAGE
        item = {
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", ""),
            "summary": entry.get("summary", ""),
            "image": image_url
        }
        items.append(item)
    return items

def build():
    all_items = []
    for url in RSS_SOURCES:
        feed = fetch_feed(url)
        items = process_entries(feed)
        all_items.extend(items)
    # Tarihe göre sırala (en yeni ilk)
    all_items.sort(key=lambda x: x.get("published", ""), reverse=True)
    # JSON üret
    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(all_items),
        "items": all_items
    }
    # Klasör yoksa yarat
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    # Kaydet
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✅ {OUTPUT_FILE} oluşturuldu: {output['count']} haber")

if __name__ == "__main__":
    build()
