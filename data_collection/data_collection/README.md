# Venture Alpha - Data Collection Layer

This is the data ingestion pipeline for the Venture Alpha hackathon project. It fetches potential VC investment signals from GitHub, HackerNews, and Exa, normalizes them into a standard schema, and saves them to our MongoDB Atlas `signals` collection.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in your API keys:
   - `MONGO_URI`: Your MongoDB connection string.
   - `GITHUB_TOKEN`: A classic personal access token.
   - `EXA_API_KEY`: Your Exa search API key.

## Running the Pipeline

To run the full collection pipeline and update the database with fresh data:

```bash
python main.py
```

This script is idempotent (it safely updates existing records using their URL to prevent duplicates).

## Data Schema

Any downstream machine learning or backend applications can expect documents in the MongoDB `signals` collection to have the following normalized schema:

```json
{
  "source": "github | hackernews | exa",
  "repo_name": "Name or Title",
  "description": "Repo description, post body, etc.",
  "url": "https://...",
  "stars": 1234,
  "contributors": 42,
  "num_comments": 89,
  "author": "username",
  "created_utc": 1675875483,
  "tags": ["AI", "agents"],
  "fetched_at": "2024-10-24T12:00:00Z"
}
```
