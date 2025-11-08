import feedparser
import requests
import json
from bs4 import BeautifulSoup
import html
from datetime import datetime
import urllib.parse

# Kategoriler ve RSS adresleri
RSS_FEEDS = {
    "ekonomi": [
        "https://news.google.com/rss/search?q=Australia+economy&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "hukumet": [
        "https://news.google.com/rss/search?q=Australia+government&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "emlak": [
        "https://news.google.com/rss/search?q=Australia+real+estate&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "goc": [
        "https://news.google.com/rss/search?q=Australia+immigration&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "spor": [
        "https://news.google.com/rss/search?q=Australia+sport&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "gelismeler": [
        "https://news.google.com/rss/search?q=Australia+breaking+news&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "sosyalist": [
        "https://news.google.com/rss/search?q=Australia+socialist&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "istihdam": [
        "https://news.google.com/rss/search?q=Australia+employment&hl=en-AU&gl=AU&ceid=AU:en"
    ],
}

# Çeviri API (MyMemory ücretsiz)
def translate(text):
    if not text:
        return ""
    try:
        url = (
            "https://api.mymemory.translated.net/get?q="
            + urllib.parse.quote(text)
            + "&langpair=en|tr"
        )
        r = requests.get(url, timeout=5).json()
        return r["responseData"]["translatedText"]
    except:
        return text


# Başlığı temizle
def clean_title(raw):
    if not raw:
        return ""

    raw = html.unescape(raw)
    soup = BeautifulSoup(raw, "html.parser")
    txt = soup.get_text()

    # Google News bazen encoded oluyor
    try:
        txt = urllib.parse.unquote(txt)
    except:
        pass

    return txt.strip()


# Summary’yi temizle
def clean_summary(summary):
    if not summary:
        return ""
    summary = html.unescape(summary)
    soup = BeautifulSoup(summary, "html.parser")
    return soup.get_text().strip()


# Görsel alma
def get_image(entry):
    if "media_content" in entry:
        try:
            return entry.media_content[0]["url"]
        except:
            pass
    if "media_thumbnail" in entry:
        try:
            return entry.media_thumbnail[0]["url"]
        except:
            pass
    return "https://via.placeholder.com/600x400?text=Haber"


# RSS kategori oku
def fetch_category(urls):
    all_items = []

    for feed_url in urls:
        f = feedparser.parse(feed_url)

        for e in f.entries:
            # İngilizce başlık temizle
            original_title = clean_title(e.title)
            tr_title = translate(original_title)

            # İngilizce özet temizle
            original_summary = clean_summary(e.get("summary", ""))
            tr_summary = translate(original_summary)

            img = get_image(e)

            all_items.append({
                "title": tr_title,
                "summary": tr_summary,
                "link": e.link,
                "published": e.get("published", ""),
                "image": img
            })

    return all_items[:20]


# JSON dosyası oluştur
def build_json():
    data = {"updated_at": datetime.utcnow().isoformat()}

    for cat, urls in RSS_FEEDS.items():
        print("Kategori işleniyor:", cat)
        data[cat] = fetch_category(urls)

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✓ Güncellendi: data/news.json")


if __name__ == "__main__":
    build_json()
