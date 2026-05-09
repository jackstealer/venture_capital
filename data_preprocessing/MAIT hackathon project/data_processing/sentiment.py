# data_processing/sentiment.py

import pandas as pd
from textblob import TextBlob


def analyze_sentiment(text: str) -> float:
    """
    Returns a sentiment score from 0.0 (very negative) to 1.0 (very positive).
    Neutral = 0.5.
    """
    if not text or len(str(text).strip()) == 0:
        return 0.5
    blob = TextBlob(str(text))
    polarity = blob.sentiment.polarity        # range: -1.0 to +1.0
    return round((polarity + 1) / 2, 4)      # shift to 0.0 to 1.0


def run_sentiment_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Member 1's schema has a 'description' field on every document —
    repo description for GitHub, post body for HackerNews, snippet for Exa.

    We combine description + repo_name for a richer signal.
    """
    scores = []

    for _, row in df.iterrows():
        texts = []

        if row.get("description"):
            texts.append(str(row["description"]))
        if row.get("repo_name"):
            texts.append(str(row["repo_name"]))

        if texts:
            combined = " ".join(texts)
            score = analyze_sentiment(combined)
        else:
            score = 0.5   # neutral default

        scores.append(score)

    df["social_sentiment"] = scores
    print(f"[sentiment.py] Sentiment scored for {len(df)} signals.")
    return df


if __name__ == "__main__":
    samples = [
        {"repo_name": "LangGraph", "description": "Incredible multi-agent framework everyone is using"},
        {"repo_name": "BrokenLib", "description": "Buggy, undocumented, abandoned project"},
        {"repo_name": "SomeTool",  "description": "A tool for processing data pipelines"},
    ]
    df = pd.DataFrame(samples)
    df = run_sentiment_pipeline(df)
    print(df[["repo_name", "social_sentiment"]])
