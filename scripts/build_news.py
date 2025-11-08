import feedparser
import json
from googletrans import Translator
import re

translator = Translator()

RSS_FEEDS = {
    "ekonomi": [
        "https://news.google.com/rss/search?q=Australia+economy&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "hukumet": [
        "https://news.google.com/rss/search?q=Australia+government&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "ev": [
        "https://news.google.com/rss/search?q=Australia+housing+market&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "goc": [
        "https://news.google.com/rss/search?q=Australia+immigration&hl=en-AU&gl=AU&ceid=AU:en"
    ],
    "gundem": [
        "https://news.google.com/rss/search?q=Australia+breaking+news&hl=en-AU&gl=AU&ceid=AU:en"
    ]
}

def clean_html(text):
    return re.sub('<[^<]+?>', '', text)

def summarize(text):
    text = text.strip()
    sentences = re.split(r'\. ', text)
    if len(sentences) > 2:
        return sentences[0] + ". " + sentences[1] + "."
    return text

def fetch_and_translate(entry):
    title = clean_html(entry.get("title", ""))
    summary = clean_html(entry.get("summary", ""))
    link = entry.get("link", "")

    # İngilizceyi Türkçeye çevir
    try:
        tr_title = translator.translate(title, dest="tr").text
        tr_summary = translator.translate(summary, dest="tr").text
    except:
        tr_title = title
        tr_summary = summary

    # Özet oluştur
    tr_summary = summarize(tr_summary)

    return {
        "title": tr_title,
        "link": link,
        "summary": tr_summary,
        "image": "https://via.placeholder.com/600x400?text=Haber"
    }

def generate_news_json():
    all_news = {}

    for category, feeds in RSS_FEEDS.items():
        cat_news = []

        for url in feeds:
            data = feedparser.parse(url)

            for entry in data.entries[:10]:  # ilk 10 haber
                item = fetch_and_translate(entry)
                cat_news.append(item)

        all_news[category] = cat_news

    all_news["generated_at"] = "otomatik"

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    generate_news_json()
