import feedparser
import json
import datetime
import requests

# Eğer RSS görseli yoksa yedek görsel
DEFAULT_IMAGE = "https://source.unsplash.com/800x600/?news,australia"

# Ekstra: Türkçe çeviri (Google Translate API gibi)
def translate_to_tr(text):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": "en|tr"}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        return data.get("responseData", {}).get("translatedText", text)
    except:
        return text

# RSS parser
def parse_feed(url, limit=20):
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        link = entry.get("link", "")

        # Görsel alanlarını kontrol et
        image = None

        # 1: media_thumbnail
        if "media_thumbnail" in entry:
            image = entry.media_thumbnail[0].get("url")

        # 2: media_content
        elif "media_content" in entry:
            image = entry.media_content[0].get("url")

        # 3: enclosure
        elif "enclosures" in entry and len(entry.enclosures) > 0:
            image = entry.enclosures[0].get("href")

        # 4: görsel yoksa varsayılan görsel
        if not image:
            image = DEFAULT_IMAGE

        items.append({
            "title": translate_to_tr(title),
            "summary": translate_to_tr(summary),
            "link": link,
            "image": image
        })

    return items

# Haber kaynakları
RSS_SOURCES = {
    "economy": [
        "https://www.abc.net.au/news/feed/45924/rss.xml",
        "https://www.theguardian.com/australia-news/economy/rss",
        "https://www.afr.com/rss"
    ],
    "government": [
        "https://www.abc.net.au/news/politics/feed/45926/rss.xml",
        "https://www.sbs.com.au/news/topic/politics/article/feed"
    ],
    "realestate": [
        "https://www.domain.com.au/news/feed/",
        "https://www.realestate.com.au/news/feed/"
    ],
    "immigration": [
        "https://www.sbs.com.au/language/turkish/en/topic/migration/feed",
        "https://www.sbs.com.au/news/topic/migration/article/feed"
    ],
    "tr_sports": [
        "https://www.trtspor.com.tr/rss/anasayfa.rss",
        "https://www.ntvspor.net/rss",
        "https://www.fanatik.com.tr/rss"
    ],
    "new_developments": [
        "https://www.abc.net.au/news/feed/51120/rss.xml"
    ],
    "socialist": [
        "https://www.greenleft.org.au/taxonomy/term/1/feed",
        "https://socialist-alliance.org/news/rss.xml"
    ],
    "jobs": [
        "https://www.abc.net.au/news/business/jobs/feed/45918/rss.xml"
    ]
}

# Tüm RSS kaynaklarını işleme
def build_json():
    result = {"generated_at": str(datetime.datetime.utcnow())}

    for category, feeds in RSS_SOURCES.items():
        merged = []
        for feed in feeds:
            merged.extend(parse_feed(feed, limit=10))
        result[category] = merged

    # JSON kaydet
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    build_json()
