# data_processing/conviction_score.py

import os
import sys
import certifi
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Ensure sibling modules (metrics, sentiment) are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metrics import fetch_raw_projects, process_all_metrics
from sentiment import run_sentiment_pipeline

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = client["venture_alpha"]
collection = db["signals"]


W_DEVELOPER_ACTIVITY  = 0.25  
W_MARKET_DEMAND       = 0.25   
W_COMMUNITY_INTEREST  = 0.20   
W_MEDIA_PRESENCE      = 0.20   
W_STARTUP_ACTIVITY    = 0.10   
INVESTMENT_LEAD_THRESHOLD = 0.85

SOURCE_WEIGHTS = {
    "github":        1.0,   
    "hackernews":    0.8,   
    "producthunt":   0.9,  
    "google_trends": 0.7,   
    "newsapi":       0.75,  
    "exa":           0.6,   
}


def apply_source_weight(score: float, source: str) -> float:
    """
    Multiply the raw conviction score by a source trust factor.
    """
    weight = SOURCE_WEIGHTS.get(source, 0.7)
    return round(score * weight, 4)


def score_developer_activity(row) -> float:
    """
    Pillar 1: Developer Activity (GitHub-centric)
    0.7 × star_velocity_norm + 0.3 × contributor_diversity
    """
    sv = float(row.get("star_velocity_norm", 0))
    cd = float(row.get("contributor_diversity", 0))
    return round(0.7 * sv + 0.3 * cd, 4)


def score_market_demand(row) -> float:
    """
    Pillar 2: Market Demand (Google Trends)
    0.6 × trend_score_norm + 0.4 × trend_growth_norm
    """
    ts = float(row.get("trend_score_norm", 0))
    tg = float(row.get("trend_growth_norm", 0))
    return round(0.6 * ts + 0.4 * tg, 4)


def score_community_interest(row) -> float:
    """
    Pillar 3: Community Interest (Product Hunt)
    0.7 × ph_votes_norm + 0.3 × ph_engagement
    """
    pv = float(row.get("ph_votes_norm", 0))
    pe = float(row.get("ph_engagement", 0))
    return round(0.7 * pv + 0.3 * pe, 4)


def score_media_presence(row) -> float:
    """
    Pillar 4: Media Presence (NewsAPI)
    0.5 × news_mentions_norm + 0.5 × media_sentiment
    """
    nm = float(row.get("news_mentions_norm", 0))
    ms = float(row.get("media_sentiment", 0))
    return round(0.5 * nm + 0.5 * ms, 4)


def score_startup_activity(row) -> float:
    """
    Pillar 5: Startup Activity (composite proxy — no Crunchbase)
    Uses trend momentum + community engagement as a proxy for
    startup traction. 0.5 × trend_growth_norm + 0.5 × ph_engagement
    """
    tg = float(row.get("trend_growth_norm", 0))
    pe = float(row.get("ph_engagement", 0))
    return round(0.5 * tg + 0.5 * pe, 4)


def calculate_conviction_score(dev, market, community, media, startup) -> float:
    """
    CS = 0.25×developer_activity + 0.25×market_demand
       + 0.20×community_interest + 0.20×media_presence
       + 0.10×startup_activity
    All inputs and output: 0.0 to 1.0
    """
    score = (
        W_DEVELOPER_ACTIVITY  * float(dev)
        + W_MARKET_DEMAND     * float(market)
        + W_COMMUNITY_INTEREST * float(community)
        + W_MEDIA_PRESENCE    * float(media)
        + W_STARTUP_ACTIVITY  * float(startup)
    )
    return round(score, 4)


