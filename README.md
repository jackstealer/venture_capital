# 🚀 Venture Alpha — AI-Powered VC Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-4285F4?logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB%20Atlas-Cloud-47A248?logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Exa%20Search-Neural-orange" />
  <img src="https://img.shields.io/badge/TailwindCSS-4.x-38BDF8?logo=tailwindcss&logoColor=white" />
</p>

> **Venture Alpha** is an autonomous AI-driven venture capital scouting agent. It automatically discovers, analyzes, and evaluates trending open-source repositories — generating investment-grade due diligence reports powered by **Google Gemini** and **Exa Neural Search**.

---

## 📋 Table of Contents

1. [Key Features](#-key-features)
2. [System Architecture](#️-system-architecture)
3. [Project Structure](#-project-structure)
4. [Tech Stack](#️-tech-stack)
5. [Prerequisites](#-prerequisites)
6. [Quick Start](#-quick-start)
7. [API Reference](#-api-reference)
8. [Environment Variables](#-environment-variables)
9. [How It Works](#-how-it-works)
10. [Conviction Score Formula](#-conviction-score-formula)
11. [Data Pipeline (Optional)](#-data-pipeline-optional)
12. [Known Issues & Fixes](#-known-issues--fixes)
13. [Contributing](#-contributing)
14. [License](#-license)

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Automated Scouting** | Aggregates trending signals from GitHub, Product Hunt, Google Trends & NewsAPI |
| 🤖 **Technology Analysis** | Gemini AI extracts core tech, use cases, and industry impact from any repo |
| 📈 **Trend Validation** | Evaluates each project against emerging industry trends with a High/Medium/Low score |
| 🎙️ **Founder Interview Simulation** | Simulates a rigorous VC due-diligence Q&A with a virtual founder |
| 📄 **Investment Memo Generation** | Produces complete VC memos with conviction score, risk breakdown & GTM analysis |
| ⚔️ **Head-to-Head Comparison** | Pits two projects against each other for a data-backed investment recommendation |
| 🗄️ **MongoDB Persistence** | Saves all analysis results with upsert for repeated runs |
| 🔒 **Prompt Injection Protection** | Sanitizes all user inputs before they reach the LLM |
| ♻️ **Exponential Backoff Retry** | All LLM calls include 3-attempt retry with fallback responses |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  FRONTEND (React + Vite)             │
│  Dashboard → Emerging Projects → AI Analysis Report  │
│  Vite Dev Proxy: /api/* → localhost:8000             │
└──────────────────────┬──────────────────────────────┘
                       │  REST API (JSON)
┌──────────────────────▼──────────────────────────────┐
│              LLM INTELLIGENCE BACKEND (FastAPI)       │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │ Tools    │  │ Agents   │  │ Services           │   │
│  │ github_  │  │ trend_   │  │ analysis_service   │   │
│  │ analyzer │  │ agent    │  │ (full pipeline +   │   │
│  │ research │  │ memo_    │  │  compare_projects) │   │
│  │ _tool    │  │ agent    │  │                    │   │
│  │ founder_ │  └──────────┘  └───────────────────┘   │
│  │ simulator│                                         │
│  └──────────┘                                         │
│                                                       │
│  External APIs: Google Gemini  ·  Exa Neural Search  │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               MongoDB Atlas (signals collection)      │
│  Stores: conviction scores, memos, evidence sources  │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
venture_capital-main/
│
├── LLM/                          # FastAPI AI Intelligence Backend
│   ├── app.py                    # Main entry point — all 9 API endpoints
│   ├── config.py                 # Settings, API keys, MongoDB client
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variable template
│   │
│   ├── models/
│   │   └── schemas.py            # Pydantic v2 input/output schemas
│   │
│   ├── tools/                    # Individual AI tools (step-functions)
│   │   ├── github_analyzer.py    # Technology analysis via Gemini
│   │   ├── research_tool.py      # Web research via Exa Search + Gemini
│   │   └── founder_simulator.py  # VC Q&A simulation via Gemini
│   │
│   ├── agents/                   # Orchestration agents
│   │   ├── trend_agent.py        # Trend strength validation
│   │   └── memo_agent.py         # Investment memo + conviction scoring
│   │
│   ├── services/
│   │   └── analysis_service.py   # Full 5-step pipeline + compare_projects
│   │
│   └── utils/
│       ├── prompt_templates.py   # All Gemini prompt templates
│       └── resilience.py         # Retry logic, sanitization, helpers
│
├── frontend/
│   └── venture-alpha-frontend/   # React + Vite + Tailwind CSS App
│       ├── src/
│       │   ├── App.jsx           # Router (3 routes)
│       │   ├── pages/
│       │   │   ├── Dashboard.jsx     # Landing page
│       │   │   ├── EmergingTech.jsx  # Project grid with conviction scores
│       │   │   └── Analysis.jsx      # Full AI analysis report view
│       │   └── components/
│       │       └── ProjectCard.jsx   # Individual project card component
│       ├── vite.config.js        # Dev proxy: /api → localhost:8000
│       └── package.json
│
├── data/
│   └── projects.json             # Cached project data (87KB)
│
├── data_collection/              # GitHub + Product Hunt scrapers
├── data_preprocessing/           # Data normalization pipeline
├── backend/                      # Legacy backend scripts
└── README.md
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Role |
|---|---|
| **Python 3.11+** | Runtime |
| **FastAPI** | REST API framework |
| **Pydantic v2** | Data validation & serialization |
| **Google Gemini 1.5 Flash** | AI analysis, memo generation, trend validation |
| **Exa Neural Search** | Web research & article retrieval |
| **PyMongo** | MongoDB Atlas client |
| **python-dotenv** | Environment variable management |

### Frontend
| Technology | Role |
|---|---|
| **React 19** | UI framework |
| **Vite 8** | Build tool & dev server |
| **Tailwind CSS 4** | Utility-first styling |
| **React Router v7** | Client-side routing |

---

## 📦 Prerequisites

- **Python 3.11+** — [Download](https://python.org/downloads)
- **Node.js 18+** — [Download](https://nodejs.org)
- **MongoDB Atlas** account (free tier works) — [Sign up](https://cloud.mongodb.com)
- **Google Gemini API Key** — [Get key](https://aistudio.google.com/app/apikey)
- **Exa API Key** — [Get key](https://exa.ai)

---

## ⚡ Quick Start

### Step 1 — Clone the Repository

```bash
git clone https://github.com/jackstealer/venture_capital.git
cd venture_capital
```

### Step 2 — Set Up the LLM Backend

```bash
cd LLM

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
# Edit .env and fill in your API keys
```

**`.env` file contents:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
EXA_API_KEY=your_exa_api_key_here
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/
```

### Step 3 — Start the Backend Server

```bash
# From the LLM/ directory
python -m uvicorn app:app --reload --port 8000
```

The API will be live at **http://localhost:8000**  
Interactive docs available at **http://localhost:8000/docs**

### Step 4 — Seed Demo Data into MongoDB

On first run, seed the 5 demo projects so the frontend has data to show:

```bash
curl -X POST http://localhost:8000/seed_data
```

Or via the Swagger UI at `/docs` → POST `/seed_data`.

### Step 5 — Start the Frontend

```bash
cd frontend/venture-alpha-frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

The app will be live at **http://localhost:5173**

---

## 📡 API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

| Method | Endpoint | Description | Response Time |
|--------|----------|-------------|---------------|
| `GET` | `/` | Health check | ~instant |
| `GET` | `/demo_projects` | Get 5 curated demo projects | ~instant |
| `GET` | `/emerging_projects` | Fetch top projects from MongoDB by conviction score | ~instant |
| `POST` | `/seed_data` | Seed 5 demo projects into MongoDB | ~instant |
| `POST` | `/analyze_repository` | Technology analysis via Gemini | 3–8s |
| `POST` | `/validate_trend` | Trend strength assessment | 3–8s |
| `POST` | `/founder_interview` | Simulated VC Q&A | 5–15s |
| `POST` | `/generate_memo` | Full investment memo + conviction score | 10–25s |
| `POST` | `/full_analysis` | Complete 5-step AI pipeline | 20–40s |
| `POST` | `/compare_projects` | Head-to-head project comparison | 10–20s |

### Example: POST `/full_analysis`

**Request:**
```json
{
  "repo_name": "LangGraph",
  "repo_url": "https://github.com/langchain-ai/langgraph",
  "description": "Framework for building stateful AI agents with LLMs",
  "stars": 12000,
  "contributors": 85,
  "star_velocity": 45.0,
  "social_sentiment": "positive",
  "news_mentions": 12
}
```

**Response:**
```json
{
  "technology_summary": "LangGraph is a graph-based orchestration framework...",
  "key_use_cases": "Building stateful multi-agent workflows...",
  "industry_impact": "Disrupting software automation and AI tooling...",
  "research_summary": "LangGraph has gained significant traction...",
  "sources": ["https://..."],
  "trend_strength": "High",
  "trend_reasoning": "Rapid star growth and community adoption...",
  "founder_interview": {
    "questions": ["What makes LangGraph defensible?"],
    "answers": ["Our core moat lies in..."]
  },
  "investment_memo": "## Investment Memo: LangGraph\n\n...",
  "conviction_score": 0.72,
  "signal_breakdown": {
    "github_velocity": 0.23,
    "community_strength": 0.17,
    "developer_sentiment": 1.0,
    "media_presence": 0.24
  },
  "risks": [
    "Dependency on OpenAI ecosystem",
    "Early-stage monetization uncertainty"
  ],
  "evidence_sources": ["https://github.com/...", "https://..."],
  "analysis_time": "28.4 seconds"
}
```

---

## 🔐 Environment Variables

Create a `.env` file inside the `LLM/` directory based on `.env.example`:

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key from AI Studio |
| `EXA_API_KEY` | ✅ Yes | Exa Neural Search API key |
| `MONGO_URI` | ✅ Yes | MongoDB Atlas connection string |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.

---

## 🧠 How It Works

### Full Analysis Pipeline (5 Steps)

```
Input: RepoInput (name, url, stars, contributors, sentiment...)
        │
        ▼
Step 1: 🔬 Technology Analysis
        └─ Gemini analyzes the repo → tech_summary, use_cases, industry_impact
        │
        ▼
Step 2: 🌐 Web Research (Exa Search)
        └─ Fetches 5 recent articles → Gemini synthesizes → research_summary
        │
        ▼
Step 3: 📈 Trend Validation
        └─ Gemini evaluates signals → trend_strength (High/Medium/Low)
        │
        ▼
Step 4: 🎙️ Founder Interview Simulation
        └─ Gemini simulates VC Q&A → questions[] + answers[]
        │
        ▼
Step 5: 📄 Investment Memo Generation
        └─ Gemini writes full memo → conviction_score + signal_breakdown + risks
        │
        ▼
Output: FullAnalysisOutput saved to MongoDB Atlas
```

---

## 📊 Conviction Score Formula

The conviction score is a weighted composite of 4 quantitative signals:

```
Conviction Score = 0.40 × GitHub Velocity
                 + 0.30 × Community Strength
                 + 0.20 × Developer Sentiment
                 + 0.10 × Media Presence
```

| Signal | Source | Normalization |
|--------|--------|---------------|
| GitHub Velocity | `star_velocity` (stars/day) | Capped at 200 stars/day |
| Community Strength | `contributors` count | Capped at 500 contributors |
| Developer Sentiment | `social_sentiment` string | positive=1.0, neutral=0.5, negative=0.0 |
| Media Presence | `news_mentions` count | Capped at 50 mentions |

**Score interpretation:**
- `0.7 – 1.0` → 🟢 Strong Buy / Invest
- `0.4 – 0.7` → 🟡 Watch / Monitor
- `0.0 – 0.4` → 🔴 Pass / Insufficient Signal

---

## 🔄 Data Pipeline (Optional)

The `data_collection/` and `data_preprocessing/` modules provide an automated pipeline to ingest fresh data from GitHub, Product Hunt, Google Trends, and NewsAPI into MongoDB.

```bash
cd data_collection/data_collection
python main.py
```

This step is **optional** — the app works fully with the seeded demo data and on-demand `/full_analysis` calls.

---

## 🐛 Known Issues & Fixes Applied

The following bugs were identified and fixed in this codebase:

| # | Issue | Fix |
|---|-------|-----|
| 1 | Frontend sent wrong API field names (`github_velocity` etc.) causing 422 errors — AI was never called | Fixed field names to match Pydantic schema |
| 2 | `validate()` raised `Exception` but app caught `EnvironmentError` — startup crash was unhandled | Changed to `raise EnvironmentError(...)` |
| 3 | `MongoClient` created before `validate()` at import time, bypassing env checks | Moved to lazy initializer |
| 4 | Gemini model `"gemini-2.5-flash-lite"` doesn't exist → all AI calls failed | Changed to `"gemini-1.5-flash"` |
| 5 | `MONGO_URI` missing from `.env.example` | Added to template |
| 6 | `alert()` used for backend errors — blank page on failure | Replaced with proper error UI with instructions |
| 7 | API key printed to stdout on every startup | Removed security leak |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📜 License

This project is open-source. Feel free to use, modify, and distribute.

---

<p align="center">
  Built with ❤️ using <strong>Google Gemini</strong>, <strong>FastAPI</strong>, <strong>React</strong>, and <strong>MongoDB Atlas</strong>
</p>
