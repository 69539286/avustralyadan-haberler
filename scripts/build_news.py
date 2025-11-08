import feedparser
import requests
import json
from bs4 import BeautifulSoup
import html
from datetime import datetime
import urllib.parse
import time

# --- Basit ve stabil çeviri sistemi ---
def translate_safe(text):
    """MyMemory ile çeviri yapar, hata olursa İngilizce döner."""
    if not text:
        return ""
    try:
        url = (
            "https://api.mymemory.translated.net/get?q="
            + urllib.parse.quote(text)
            + "&langpair=en|tr"
        )
        res = requests.get(url, timeout=5).json()
        tr = res.get("responseData", {}).get("translatedText")
        if tr:
            return tr
        return text
    except:
        return text


# --- RSS KAYNAKLARI ---
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
        "https://news.google.com/rss/search?q=Turkey+sports&hl=en-AU&gl=AU&ceid=AU:en"
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


# --- TEMİZLEME FONKSİYONLARI ---
def clean_html(text):
    if not text:
        return ""
    text = html.unescape(text)
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text().strip()


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


# --- HER KATEGORİYİ ÇEK ---
def fetch_category(urls):
    items = []

    for url in urls:
        feed = feedparser.parse(url)

        for e in feed.entries[:20]:
            title_en = clean_html(e.title)
            summary_en = clean_html(e.get("summary", ""))

            # çeviri 1 saniye aralıklarla güvenli çalışır
            tr_title = translate_safe(title_en)
            time.sleep(1)
            tr_summary = translate_safe(summary_en)

            items.append({
                "title": tr_title,
                "summary": tr_summary,
                "link": e.link,
                "published": e.get("published", ""),
                "image": get_image(e)
            })

    return items


# --- JSON OLUŞTUR ---
def build():
    print("JSON oluşturuluyor...")

    out = {"updated_at": datetime.utcnow().isoformat()}

    for cat, urls in RSS_FEEDS.items():
        print("Kategori işleniyor:", cat)
        out[cat] = fetch_category(urls)

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("✅ Tamamlandı: data/news.json")


if __name__ == "__main__":
    build()
