import feedparser
import requests
import json
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# -------------------------------
# AYARLAR
# -------------------------------
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
        "https://news.google.com/rss/search?q=Australia+socialist+movements&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "istihdam": [
        "https://news.google.com/rss/search?q=Australia+employment&hl=en-AU&gl=AU&ceid=AU:en"
    ]
}

PLACEHOLDER_IMAGE = "https://via.placeholder.com/600x400?text=Haber"


# ----------------------------------------
# METİN TÜRKÇE ÇEVİRİ (MyMemory API)
# ----------------------------------------
def translate_tr(text):
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


# ----------------------------------------
# OpenGraph Görsel Alma
# ----------------------------------------
def get_opengraph_image(url):
    try:
        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, "html.parser")
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]
    except:
        pass
    return None


# ----------------------------------------
# RSS İÇERİSİNDEN GÖRSEL ALMA
# ----------------------------------------
def extract_image(entry):
    if "media_content" in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get("url", PLACEHOLDER_IMAGE)

    if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get("url", PLACEHOLDER_IMAGE)

    return PLACEHOLDER_IMAGE


# ----------------------------------------
# RSS TOPLA – ÇEVİR – GÖRSEL EKLE
# ----------------------------------------
def fetch_category(feed_list):
    items = []

    for url in feed_list:
        parsed = feedparser.parse(url)

        for entry in parsed.entries:
            image = extract_image(entry)
            if image == PLACEHOLDER_IMAGE:
                og = get_opengraph_image(entry.link)
                if og:
                    image = og

            items.append(
                {
                    "title": translate_tr(entry.title),
                    "summary": translate_tr(entry.get("summary", "")),
                    "link": entry.link,
                    "published": entry.get("published", ""),
                    "image": image,
                }
            )
    return items[:20]


# ----------------------------------------
# ANA JSON DOSYASINI OLUŞTUR
# ----------------------------------------
def build_news_json():
    data = {"updated_at": datetime.utcnow().isoformat()}

    for category, feeds in RSS_FEEDS.items():
        print(f"Kategori işleniyor: {category}")
        data[category] = fetch_category(feeds)

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure
