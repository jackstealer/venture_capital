from datetime import datetime

def normalize(source, raw):
    source_name = str(source) if source is not None else ""
    repo_name = ""
    description = ""
    url = ""
    stars = 0
    contributors = 0
    num_comments = 0
    author = ""
    created_utc = 0
    tags = []
    trend_score = 0.0
    growth_rate = 0.0
    sentiment = 0.0
    news_mentions = 0
    votes = 0
    raw = raw or {}
    keyword = ""
    if source_name == "github":
        repo_name = raw.get("name", "") or ""
        description = raw.get("description", "") or ""
        url = raw.get("html_url", "") or ""
        stars = int(raw.get("stargazers_count", 0) or 0)
        contributors = int(raw.get("contributor_count", 0) or 0)
        num_comments = 0
        author = raw.get("owner_login", "") or ""
        created_str = raw.get("created_at", "") or ""
        if created_str:
            try:
                dt = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ")
                created_utc = int(dt.timestamp())
            except Exception:
                created_utc = 0
        tags = raw.get("topics", []) or []
    elif source_name == "producthunt":
        repo_name = raw.get("name", "") or ""
        description = raw.get("tagline", "") or ""
        url = raw.get("website", "") or ""
        stars = int(raw.get("votesCount", 0) or 0)
        votes = int(raw.get("votesCount", 0) or 0)
        num_comments = int(raw.get("commentsCount", 0) or 0)
        trend_score = float(raw.get("trend_score", 0.0) or 0.0)
        growth_rate = float(raw.get("growth_rate", 0.0) or 0.0)
        sentiment = float(raw.get("sentiment", 0.0) or 0.0)
        news_mentions = int(raw.get("news_mentions", 0) or 0)
        created_str = raw.get("createdAt", "") or ""
        if created_str:
            try:
                dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                created_utc = int(dt.timestamp())
            except Exception:
                created_utc = 0
        topics_edges = (raw.get("topics") or {}).get("edges", []) or []
        tags = []
        for edge in topics_edges:
            node = (edge or {}).get("node") or {}
            name = node.get("name", "") or ""
            if name:
                tags.append(name)
    elif source_name == "google_trends":
        keyword = raw.get("keyword", "") or ""
        repo_name = keyword
        description = ""
        url = f"google_trends:{keyword}" if keyword else "google_trends:"
        author = ""
        trend_score = float(raw.get("trend_score", 0.0) or 0.0)
        growth_rate = float(raw.get("growth_rate", 0.0) or 0.0)
        tags = [keyword] if keyword else []
    elif source_name == "newsapi":
        keyword = raw.get("keyword", "") or ""
        repo_name = keyword
        description = ""
        url = f"newsapi:{keyword}" if keyword else "newsapi:"
        author = ""
        news_mentions = int(raw.get("news_mentions", 0) or 0)
        sentiment = float(raw.get("avg_sentiment", 0.0) or 0.0)
        tags = [keyword] if keyword else []
    result = {
        "source": source_name,
        "repo_name": repo_name or "",
        "description": description or "",
        "url": url or (f"{source_name}:{repo_name}" if repo_name else f"{source_name}:"),
        "stars": int(stars or 0),
        "contributors": int(contributors or 0),
        "num_comments": int(num_comments or 0),
        "author": author or "",
        "created_utc": int(created_utc or 0),
        "tags": tags or [],
        "fetched_at": datetime.utcnow(),
        "extra": {
            "trend_score": float(trend_score or 0.0),
            "growth_rate": float(growth_rate or 0.0),
            "sentiment": float(sentiment or 0.0),
            "news_mentions": int(news_mentions or 0),
            "votes": int(votes or 0),
        },
    }
    return result
