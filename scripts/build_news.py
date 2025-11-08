import feedparser
import requests
import json
from bs4 import BeautifulSoup
import html
from datetime import datetime
import urllib.parse
import re

# RSS Kategorileri
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
    ]
}

# ✅ MyMemory API ile İngilizce→Türkçe çeviri
def translate(text):
    if not text:
        return ""
    text = text.strip()
    if len(text) > 4000:
        text = text[:4000]

    try:
        url = (
            "https://api.mymemory.translated.net/get?q="
            + urllib.parse.quote(text)
            + "&langpair=en|tr"
        )
        r = requests.get(url, timeout=10).json()
        tr = r.get("responseData", {}).get("translatedText", "")

        # API bazen AUTO|IT hatası veriyor → düzeltme
        if "INVALID" in tr.upper() or tr.strip() == "":
            return text

        return tr
    except:
        return text


# ✅ Basit bir yapay zeka özetleyici (kuralsal)
def summarize_tr(text):
    if not text:
        return ""

    text = text.strip()

    # Noktaya göre böl
    cums = re.split(r'[.!?]', text)
    cums = [c.strip() for c in cums if c.strip()]

    if len(cums) == 0:
        return text

    # 4–7 cümlelik detaylı özet kuralı
    if len(cums) > 7:
        cums = cums[:7]

    return " ".join(cums)


# ✅ Başlık temizliği
def clean_title(raw):
    if not raw:
        return ""
    raw = html.unescape(raw)
    soup = BeautifulSoup(raw, "html.parser")
    text = soup.get_text()
    try:
        text = urllib.parse.unquote(text)
    except:
        pass
    return text.strip()


# ✅ İngilizce summary temizliği
def clean_summary(raw):
    if not raw:
        return ""
    raw = html.unescape(raw)
    soup = BeautifulSoup(raw, "html.parser")
    return soup.get_text().strip()


# ✅ Görsel bulma
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


# ✅ Kategori çekme + çeviri + detaylı özet
def fetch_category(urls):
    all_items = []

    for feed_url in urls:
        f = feedparser.parse(feed_url)

        for e in f.entries:
            en_title = clean_title(e.title)
            en_summary = clean_summary(e.get("summary", ""))

            # Türkçeye çeviri
            tr_title = translate(en_title)
            tr_summary_raw = translate(en_summary)

            # Detaylı Türkçe özet
            tr_summary = summarize_tr(tr_summary_raw)

            img = get_image(e)

            all_items.append({
                "title": tr_title,
                "summary": tr_summary,
                "link": e.link,
                "published": e.get("published", ""),
                "image": img
            })

    return all_items[:20]


# ✅ JSON Dosyası Oluşturma
def build_json():
    data = {"updated_at": datetime.utcnow().isoformat()}

    for cat, urls in RSS_FEEDS.items():
        print("Kategori:", cat)
        data[cat] = fetch_category(urls)

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✓ Tamamlandı: data/news.json güncellendi")


if __name__ == "__main__":
    build_json()
