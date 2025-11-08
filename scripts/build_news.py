# scripts/build_news.py
import os, re, json, time, hashlib, textwrap
from datetime import datetime, timezone
import feedparser, requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# ---------- Ayarlar ----------
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT, 'data')
IMG_DIR = os.path.join(ROOT, 'images', 'generated')
JSON_PATH = os.path.join(DATA_PATH, 'news.json')

os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

USER_AGENT = "avustralyadan-haberler-bot/1.0 (+github actions)"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}

# KATEGORİLERE RSS KAYNAKLARI (çoğaltılabilir)
SOURCES = {
    "ekonomi": [
        "https://www.abc.net.au/news/feed/2942460/rss.xml",          # ABC Business
        "https://www.afr.com/rss"                                     # AFR genel RSS (bazı başlıklarda ekonomi)
    ],
    "hukumet": [
        "https://www.abc.net.au/news/politics/rss",                   # ABC Politics
        "https://www.theguardian.com/australia-news/rss"              # Guardian AU
    ],
    "emlak": [
        "https://www.domain.com.au/news/feed",                        # Domain property news
        "https://www.realestate.com.au/news/feed/"                    # REA News
    ],
    "goc": [
        "https://minister.homeaffairs.gov.au/Pages/rss.aspx",         # Home Affairs (değişebilir)
        "https://www.sbs.com.au/news/topic/migration/rss"             # SBS Migration
    ],
    "spor": [
        "https://www.trtspor.com.tr/rss/anasayfa.rss"                 # TR spor geniş
    ],
    "gelismeler": [
        "https://www.abc.net.au/news/justin/rss",                     # ABC Just In
        "https://www.smh.com.au/rss/feed.xml"                         # SMH genel
    ],
    "sosyalist": [
        "https://www.greenleft.org.au/feed"                           # Green Left
    ],
    "istihdam": [
        "https://www.abs.gov.au/rss"                                  # ABS yayınları (işgücü vs.)
    ]
}

# Kaç haber toplanacak (kategori başına)
LIMIT_PER_CATEGORY = 6

# ---------- Yardımcılar ----------
def slugify(text):
    s = re.sub(r"[^\w\s-]", "", text, flags=re.U).strip().lower()
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:60] if s else "post"

def first(val, *alts):
    for v in (val,)+alts:
        if v: return v
    return None

def pick_image_from_entry(entry):
    # RSS standard: media:content, enclosure, image url fields
    # feedparser bazen 'media_content', 'links' vs. döner
    # 1) media_content
    if hasattr(entry, "media_content"):
        for m in entry.media_content:
            url = m.get("url")
            if url: return url
    # 2) media_thumbnail
    if hasattr(entry, "media_thumbnail"):
        for m in entry.media_thumbnail:
            url = m.get("url")
            if url: return url
    # 3) enclosure
    for l in entry.get("links", []):
        if l.get("rel") == "enclosure" and l.get("type","").startswith("image/"):
            return l.get("href")
    # 4) content/summary içinde img ara
    for key in ("content", "summary"):
        htmls = entry.get(key)
        if isinstance(htmls, list):
            htmls = " ".join([c.get("value","") for c in htmls])
        if isinstance(htmls, str):
            soup = BeautifulSoup(htmls, "html.parser")
            im = soup.find("img")
            if im and im.get("src"): return im.get("src")
    return None

def fetch_og_image(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        og = soup.find("meta", property="og:image")
        if og and og.get("content"): return og["content"]
        tw = soup.find("meta", attrs={"name":"twitter:image"})
        if tw and tw.get("content"): return tw["content"]
    except Exception:
        return None

def ensure_placeholder_png(slug, title):
    # Başlıktan basit görsel üret (PNG)
    path = os.path.join(IMG_DIR, f"{slug}.png")
    if os.path.exists(path): return path
    W, H = (780, 520)
    img = Image.new("RGB", (W, H), (237, 242, 247))
    draw = ImageDraw.Draw(img)
    # Basit bir başlık yerleşimi
    pad = 36
    boxW = W - pad*2
    # Yazı tipini default al (GitHub runner’da DejaVu bulunur)
    try:
        fnt = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        fnt2 = ImageFont.truetype("DejaVuSans.ttf", 20)
    except:
        fnt = ImageFont.load_default()
        fnt2 = ImageFont.load_default()

    # Kategori etiketi
    draw.rounded_rectangle([pad, pad, pad+180, pad+40], radius=10, fill=(11,91,161))
    draw.text((pad+12, pad+8), "Avustralyadan Haberler", fill=(255,255,255), font=fnt2)

    # Başlık metni (kısalt)
    t = textwrap.shorten(title, width=120, placeholder="…")
    draw.text((pad, pad+60), t, fill=(20,34,58), font=fnt, spacing=6)

    img.save(path, "PNG")
    return path

def shorten(txt, n=220):
    if not txt: return ""
    return (txt[:n] + "…") if len(txt) > n else txt

def parse_feed(url):
    d = feedparser.parse(url)
    return d.entries or []

# ---------- Topla ----------
def collect():
    out = {k: [] for k in ["ekonomi","hukumet","emlak","goc","spor","gelismeler","sosyalist","istihdam"]}
    for cat, feeds in SOURCES.items():
        bucket = []
        for f in feeds:
            try:
                entries = parse_feed(f)
                for e in entries:
                    title = e.get("title") or ""
                    link = e.get("link") or ""
                    if not title or not link: continue
                    summary = e.get("summary") or ""
                    published = first(
                        e.get("published"),
                        e.get("updated"),
                        ""
                    )
                    source = (e.get("source") or {}).get("title") if isinstance(e.get("source"), dict) else dhost(link)
                    slug = slugify(title) + "-" + hashlib.md5(link.encode("utf-8")).hexdigest()[:6]

                    # Görsel çıkarımı
                    img = pick_image_from_entry(e)
                    if not img:
                        img = fetch_og_image(link)

                    item = {
                        "title": title,
                        "link": link,
                        "summary": shorten(clean_html(summary)),
                        "published": published,
                        "source": source,
                        "image": img,           # varsa gerçek görsel
                        "slug": slug            # yoksa placeholder için kullanılacak
                    }
                    bucket.append(item)
            except Exception as ex:
                print("feed error:", f, ex)
        # Sırala: en taze üstte (published yoksa başa almayız)
        bucket = dedupe_by_link(bucket)
        out[cat] = bucket[:LIMIT_PER_CATEGORY]
    return out

def dhost(url):
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace("www.","")
    except:
        return ""

def clean_html(s):
    try:
        return BeautifulSoup(s, "html.parser").get_text(" ", strip=True)
    except:
        return s

def dedupe_by_link(items):
    seen = set()
    uniq = []
    for it in items:
        if it["link"] in seen: continue
        seen.add(it["link"])
        uniq.append(it)
    return uniq

def generate_placeholders(data):
    for cat, arr in data.items():
        for it in arr:
            if not it.get("image"):
                ensure_placeholder_png(it["slug"], it["title"])

def main():
    data = collect()
    # Placeholder oluştur (gerçek görsel yoksa)
    generate_placeholders(data)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        **data
    }
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("Wrote", JSON_PATH)

if __name__ == "__main__":
    main()
