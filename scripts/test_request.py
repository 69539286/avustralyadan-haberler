import requests

print("İnternet test başlıyor...")

urls = [
    "https://news.google.com/rss?hl=en-AU&gl=AU&ceid=AU:en",
    "https://www.reuters.com/markets/australia/rss",
    "https://www.abc.net.au/news/feed/51120/rss.xml"
]

for u in urls:
    print("\n---", u)
    try:
        r = requests.get(u, timeout=10)
        print("Status:", r.status_code)
        print("Length:", len(r.text))
    except Exception as e:
        print("Hata:", e)
