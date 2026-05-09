import os
import requests
from textblob import TextBlob

API_ENDPOINT = "https://newsapi.org/v2/everything"

def fetch_news(keywords: list) -> list:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("Missing NEWS_API_KEY, skipping NewsAPI fetch")
        return []
    if not isinstance(keywords, list):
        return []
    results = []
    for keyword in keywords:
        params = {
            "q": str(keyword),
            "sortBy": "publishedAt",
            "pageSize": 20,
            "language": "en",
            "apiKey": api_key,
        }
        try:
            res = requests.get(API_ENDPOINT, params=params)
            res.raise_for_status()
            data = res.json() or {}
            articles = data.get("articles", []) or []
            titles = []
            sentiments = []
            for article in articles:
                title = (article or {}).get("title", "") or ""
                if title:
                    titles.append(title)
                    try:
                        polarity = float(TextBlob(title).sentiment.polarity)
                    except Exception:
                        polarity = 0.0
                    sentiments.append(polarity)
            news_mentions = len(titles)
            if sentiments:
                avg_sentiment = float(sum(sentiments) / len(sentiments))
            else:
                avg_sentiment = 0.0
            results.append(
                {
                    "keyword": str(keyword),
                    "articles": titles,
                    "news_mentions": int(news_mentions),
                    "avg_sentiment": float(avg_sentiment),
                }
            )
        except Exception as e:
            print(f"NewsAPI fetch failed for '{keyword}': {e}")
            continue
    return results

if __name__ == "__main__":
    items = fetch_news(["AI agents"])
    print(len(items))

