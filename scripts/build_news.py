import feedparser
import requests
import json
from bs4 import BeautifulSoup
import html
from datetime import datetime
import urllib.parse

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

# ✅ ÜCRETSİZ ÇEVİRİ (MyMemory)
def translate(text):
    if not text:
        return ""
    try:
        api = "https://api.mymemory.translated.net/get?q=" + urllib.parse.quote(text) + "&langpair=en|tr"
        r = requests.get(api, timeout=7).json()
        return r["responseData"]["translatedText"]
    except:
        return text

# ✅ Title temizleme
def clean_title(raw):
    try:
        raw = html.unescape(raw)
        soup = BeautifulSoup(raw, "html.parser")
        txt = soup.get_text()
        return txt.strip()
    except:
        return raw

# ✅ Özet yapay olarak site içeriğinden çıkarılıyor
def extract_summary(url):
    try:
        real = requests.get(url, timeout=7)
        soup = BeautifulSoup(real.text, "html.parser")

        p = soup.find("p")
        if p:
            return p.get_text().strip()

    except:
        pass
    return ""

# ✅ Google News URL → gerçek URL çözümü
def resolve_url(gn_url):
    try:
        r = requests.get(gn_url, allow_redirects=True, timeout=7)
        return r.url
    except:
        return gn_url

# ✅ Görsel bulma
def get_image_from_page(url):
    try:
        r = requests.get(url, timeout=7)
        soup = BeautifulSoup(r.text, "html.parser")

        og = soup.find("meta", property="og:image")
        if og:
            return og["content"]

        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

    except:
        pass

    return "https://via.placeholder.com/600x400?text=Haber"

# ✅ Tek kategori oku
def fetch_category(urls):
    out = []

    for feed in urls:
        f = feedparser.parse(feed)

        for e in f.entries[:15]:

            original_title = clean_title(e.title)
            tr_title = translate(original_title)

            final_url = resolve_url(e.link)

            summary = extract_summary(final_url)
            tr_summary = translate(summary) if summary else ""

            image = get_image_from_page(final_url)

            out.append({
                "title": tr_title,
                "summary": tr_summary,
                "link": final_url,
                "published": e.get("published", ""),
                "image": image
            })

    return out

# ✅ JSON oluştur
def build_json():
    data = {
        "updated_at": datetime.utcnow().isoformat()
    }

    for cat, urls in RSS_FEEDS.items():
        print("Kategori işleniyor:", cat)
        data[cat] = fetch_category(urls)

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Tamamlandı → data/news.json")

if __name__ == "__main__":
    build_json()
