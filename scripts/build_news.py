import feedparser
import requests
import json
import html
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

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
        "https://news.google.com/rss/search?q=Australia+socialist+movement&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "istihdam": [
        "https://news.google.com/rss/search?q=Australia+employment&hl=en-AU&gl=AU&ceid=AU:en"
    ],
}

PLACEHOLDER_IMAGE = "https://via.placeholder.com/600x400?text=Haber"


# -----------------------------
# EN KRİTİK KISIM: Temiz başlık
# -----------------------------
def clean_title(raw):
    if not raw:
        return ""

    # HTML decode
    txt = html.unescape(raw)

    # Bazı başlıklarda link etiketi oluyor: <a href="...">Title</a>
    soup = BeautifulSoup(txt, "html.parser")
    txt = soup.get_text()

    # Google News bazen başlığı encode ediyor → decode et
    try:
        txt = urllib.parse.unquote(txt)
    except:
        pass

    return txt.strip()


# -----------------------------
# MyMemory çeviri
# -----------------------------
def translate_tr(text):
    if not text:
        return ""
    try:
        url = "https://api.mymemory.translated.net/get?q=" + urllib.parse.quote(text) + "&langpair=en|tr"
        r = requests.get(url, timeout=5).json()
        return r["responseData"]["translatedText"]
    except:
        return text


# ----------------------------------------
# OpenGraph görsel alma
# ----------------------------------------
def get_opengraph_image(url):
    try:
        html_doc = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html_doc, "html.parser")
        tag = soup.find("meta", property="og:image")
        if tag and tag.get("content"):
            return tag["content"]
    except:
        pass
    return None


# ----------------------------------------
# RSS içinden görsel alma
# ----------------------------------------
def extract_image(entry):
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

    return PLACEHOLDER_IMAGE


# ----------------------------------------
# Kategori topla → çevir → temizle → kaydet
# ----------------------------------------
def fetch_category(urls):
    items = []

    for u in urls:
        feed = feedparser.parse(u)

        for e in feed.entries:
            clean = clean_title(e.title)
            tr_title = translate_tr(clean)

            summary_raw = html.unescape(e.get("summary", ""))
            summary_txt = BeautifulSoup(summary_raw, "html.parser").get_text()
            tr_summary = translate_tr(summary_txt)

            image = extract_image(e)
            if image == PLACEHOLDER_IMAGE:
                og = get_opengraph_image(e.link)
                if og:
                    image = og

            items.append({
                "title": tr_title,
                "summary": tr_summary,
                "link": e.link,
                "published": e.get("published", ""),
                "image": image
            })

    return items[:20]


# ----------------------------------------
# JSON yaz
# ----------------------------------------
def build_json():
    data = {
        "updated_at": datetime.utcnow().isoformat()
    }

    for cat, urls in RSS_FEEDS.items():
        print("Kategori:", cat)
        data[cat] = fetch_category(urls)

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✓ Haberler yenilendi → data/news.json")


if __name__ == "__main__":
    build_json()
