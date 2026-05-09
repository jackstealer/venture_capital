from github_fetcher import fetch_github
from producthunt_fetcher import fetch_producthunt
from trends_fetcher import fetch_trends
from news_fetcher import fetch_news
from normalizer import normalize
import db_runtime as db

TOPICS = [
    "AI agents",
    "LLM framework",
    "vector database",
    "autonomous AI",
    "multi-agent systems",
    "open source AI",
    "AI infrastructure",
]

GH_MAX_PER_QUERY = 5
PH_MAX_RESULTS = 50
PH_ENRICH_LIMIT = 30

def main():
    print("Starting Venture Alpha Data Collection")
    summary = {
        "github": 0,
        "producthunt": 0,
        "google_trends": 0,
        "newsapi": 0,
    }
    print("Fetching GitHub")
    try:
        gh_items = fetch_github(TOPICS, max_per_query=GH_MAX_PER_QUERY)
        for item in gh_items:
            doc = normalize("github", item)
            db.save(doc)
            summary["github"] += 1
    except Exception as e:
        print(f"Error in GitHub collection: {e}")
    print("Fetching Product Hunt")
    try:
        ph_items = fetch_producthunt(max_results=PH_MAX_RESULTS)
        names = []
        for it in ph_items:
            name = (it or {}).get("name", "") or ""
            if name:
                names.append(name)
        names = list(dict.fromkeys(names))[:PH_ENRICH_LIMIT]
        trend_map = {}
        news_map = {}
        try:
            t_items = fetch_trends(names)
            for t in t_items:
                k = (t or {}).get("keyword", "") or ""
                if k:
                    trend_map[k] = t
        except Exception as e:
            print(f"Product Hunt enrichment (trends) failed: {e}")
        try:
            n_items = fetch_news(names)
            for n in n_items:
                k = (n or {}).get("keyword", "") or ""
                if k:
                    news_map[k] = n
        except Exception as e:
            print(f"Product Hunt enrichment (news) failed: {e}")
        for item in ph_items:
            name = (item or {}).get("name", "") or ""
            enriched = dict(item or {})
            if name and name in trend_map:
                enriched["trend_score"] = float((trend_map[name] or {}).get("trend_score", 0.0) or 0.0)
                enriched["growth_rate"] = float((trend_map[name] or {}).get("growth_rate", 0.0) or 0.0)
            if name and name in news_map:
                enriched["news_mentions"] = int((news_map[name] or {}).get("news_mentions", 0) or 0)
                enriched["sentiment"] = float((news_map[name] or {}).get("avg_sentiment", 0.0) or 0.0)
            doc = normalize("producthunt", enriched)
            db.save(doc)
            summary["producthunt"] += 1
    except Exception as e:
        print(f"Error in Product Hunt collection: {e}")
    print("Fetching Google Trends")
    try:
        trends_keywords = list(dict.fromkeys(TOPICS + names))
        trends_items = fetch_trends(trends_keywords)
        for item in trends_items:
            doc = normalize("google_trends", item)
            db.save(doc)
            summary["google_trends"] += 1
    except Exception as e:
        print(f"Error in Google Trends collection: {e}")
    print("Fetching NewsAPI")
    try:
        news_keywords = list(dict.fromkeys(TOPICS + names))
        news_items = fetch_news(news_keywords)
        for item in news_items:
            doc = normalize("newsapi", item)
            db.save(doc)
            summary["newsapi"] += 1
    except Exception as e:
        print(f"Error in NewsAPI collection: {e}")
    total = sum(summary.values())
    print("=== Venture Alpha Data Collection Complete ===")
    print(f"GitHub:        {summary['github']} saved")
    print(f"Product Hunt:  {summary['producthunt']} saved")
    print(f"Google Trends: {summary['google_trends']} saved")
    print(f"NewsAPI:       {summary['newsapi']} saved")
    print(f"Total:         {total} signals saved to MongoDB Atlas")

if __name__ == "__main__":
    main()