def save_scores_to_mongo(df: pd.DataFrame):
    """
    Write scores back into MongoDB.
    Match on 'url' as primary key.  Persist all 5 pillar scores.
    """
    updated = 0
    skipped = 0
    for _, row in df.iterrows():
        url = row.get("url")
        if not url:
            skipped += 1
            continue

        collection.update_one(
            {"url": url},
            {"$set": {
                "conviction_score":       float(row["conviction_score"]),
                "is_investment_lead":     bool(row["is_investment_lead"]),
                # Pillar scores
                "developer_activity":     float(row.get("developer_activity", 0)),
                "market_demand":          float(row.get("market_demand", 0)),
                "community_interest":     float(row.get("community_interest", 0)),
                "media_presence":         float(row.get("media_presence", 0)),
                "startup_activity":       float(row.get("startup_activity", 0)),
                # Legacy fields kept for backward compat
                "social_sentiment":       float(row.get("social_sentiment", 0)),
                "star_velocity":          float(row.get("star_velocity", 0)),
                "contributor_diversity":  float(row.get("contributor_diversity", 0)),
                "star_velocity_norm":     float(row.get("star_velocity_norm", 0)),
            }},
            upsert=False
        )
        updated += 1

    print(f"[conviction_score.py] Updated {updated} documents in MongoDB.")
    if skipped:
        print(f"[conviction_score.py] Skipped {skipped} documents (no 'url' field).")


def run_full_pipeline():
    print("=" * 55)
    print("Member 2 pipeline starting...")
    print("=" * 55)

    # 1. Fetch
    df = fetch_raw_projects()
    if df.empty:
        print("No signals found in MongoDB. Check MONGO_URI and collection name.")
        return

    print(f"Fetched {len(df)} signals from MongoDB Atlas.")

    # 2. Metrics (now includes multi-source extraction)
    df = process_all_metrics(df)

    # 3. Sentiment
    df = run_sentiment_pipeline(df)

    # 4. Compute 5-pillar scores
    pillar_scores = {"developer_activity": [], "market_demand": [],
                     "community_interest": [], "media_presence": [],
                     "startup_activity": []}
    conviction_scores = []
    flags = []

    for _, row in df.iterrows():
        dev     = score_developer_activity(row)
        market  = score_market_demand(row)
        comm    = score_community_interest(row)
        media   = score_media_presence(row)
        startup = score_startup_activity(row)

        cs = apply_source_weight(
            calculate_conviction_score(dev, market, comm, media, startup),
            row.get("source", "exa")
        )

        pillar_scores["developer_activity"].append(dev)
        pillar_scores["market_demand"].append(market)
        pillar_scores["community_interest"].append(comm)
        pillar_scores["media_presence"].append(media)
        pillar_scores["startup_activity"].append(startup)
        conviction_scores.append(cs)
        flags.append(cs >= INVESTMENT_LEAD_THRESHOLD)

    for col, vals in pillar_scores.items():
        df[col] = vals
    df["conviction_score"]   = conviction_scores
    df["is_investment_lead"] = flags

    # 5. Print ranked results
    print("\n" + "=" * 55)
    print("CONVICTION SCORE RESULTS (top 10)")
    print("=" * 55)

    display_cols = ["repo_name", "source", "developer_activity", "market_demand",
                    "community_interest", "media_presence", "startup_activity",
                    "conviction_score", "is_investment_lead"]
    display_cols = [c for c in display_cols if c in df.columns]

    top = df[display_cols] \
            .sort_values("conviction_score", ascending=False) \
            .head(10)
    print(top.to_string(index=False))

    leads = df[df["is_investment_lead"]]
    print(f"\n>>> {len(leads)} INVESTMENT LEADS (score >= {INVESTMENT_LEAD_THRESHOLD})")
    for _, lead in leads.iterrows():
        src = lead.get("source", "unknown")
        name = lead.get("repo_name", "unnamed")
        print(f"    [{str(src).upper()}] {name} — {lead['conviction_score']}")

    # 6. Save back to MongoDB
    try:
        save_scores_to_mongo(df)
    except Exception as e:
        print(f"\n[WARNING] Could not save scores to MongoDB: {e}")
        print("Your DB user may only have read permissions. Update role to 'Read and Write' in Atlas → Database Access.")
    print("\nMember 2 pipeline complete.")
    return df


if __name__ == "__main__":
    run_full_pipeline()
