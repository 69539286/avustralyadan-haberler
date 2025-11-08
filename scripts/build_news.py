#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os, time, datetime, re
from urllib.parse import urlparse
import feedparser

# KATEGORİ → RSS kaynakları (örnekler, dilediğin gibi ekleyip çıkarabilirsin)
SOURCES = {
    "economy": [
        "https://www.rba.gov.au/rss/rss.xml",
        "https://www.afr.com/rss",
        "https://www.abc.net.au/news/feed/2942460/rss.xml",
    ],
    "government": [
        "https://www.pm.gov.au/media/rss.xml",
        "https://www.abc.net.au/news/politics/rss",
        "https://minister.homeaffairs.gov.au/Pages/Media-Releases.aspx?rss=1",
    ],
    "realestate": [
        "https://www.domain.com.au/news/feed/",
        "https://www.realestate.com.au/news/feed/",
    ],
    "immigration": [
        "https://immi.homeaffairs.gov.au/rss-feed",
        "https://www.sbs.com.au/language/turkish/en/news/topic/migration/rss.xml",
    ],
    "tr_sports": [
        "https://www.fanatik.com.tr/rss",
        "https://www.ntvspor.net/rss",
    ],
    "new_developments": [
        "https://www.abc.net.au/news/science/rss",
        "https://www.abc.net.au/news/justin/rss",
    ],
    "socialist": [
        "https://www.greenleft.org.au/rss.xml",
    ],
    "jobs": [
        "https://www.abs.gov.au/rss/media-releases",  # İş/işsizlik verileri
        "https://www.abc.net.au/news/business/rss",
    ],
}

OUT_DIR = os.path.join("data")
OUT_FILE = os.path.join(OUT_DIR, "news.json")

def strip_html(s):
    if not s: return ""
    return re.sub(r"<[^>]+>", "", s)

def to_local_iso(ts_struct):
    try:
        # feedparser published_parsed → time.struct_time (UTC olabiliyor)
        dt = datetime.datetime.fromtimestamp(time.mktime(ts_struct))
        # Melbourne (Australia/Melbourne) ofsetini basit tutuyoruz:
        # GitHub Actions UTC’de çalışır; ISO string yeterli.
        return dt.isoformat(sep=" ", timespec="minutes")
    except Exception:
        return ""

def parse_feed(url, limit=20):
    d = feedparser.parse(url)
    items = []
    for e in d.entries[:limit]:
        title = e.get("title", "").strip()
        link = e.get("link", "")
        summary = strip_html(e.get("summary", "") or e.get("description", ""))
        published = ""
        published_local = ""
        if e.get("published_parsed"):
            published = datetime.datetime.utcfromtimestamp(
                time.mktime(e.published_parsed)
            ).isoformat(sep=" ", timespec="minutes")
            published_local = to_local_iso(e.published_parsed)
        host = urlparse(link).netloc.replace("www.", "")
        items.append({
            "title": title,
            "url": link,
            "summary": summary,
            "published": published,
            "published_local": published_local,
            "source": host or urlparse(url).netloc.replace("www.",""),
        })
    return items

def build_all():
    os.makedirs(OUT_DIR, exist_ok=True)
    payload = {"generated_at": datetime.datetime.utcnow().isoformat() + "Z"}
    for cat, feeds in SOURCES.items():
        bucket = []
        for f in feeds:
            try:
                bucket.extend(parse_feed(f))
            except Exception as ex:
                bucket.append({
                    "title": f"Kaynak okunamadı: {f}",
                    "url": f, "summary": str(ex), "source": "hata"
                })
        # basitçe başlığa göre benzersizleştir
        seen = set(); uniq = []
        for it in bucket:
            key = (it.get("title") or "").strip()
            if key and key not in seen:
                uniq.append(it); seen.add(key)
        payload[cat] = uniq
    with open(OUT_FILE, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)
    print(f"Wrote {OUT_FILE} with {sum(len(payload[k]) for k in SOURCES.keys())} items.")

if __name__ == "__main__":
    build_all()
