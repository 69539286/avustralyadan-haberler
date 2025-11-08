# scripts/build_news.py
import os, re, json, hashlib, textwrap
from datetime import datetime, timezone
import feedparser, requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# AYARLAR
# ============================================================

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT, "data")
IMG_DIR = os.path.join(ROOT, "images", "generated")
JSON_PATH = os.path.join(DATA_PATH, "news.json")

os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

USER_AGENT = "avustralyadan-haberler-bot/1.0"
HEADERS = {"User-Agent": USER_AGENT}

LIMIT_PER_CATEGORY = 6   # Her kategroide 6 haber

# ============================================================
# RSS KAYNAKLARI
# ============================================================

SOURCES = {
    "ekonomi": [
        "https://www.abc.net.au/news/feed/2942460/rss.xml",
        "https://www.afr.com/rss"
    ],
    "hukumet": [
        "https://www.abc.net.au/news/politics/rss",
        "https://www.theguardian.com/australia-news/rss"
    ],
    "emlak": [
        "https://www.domain.com.au/news/feed",
        "https://www.realestate.com.au/news/feed/"
    ],
    "goc": [
        "https://www.sbs.com.au/news/topic/migration/rss",
        "https://minister.homeaffairs.gov.au/Pages/rss.aspx"
    ],
    "spor": [
        "https://www.trtspor.com.tr/rss/anasayfa.rss"
    ],
    "gelismeler": [
        "https://www.abc.net.au/news/justin/rss",
        "https://www.smh.com.au/rss/feed.xml"
    ],
    "sosyalist": [
        "https://www.greenleft.org.au/feed"
    ],
    "istihdam": [
        "https://www.abs.gov.au/rss"
    ]
}

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def slugify(text):
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:60] if s else "post"

def clean_html(s):
    try:
        return BeautifulSoup(s, "html.parser").get_text(" ", strip=True)
    except:
        return s

def shorten(txt, n=220):
    if not txt:
        return ""
    return txt[:n] + "…" if len(txt) > n else txt

def domain(url):
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace("www.", "")
    except:
        return ""

def dedupe(items):
    seen = set()
    out = []
    for it in items:
        if it["link"] in seen:
            continue
        seen.add(it["link"])
        out.append(it)
    return out

# ============================================================
# GÖRSEL ÇIKARMA (RSS → OG:IMAGE → YOKSA PLACEHOLDER PNG)
# ============================================================

def pick_image_from_entry(entry):
    # media:content
    if hasattr(entry, "media_content"):
        for m in entry.media_content:
            if m.get("url"):
                return m["url"]

    # media:thumbnail
    if hasattr(entry, "media_thumbnail"):
        for m in entry.media_thumbnail:
            if m.get("url"):
                return m["url"]

    # enclosure
    for link in entry.get("links", []):
        if link.get("rel") == "enclosure" and link.get("type","").startswith("image/"):
            return link.get("href")

    # summary içindeki img
    if entry.get("summary"):
        soup = BeautifulSoup(entry.summary, "html.parser")
        im = soup.find("img")
        if im and im.get("src"):
            return im["src"]

    return None

def fetch_og_image(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]

        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            return tw["content"]

    except:
        return None

    return None

def make_placeholder(slug, title):
    path = os.path.join(IMG_DIR, f"{slug}.png")
    if os.path.exists(path):
        return path

    W, H = 780, 520
    img = Image.new("RGB", (W, H), (235, 240, 245))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 22)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((30, 30), "Avustralyadan Haberler", fill=(20,40,80), font=font_small)

    short_title = textwrap.shorten(title, width=40, placeholder="…")
    draw.text((30, 120), short_title, fill=(10, 20, 40), font=font_big)

    img.save(path, "PNG")
    return path

# ====================================
