# -*- coding: utf-8 -*-
import feedparser
import requests
import json
from bs4 import BeautifulSoup
import html
from datetime import datetime, timezone
import urllib.parse
import hashlib
import time

# ---------- Ayarlar ----------
USER_AGENT = "Mozilla/5.0 (compatible; Avustralyadan-Haberler/1.0; +https://example.local)"
TIMEOUT = 12
PER_SECTION_LIMIT = 20
REQUEST_SLEEP = 0.7  # siteleri üzmeyelim
TRANSLATE_SLEEP = 0.4

# Kategoriler ve RSS adresleri (Google News)
RSS_FEEDS = {
    "ekonomi":   ["https://news.google.com/rss/search?q=Australia+economy&hl=en-AU&gl=AU&ceid=AU:en"],
    "hukumet":   ["https://news.google.com/rss/search?q=Australia+government&hl=en-AU&gl=AU&ceid=AU:en"],
    "emlak":     ["https://news.google.com/rss/search?q=Australia+housing+OR+real+estate&hl=en-AU&gl=AU&ceid=AU:en"],
    "goc":       ["https://news.google.com/rss/search?q=Australia+immigration&hl=en-AU&gl=AU&ceid=AU:en"],
    "spor":      ["https://news.google.com/rss/search?q=Turkey+sport+Australia+site:abc.net.au+OR+site:sbs.com.au&hl=en-AU&gl=AU&ceid=AU:en"],
    "gelismeler":["https://news.google.com/rss/search?q=Australia+breaking+news&hl=en-AU&gl=AU&ceid=AU:en"],
    "sosyalist": ["https://news.google.com/rss/search?q=Australia+socialist+union+strike&hl=en-AU&gl=AU&ceid=AU:en"],
    "istihdam":  ["https://news.google.com/rss/search?q=Australia+employment+jobs+unemployment&hl=en-AU&gl=AU&ceid=AU:en"],
}

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


# ---------- Yardımcılar ----------
def translate(text, src="auto", dst="tr"):
    """MyMemory ile basit çeviri (ücretsiz). Hata olursa orijinali döndürür."""
    if not text:
        return ""
    try:
        url = (
            "https://api.mymemory.translated.net/get?q="
            + urllib.parse.quote(text[:5000])
            + f"&langpair={src}|{dst}"
        )
        r = session.get(url, timeout=TIMEOUT).json()
        out = r.get("responseData", {}).get("translatedText") or text
        time.sleep(TRANSLATE_SLEEP)
        return out
    except Exception:
        return text


def clean_html(raw):
    if not raw:
        return ""
    raw = html.unescape(raw)
    soup = BeautifulSoup(raw, "html.parser")
    return soup.get_text(" ", strip=True)


def resolve_url(url):
    """Google News linklerini gerçek haber URL’sine çevir."""
    try:
        # Google News çoğu zaman 302 ile gerçek siteye atar
        resp = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        return resp.url
    except Exception:
        return url


def extract_meta(soup, names):
    for name in names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return ""


def fetch_article(url):
    """Sayfadan özet ve görsel çıkar."""
    try:
        resp = session.get(url, timeout=TIMEOUT)
        if resp.status_code != 200 or not resp.text:
            return {"summary_en": "", "image": ""}
        soup = BeautifulSoup(resp.text, "html.parser")

        # Özet: önce og:description / description, sonra ilk düzgün paragraf
        desc = extract_meta(soup, ["og:description", "twitter:description", "description"])
        if not desc:
            # ilk makul paragraf (çok kısa/uzun olmayan)
            for p in soup.find_all("p"):
                txt = clean_html(str(p))
                if 60 <= len(txt) <= 600:
                    desc = txt
                    break

        # Görsel: og:image/Twitter image
        img = extract_meta(soup, ["og:image", "twitter:image", "twitter:image:src"])

        return {"summary_en": desc or "", "image": img or ""}
    except Exception:
        return {"summary_en": "", "image": ""}


def summarize_tr(text_tr, max_words=60):
    """Türkçe metni 1–3 cümlelik kısa özet gibi kırpar (kelime limiti)."""
    words = text_tr.split()
    if len(words) <= max_words:
        return text_tr
    return " ".join(words[:max_words]) + "…"


def item_key(url):
    try:
        u = urllib.parse.urlparse(url)
        core = f"{u.netloc}{u.path}".lower()
        return hashlib.md5(core.encode("utf-8")).hexdigest()
    except Exception:
        return hashlib.md5(url.encode("utf-8")).hexdigest()


def get_image_from_entry(entry):
    try:
        if "media_content" in entry and entry.media_content:
            return entry.media_content[0].get("url")
    except Exception:
        pass
    try:
        if "media_thumbnail" in entry and entry.media_thumbnail:
            return entry.media_thumbnail[0].get("url")
    except Exception:
        pass
    return ""


# ---------- Ana iş akışı ----------
def fetch_category(urls):
    items = []
    seen = set()
    for feed_url in urls:
        f = feedparser.parse(feed_url)
        for e in f.entries:
            # Başlık & tarih
            original_title = clean_html(getattr(e, "title", ""))
            link = getattr(e, "link", "")

            # Google News yönlendirmesini çöz
            real_link = resolve_url(link)

            key = item_key(real_link or link)
            if key in seen:
                continue
            seen.add(key)

            published = getattr(e, "published", "") or getattr(e, "updated", "") or ""
            summary_from_feed = clean_html(getattr(e, "summary", ""))

            # Sayfadan meta özet + görsel
            art = fetch_article(real_link or link)
            img = art["image"] or get_image_from_entry(e) or "https://via.placeholder.com/800x450?text=Haber"

            # Özet (öncelik: sayfa meta → feed summary)
            summary_en = art["summary_en"] or summary_from_feed

            # Çeviriler
            tr_title = translate(original_title)
            tr_summary_full = translate(summary_en) if summary_en else ""
            tr_summary = summarize_tr(tr_summary_full)

            # Host adı
            try:
                host = urllib.parse.urlparse(real_link or link).netloc.replace("www.", "")
            except Exception:
                host = "Kaynak"

            items.append({
                "title": tr_title,
                "title_en": original_title,
                "summary": tr_summary,              # Kısa Türkçe özet
                "summary_full": tr_summary_full,    # Daha uzun Türkçe (gerekirse gösterilebilir)
                "link": real_link or link,
                "published": published,
                "image": img,
                "source_host": host
            })

            # nazikçe bekle
            time.sleep(REQUEST_SLEEP)

            if len(items) >= PER_SECTION_LIMIT:
                break
        if len(items) >= PER_SECTION_LIMIT:
            break
    return items


def build_json():
    data = {"updated_at": datetime.now(timezone.utc).isoformat()}

    for cat, urls in RSS_FEEDS.items():
        print("→ Kategori:", cat)
        data[cat] = fetch_category(urls)

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✓ data/news.json güncellendi.")


if __name__ == "__main__":
    build_json()
