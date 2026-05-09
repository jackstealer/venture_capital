# data_processing/metrics.py

import os
import certifi
import pandas as pd
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB Atlas (certifi fixes TLS CA issues on Windows)
client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = client["venture_alpha"]
collection = db["signals"]


def fetch_raw_projects() -> pd.DataFrame:
    """
    Pull all documents from the signals collection.
    MongoDB returns dicts — we convert straight to DataFrame.

    Member 1's schema fields we care about:
      source, repo_name, description, stars,
      contributors, created_utc, tags, url, extra, num_comments
    """
    docs = list(collection.find({}))
    df = pd.DataFrame(docs)

    # MongoDB _id is not JSON-serializable, drop it
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    return df


def calculate_star_velocity(stars, created_utc) -> float:
    """
    star_velocity = stars / age_in_days

    created_utc is a Unix timestamp (integer) from Member 1's schema.
    Convert it to datetime first.
    """
    try:
        stars = int(stars) if stars else 0
        created_dt = datetime.fromtimestamp(int(created_utc), tz=timezone.utc)
        today = datetime.now(timezone.utc)
        age_days = (today - created_dt).days
        if age_days <= 0:
            age_days = 1
        return round(stars / age_days, 4)
    except Exception:
        return 0.0


def calculate_contributor_diversity(contributors, stars) -> float:
    """
    contributor_diversity = contributors / max(stars, 1)
    Capped at 1.0.
    """
    try:
        contributors = int(contributors) if contributors else 0
        stars = int(stars) if stars else 1
        if stars == 0:
            stars = 1
        diversity = contributors / stars
        return round(min(diversity, 1.0), 4)
    except Exception:
        return 0.0


def calculate_repo_age_days(created_utc) -> int:
    try:
        created_dt = datetime.fromtimestamp(int(created_utc), tz=timezone.utc)
        return (datetime.now(timezone.utc) - created_dt).days
    except Exception:
        return 0


def normalize(value: float, min_val: float, max_val: float) -> float:
    if max_val == min_val:
        return 0.0
    return round((value - min_val) / (max_val - min_val), 4)


def safe_float(val, default=0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(val) if val else default
    except (ValueError, TypeError):
        return default


def extract_extra_metrics(row) -> dict:
    """
    Pull new metrics from the 'extra' embedded document.
    Works for all sources — fields that don't exist just default to 0.
    """
    extra = row.get("extra")
    if pd.isna(extra) or not isinstance(extra, dict):
        extra = {}

    return {
        "trend_score":    safe_float(extra.get("trend_score", 0)),
        "trend_growth":   safe_float(extra.get("growth_rate", 0)),
        "media_sentiment": safe_float(extra.get("sentiment", 0)),
        "news_mentions":  safe_float(extra.get("news_mentions", 0)),
        "ph_votes":       safe_float(extra.get("votes", 0)),
        "ph_upvote_ratio": safe_float(extra.get("upvote_ratio", 0)),
    }


def normalize_column(df: pd.DataFrame, col: str) -> pd.Series:
    """Normalize a column to 0-1 range across the dataset."""
    min_val = df[col].min()
    max_val = df[col].max()
    return df[col].apply(lambda v: normalize(v, min_val, max_val))


def process_all_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # ── Existing metrics (unchanged) ──
    df["star_velocity"] = df.apply(
        lambda row: calculate_star_velocity(row.get("stars", 0), row.get("created_utc", 0)),
        axis=1
    )

    df["contributor_diversity"] = df.apply(
        lambda row: calculate_contributor_diversity(
            row.get("contributors", 0), row.get("stars", 1)
        ),
        axis=1
    )

    if "created_utc" in df.columns:
        df["repo_age_days"] = df["created_utc"].apply(calculate_repo_age_days)
    else:
        df["repo_age_days"] = 0

    # Normalize star_velocity
    min_vel = df["star_velocity"].min()
    max_vel = df["star_velocity"].max()
    df["star_velocity_norm"] = df["star_velocity"].apply(
        lambda v: normalize(v, min_vel, max_vel)
    )

    # ── New multi-source metrics from 'extra' field ──
    extra_rows = df.apply(extract_extra_metrics, axis=1, result_type="expand")
    for col in extra_rows.columns:
        df[col] = extra_rows[col]

    # Product Hunt engagement = num_comments / max(votes, 1)
    df["ph_engagement"] = df.apply(
        lambda row: round(
            safe_float(row.get("num_comments", 0)) / max(safe_float(row.get("ph_votes", 0)), 1),
            4
        ),
        axis=1
    )

    # ── Normalize new columns to 0-1 ──
    for col in ["trend_score", "trend_growth", "news_mentions", "ph_votes"]:
        df[f"{col}_norm"] = normalize_column(df, col)

    # media_sentiment and ph_engagement are already ratios, clamp to [0, 1]
    df["media_sentiment"] = df["media_sentiment"].clip(0, 1)
    df["ph_engagement"] = df["ph_engagement"].clip(0, 1)

    print(f"[metrics.py] Processed {len(df)} signals with multi-source metrics.")
    return df


if __name__ == "__main__":
    df = fetch_raw_projects()
    df = process_all_metrics(df)
    if not df.empty:
        cols = ["repo_name", "source", "star_velocity", "contributor_diversity",
                "trend_score", "ph_votes", "news_mentions"]
        cols = [c for c in cols if c in df.columns]
        print(df[cols].head(10))
