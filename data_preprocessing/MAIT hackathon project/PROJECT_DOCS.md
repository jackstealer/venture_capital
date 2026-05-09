# 🚀 Venture Alpha — Project Documentation

> **Venture Alpha** is an AI-driven data pipeline that discovers promising open-source projects and startup signals from multiple sources (GitHub, Hacker News, Exa), then scores them using quantitative metrics and NLP sentiment analysis to surface high-conviction venture capital investment leads.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Architecture & Data Flow](#-architecture--data-flow)
3. [Tech Stack](#-tech-stack)
4. [APIs & External Services](#-apis--external-services)
5. [Project Structure](#-project-structure)
6. [Module Breakdown](#-module-breakdown)
7. [Data Schema](#-data-schema)
8. [Conviction Score Formula](#-conviction-score-formula)
9. [Environment Setup](#-environment-setup)
10. [How to Run](#-how-to-run)
11. [Troubleshooting](#-troubleshooting)
12. [Contributing](#-contributing)

---

## 🧭 Project Overview

Venture Alpha is a **two-member hackathon project** built for the MAIT hackathon:

| Role | Responsibility |
|------|---------------|
| **Member 1** | Data collection — scrapes/fetches signals from GitHub, Hacker News, and Exa, then stores raw documents in MongoDB Atlas. |
| **Member 2** | Data processing — pulls raw signals from MongoDB, calculates quantitative metrics, runs sentiment analysis, computes a weighted **Conviction Score**, and writes results back to the database. |

**This repository is Member 2's codebase** — the data-processing and scoring pipeline.

### What It Does

1. **Fetches** raw project/startup signal documents from a shared MongoDB Atlas database.
2. **Calculates metrics** — star velocity, contributor diversity, repo age.
3. **Runs sentiment analysis** on project descriptions using NLP (TextBlob).
4. **Computes a Conviction Score** (0.0–1.0) using a weighted formula.
5. **Applies source-trust weighting** — GitHub signals are trusted more than Exa news snippets.
6. **Flags investment leads** (score ≥ 0.85).
7. **Writes scores back** to MongoDB so they're available to the full team.

---

## 🏗 Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                   MongoDB Atlas                         │
│              Database: venture_alpha                    │
│              Collection: signals                        │
│                                                         │
│  ┌──────────────┐          ┌──────────────────────────┐ │
│  │  Member 1    │  writes  │  Raw signal documents    │ │
│  │  (Scraper)   │ ───────► │  (GitHub, HN, Exa)      │ │
│  └──────────────┘          └──────────┬───────────────┘ │
│                                       │ reads           │
│                            ┌──────────▼───────────────┐ │
│                            │  Member 2 (This Repo)    │ │
│                            │  Data Processing Pipeline│ │
│                            └──────────┬───────────────┘ │
│                                       │ writes back     │
│                            ┌──────────▼───────────────┐ │
│                            │  Enriched documents with │ │
│                            │  conviction_score,       │ │
│                            │  social_sentiment, etc.  │ │
│                            └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Pipeline Stages (in order)

```
fetch_raw_projects()          # 1. Pull all signals from MongoDB
        │
        ▼
process_all_metrics()         # 2. Compute star_velocity, contributor_diversity, repo_age
        │
        ▼
run_sentiment_pipeline()      # 3. NLP sentiment on description + repo_name
        │
        ▼
calculate_conviction_score()  # 4. Weighted score + source trust multiplier
        │
        ▼
save_scores_to_mongo()        # 5. Write enriched data back to MongoDB
```

---

## 🛠 Tech Stack

| Technology | Version Info | Purpose |
|---|---|---|
| **Python 3** | 3.10+ recommended | Core programming language |
| **MongoDB Atlas** | Cloud (M0 Free Tier) | Shared cloud database (NoSQL) |
| **PyMongo** (`pymongo[srv]`) | Latest | Python driver for MongoDB, SRV connection support |
| **dnspython** | Latest | DNS resolution for MongoDB SRV connection strings |
| **Pandas** | Latest | Data manipulation and DataFrame processing |
| **NumPy** | Latest | Numerical operations (Pandas dependency) |
| **TextBlob** | Latest | NLP library for sentiment analysis |
| **python-dotenv** | Latest | Loads `.env` variables into `os.environ` |
| **certifi** | Latest | Mozilla CA bundle — fixes TLS/SSL certificate issues on Windows |

---

## 🔌 APIs & External Services

### 1. MongoDB Atlas (Database-as-a-Service)

| Detail | Value |
|---|---|
| **Service** | [MongoDB Atlas](https://www.mongodb.com/atlas) |
| **Cluster** | `Cluster0` on shared tier |
| **Database** | `venture_alpha` |
| **Collection** | `signals` |
| **Connection** | SRV connection string via `MONGO_URI` env variable |
| **Auth** | Username + password embedded in connection URI |
| **TLS** | Uses `certifi` CA bundle for Windows compatibility |

**How it's used:**
- `metrics.py` — reads all documents from the `signals` collection
- `conviction_score.py` — writes computed scores back to each document (matched by `url` field)

### 2. TextBlob (NLP — No external API call)

TextBlob is a **local NLP library** (no network calls). It uses a pre-trained model bundled with the package to compute:
- **Polarity** (−1.0 to +1.0) — how positive/negative the text is
- This is shifted to a 0.0 to 1.0 scale for our pipeline

### 3. Data Sources (Member 1 — upstream)

Member 1's scraper feeds the database from these sources. Member 2's code **reads** this data but does not call these APIs directly:

| Source | What It Provides | Key Fields |
|---|---|---|
| **GitHub API** | Repository metadata | `stars`, `contributors`, `repo_name`, `description`, `tags`, `url`, `created_utc` |
| **Hacker News (HN)** | Tech community posts | `stars` (upvotes), `description` (post body), `repo_name`, `url`, `created_utc` |
| **Exa API** | AI-powered news/article search | `description` (snippet), `repo_name`, `tags`, `url`, `created_utc` |

---

## 📁 Project Structure

```
MAIT hackathon project/
│
├── .env                          # Environment variables (MONGO_URI) — NEVER commit this
├── .gitignore                    # Excludes .env from version control
├── requirements.txt              # Python dependencies
│
└── data_processing/              # Core Python package
    ├── __init__.py               # Makes this a Python package
    ├── metrics.py                # Quantitative metric calculations
    ├── sentiment.py              # NLP sentiment analysis
    └── conviction_score.py       # Main pipeline orchestrator + scoring
```

---

## 📦 Module Breakdown

### `metrics.py` — Quantitative Metrics Engine

**Purpose:** Connects to MongoDB, fetches raw signal data, and computes quantitative metrics.

| Function | Description |
|---|---|
| `fetch_raw_projects()` | Pulls all documents from `signals` collection → returns a Pandas DataFrame |
| `calculate_star_velocity(stars, created_utc)` | `stars ÷ age_in_days` — measures growth momentum |
| `calculate_contributor_diversity(contributors, stars)` | `contributors ÷ stars` (capped at 1.0) — measures team breadth |
| `calculate_repo_age_days(created_utc)` | Converts Unix timestamp to age in days |
| `normalize(value, min_val, max_val)` | Min-max normalization to 0.0–1.0 range |
| `process_all_metrics(df)` | Orchestrates all metric calculations on the DataFrame |

---

### `sentiment.py` — NLP Sentiment Analysis

**Purpose:** Uses TextBlob to score the sentiment of each signal's description.

| Function | Description |
|---|---|
| `analyze_sentiment(text)` | Takes any text → returns sentiment score 0.0 (negative) to 1.0 (positive), 0.5 = neutral |
| `run_sentiment_pipeline(df)` | Iterates over all rows, combines `description` + `repo_name`, scores sentiment, adds `social_sentiment` column |

**How sentiment is calculated:**
```
TextBlob polarity: -1.0 to +1.0
Our scale:         (polarity + 1) / 2  →  0.0 to 1.0
```

---

### `conviction_score.py` — Main Pipeline & Scoring Engine

**Purpose:** The entry point. Orchestrates the entire pipeline and computes the final Conviction Score.

| Function | Description |
|---|---|
| `apply_source_weight(score, source)` | Multiplies score by source trust factor (GitHub=1.0, HN=0.8, Exa=0.6) |
| `get_news_mentions_score(tags)` | Scores relevance based on high-signal tags (AI, LLM, YCombinator, etc.) |
| `calculate_conviction_score(sv, diversity, sentiment, news)` | Weighted sum of all four factors |
| `save_scores_to_mongo(df)` | Writes scores back to MongoDB, matched by `url` field |
| `run_full_pipeline()` | **Main entry point** — runs all stages in sequence |

---

## 📊 Data Schema

### Input Document (from MongoDB `signals` collection)

```json
{
  "source":        "github | hackernews | exa",
  "repo_name":     "project-name",
  "description":   "A brief description of the project...",
  "stars":         1500,
  "contributors":  42,
  "created_utc":   1700000000,
  "tags":          ["AI", "LLM", "open-source"],
  "url":           "https://github.com/org/repo"
}
```

### Output Fields (added by this pipeline)

| Field | Type | Description |
|---|---|---|
| `star_velocity` | float | Raw stars ÷ age in days |
| `star_velocity_norm` | float | Normalized (0.0–1.0) across all signals |
| `contributor_diversity` | float | Contributors ÷ stars (capped at 1.0) |
| `repo_age_days` | int | Age of the project in days |
| `social_sentiment` | float | NLP sentiment score (0.0–1.0) |
| `conviction_score` | float | Final weighted score (0.0–1.0) |
| `is_investment_lead` | bool | `True` if conviction_score ≥ 0.85 |

---

## 🧮 Conviction Score Formula

```
Conviction Score = 0.40 × star_velocity_norm
                 + 0.30 × contributor_diversity
                 + 0.20 × social_sentiment
                 + 0.10 × news_mentions_score
```

The raw score is then **multiplied by a source trust weight:**

| Source | Weight | Rationale |
|---|---|---|
| GitHub | 1.0 | Real code activity — most reliable |
| Hacker News | 0.8 | Developer discussion — high signal |
| Exa | 0.6 | News/articles — useful but noisier |

A signal with a final score **≥ 0.85** is flagged as an **Investment Lead**.

---

## ⚙ Environment Setup

### Prerequisites

- **Python 3.10+** installed
- **pip** (Python package manager)
- **Internet connection** (to reach MongoDB Atlas)
- Access to the shared **MongoDB Atlas cluster** (connection URI provided by the team)

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/arpitpandey0307/venture-capital.git
cd venture-capital

# 2. (Recommended) Create a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download TextBlob corpora (required on first run)
python -m textblob.download_corpora

# 5. Create the .env file
#    Create a file named .env in the project root with:
#    MONGO_URI=mongodb+srv://<username>:<password>@cluster0.vcwoaoz.mongodb.net/?appName=Cluster0
#
#    ⚠️ Get the actual credentials from your team lead. NEVER commit .env to Git.
```

### Environment Variables

| Variable | Description | Example |
|---|---|---|
| `MONGO_URI` | MongoDB Atlas SRV connection string | `mongodb+srv://user:pass@cluster0.vcwoaoz.mongodb.net/?appName=Cluster0` |

---

## ▶ How to Run

### Run the Full Pipeline

```bash
python data_processing/conviction_score.py
```

This will:
1. Connect to MongoDB Atlas
2. Fetch all signals
3. Calculate metrics (star velocity, contributor diversity, repo age)
4. Run sentiment analysis
5. Compute conviction scores
6. Print the top 10 ranked signals to the console
7. Save enriched scores back to MongoDB

### Run Individual Modules (for testing/debugging)

```bash
# Test metrics calculation only
python data_processing/metrics.py

# Test sentiment analysis with sample data
python data_processing/sentiment.py
```

### Expected Console Output

```
=======================================================
Member 2 pipeline starting...
=======================================================
Fetched 25 signals from MongoDB Atlas.
[metrics.py] Processed 25 signals.
[sentiment.py] Sentiment scored for 25 signals.

=======================================================
CONVICTION SCORE RESULTS (top 10)
=======================================================
    repo_name    source  star_velocity  social_sentiment  conviction_score  is_investment_lead
   LangGraph    github         12.34              0.82              0.91                True
   AutoGPT     github          8.21              0.75              0.87                True
   ...

>>> 2 INVESTMENT LEADS (score >= 0.85)
    [GITHUB] LangGraph — 0.91
    [GITHUB] AutoGPT — 0.87

[conviction_score.py] Updated 25 documents in MongoDB.
Member 2 pipeline complete.
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `ServerSelectionTimeoutError` | Check your internet connection and verify `MONGO_URI` in `.env` is correct. Make sure your IP is whitelisted in MongoDB Atlas (Network Access → Add Current IP). |
| `SSL: CERTIFICATE_VERIFY_FAILED` | The `certifi` package should handle this. Run `pip install --upgrade certifi`. |
| `ModuleNotFoundError: No module named 'textblob'` | Run `pip install -r requirements.txt` and then `python -m textblob.download_corpora`. |
| `No signals found in MongoDB` | Member 1's scraper may not have run yet, or the database/collection name may be different. Verify you're connecting to `venture_alpha.signals`. |
| `Could not save scores to MongoDB` | Your database user may have read-only permissions. Go to MongoDB Atlas → Database Access → Edit user → Change role to **Read and Write to Any Database**. |
| `KeyError` on a column name | The upstream schema may have changed. Verify document fields match what `metrics.py` expects (`stars`, `contributors`, `created_utc`, `description`, `repo_name`, `tags`, `url`). |

---

## 🤝 Contributing

### For New Developers Joining the Project

1. **Read this document fully** before touching any code.
2. **Set up your environment** following the [Environment Setup](#-environment-setup) section.
3. **Understand the pipeline flow** — data flows through `metrics.py` → `sentiment.py` → `conviction_score.py`.
4. **Coordinate with Member 1** — any changes to the MongoDB document schema must be agreed upon by both members.
5. **Never commit `.env`** — it contains database credentials. It's already in `.gitignore`.

### Code Style

- Use **type hints** on function signatures.
- Write **docstrings** for every public function.
- Handle exceptions gracefully — no silent crashes.
- Print status messages with a `[module_name]` prefix for easy debugging.

### Key Conventions

- **Primary key:** `url` field (not `_id`) — used to match and update documents.
- **Timestamps:** Unix timestamps (`created_utc`), not ISO strings.
- **Score range:** All scores are normalized to **0.0–1.0**.
- **Source field:** One of `"github"`, `"hackernews"`, or `"exa"`.

---

*Last updated: March 16, 2026*
