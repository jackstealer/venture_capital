"""
app.py
------
Venture-Alpha AI Intelligence Layer — FastAPI Entry Point (Phase 2)

Endpoints:
  GET  /                    → Health check
  POST /analyze_repository  → Technology analysis
  POST /validate_trend      → Trend strength assessment
  POST /founder_interview   → Simulated VC Q&A
  POST /generate_memo       → VC memo + conviction + risks + signals
  POST /full_analysis       → Complete 5-step pipeline
  GET  /demo_projects       → Pre-loaded trending repos for demos
  POST /compare_projects    → Head-to-head project comparison

Phase 2 enhancements:
  ✓ evidence_sources — explainable AI, trust signals
  ✓ analysis_time — performance metric
  ✓ signal_breakdown — component-level conviction breakdown
  ✓ risks — structured risk list
  ✓ /demo_projects — curated demo data
  ✓ /compare_projects — side-by-side AI comparison
"""

import time
import logging
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings

# Validate required env vars before booting
try:
    settings.validate()
except EnvironmentError as e:
    print(f"[STARTUP ERROR] {e}")
    sys.exit(1)

from models.schemas import (
    RepoInput,
    TechAnalysisOutput,
    TrendOutput,
    InterviewOutput,
    MemoOutput,
    FullAnalysisOutput,
    DemoProject,
    DemoProjectsOutput,
    CompareProjectsInput,
    CompareProjectsOutput,
)

from tools.github_analyzer import analyze_repository
from tools.research_tool import research_technology
from tools.founder_simulator import simulate_founder_interview
from agents.trend_agent import validate_trend
from agents.memo_agent import generate_investment_memo, compute_signal_breakdown
from services.analysis_service import run_full_pipeline, compare_projects, get_emerging_projects, seed_demo_projects

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO PROJECTS DATA — curated trending repos for hackathon demos
# ─────────────────────────────────────────────────────────────────────────────

DEMO_PROJECTS = [
    DemoProject(
        repo_name="LangGraph",
        repo_url="https://github.com/langchain-ai/langgraph",
        description="Framework for building stateful AI agents with LLMs",
        stars=12000, contributors=85, star_velocity=45,
        social_sentiment="positive", news_mentions=12,
        category="AI Agents"
    ),
    DemoProject(
        repo_name="CrewAI",
        repo_url="https://github.com/crewaiinc/crewai",
        description="Framework for orchestrating role-playing autonomous AI agents",
        stars=22000, contributors=120, star_velocity=60,
        social_sentiment="positive", news_mentions=18,
        category="AI Agents"
    ),
    DemoProject(
        repo_name="Ollama",
        repo_url="https://github.com/ollama/ollama",
        description="Get up and running with large language models locally",
        stars=105000, contributors=400, star_velocity=120,
        social_sentiment="positive", news_mentions=35,
        category="Local AI / Inference"
    ),
    DemoProject(
        repo_name="Dify",
        repo_url="https://github.com/langgenius/dify",
        description="Open-source LLM app development platform with visual workflow",
        stars=60000, contributors=300, star_velocity=80,
        social_sentiment="positive", news_mentions=20,
        category="LLM Platform"
    ),
    DemoProject(
        repo_name="Pydantic AI",
        repo_url="https://github.com/pydantic/pydantic-ai",
        description="Agent Framework / shim to use Pydantic with LLMs",
        stars=5000, contributors=45, star_velocity=25,
        social_sentiment="positive", news_mentions=8,
        category="AI DevTools"
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health check — confirms the service is running."""
    return {
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": [
            "/analyze_repository", "/validate_trend",
            "/founder_interview", "/generate_memo",
            "/full_analysis", "/demo_projects", "/compare_projects"
        ],
        "docs": "/docs"
    }


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 1: REPOSITORY TECHNOLOGY ANALYZER
# ─────────────────────────────────────────────────────────────────────────────

@app.post(
    "/analyze_repository",
    response_model=TechAnalysisOutput,
    tags=["AI Analysis"],
    summary="Analyse a repository's technology using Gemini"
)
def endpoint_analyze_repository(repo: RepoInput) -> TechAnalysisOutput:
    try:
        logger.info(f"POST /analyze_repository — {repo.repo_name}")
        return analyze_repository(repo.model_dump())
    except Exception as e:
        logger.error(f"analyze_repository failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 2: TREND VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

@app.post(
    "/validate_trend",
    response_model=TrendOutput,
    tags=["AI Analysis"],
    summary="Validate whether a project represents an emerging trend"
)
def endpoint_validate_trend(repo: RepoInput) -> TrendOutput:
    try:
        logger.info(f"POST /validate_trend — {repo.repo_name}")
        return validate_trend(repo.model_dump())
    except Exception as e:
        logger.error(f"validate_trend failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 3: FOUNDER INTERVIEW SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

@app.post(
    "/founder_interview",
    response_model=InterviewOutput,
    tags=["AI Analysis"],
    summary="Simulate a VC founder due-diligence interview"
)
def endpoint_founder_interview(repo: RepoInput) -> InterviewOutput:
    try:
        logger.info(f"POST /founder_interview — {repo.repo_name}")
        tech = analyze_repository(repo.model_dump())
        enriched = {
            **repo.model_dump(),
            "technology_summary": tech.technology_summary,
            "key_use_cases": tech.key_use_cases,
            "industry_impact": tech.industry_impact
        }
        return simulate_founder_interview(enriched)
    except Exception as e:
        logger.error(f"founder_interview failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 4: INVESTMENT MEMO GENERATOR (Phase 2 enhanced)
# ─────────────────────────────────────────────────────────────────────────────

@app.post(
    "/generate_memo",
    response_model=MemoOutput,
    tags=["AI Analysis"],
    summary="Generate a VC investment memo with conviction score, signals, and risks"
)
def endpoint_generate_memo(repo: RepoInput) -> MemoOutput:
    try:
        logger.info(f"POST /generate_memo — {repo.repo_name}")
        repo_dict = repo.model_dump()

        tech = analyze_repository(repo_dict)
        research = research_technology(repo.repo_name)
        trend = validate_trend(repo_dict)

        memo_input = {
            **repo_dict,
            "technology_summary": tech.technology_summary,
            "key_use_cases": tech.key_use_cases,
            "industry_impact": tech.industry_impact,
            "research_summary": research.research_summary,
            "trend_strength": trend.trend_strength
        }
        return generate_investment_memo(memo_input)
    except Exception as e:
        logger.error(f"generate_memo failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 5: FULL ANALYSIS PIPELINE (Phase 2 enhanced)
# ─────────────────────────────────────────────────────────────────────────────

@app.post(
    "/full_analysis",
    response_model=FullAnalysisOutput,
    tags=["AI Analysis"],
    summary="Run the complete 5-step AI pipeline with evidence, timing, and risk analysis",
    description=(
        "Executes the full pipeline and returns:\n"
        "• Technology analysis\n"
        "• Web research (Exa) with evidence_sources\n"
        "• Trend validation\n"
        "• Founder interview simulation\n"
        "• Investment memo + conviction score\n"
        "• Signal breakdown + risks\n"
        "• Processing time\n\n"
        "⚠️ Takes 20-40 seconds (multiple API calls)."
    )
)
def endpoint_full_analysis(repo: RepoInput) -> FullAnalysisOutput:
    try:
        logger.info(f"POST /full_analysis — {repo.repo_name} (full pipeline)")
        return run_full_pipeline(repo.model_dump())
    except Exception as e:
        logger.error(f"full_analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 6: DEMO PROJECTS (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/demo_projects",
    response_model=DemoProjectsOutput,
    tags=["Demo & Compare"],
    summary="Get curated trending repositories for demo purposes",
    description=(
        "Returns 5 pre-loaded trending open-source projects that can be "
        "directly used as input to any analysis endpoint. "
        "Great for hackathon demos and frontend showcase."
    )
)
def endpoint_demo_projects() -> DemoProjectsOutput:
    """Return curated trending repos — no API calls, instant response."""
    return DemoProjectsOutput(
        projects=DEMO_PROJECTS,
        total=len(DEMO_PROJECTS)
    )


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 7: COMPARE PROJECTS (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────

@app.post(
    "/compare_projects",
    response_model=CompareProjectsOutput,
    tags=["Demo & Compare"],
    summary="Compare two projects side-by-side for investment strength",
    description=(
        "Accepts two RepoInput objects, computes signal breakdowns and "
        "conviction scores for both, then uses Gemini to generate a "
        "comparative analysis and investment recommendation."
    )
)
def endpoint_compare_projects(body: CompareProjectsInput) -> CompareProjectsOutput:
    try:
        logger.info(f"POST /compare_projects — {body.repo1.repo_name} vs {body.repo2.repo_name}")
        return compare_projects(body.repo1.model_dump(), body.repo2.model_dump())
    except Exception as e:
        logger.error(f"compare_projects failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 8: EMERGING PROJECTS FROM MONGODB
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/emerging_projects",
    tags=["MongoDB"],
    summary="Fetch top emerging projects from MongoDB signals collection",
    description=(
        "Reads the 'signals' collection in MongoDB, sorts by conviction_score "
        "descending, and returns the top-N projects. Requires MONGO_URI to be set."
    )
)
def endpoint_emerging_projects(limit: int = 10):
    try:
        logger.info(f"GET /emerging_projects — limit={limit}")
        projects = get_emerging_projects(limit=limit)
        return {"count": len(projects), "projects": projects}
    except Exception as e:
        logger.error(f"emerging_projects failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 9: SEED DEMO DATA INTO MONGODB
# ─────────────────────────────────────────────────────────────────────────────

@app.post(
    "/seed_data",
    tags=["MongoDB"],
    summary="Seed the 5 demo projects into MongoDB signals collection",
    description=(
        "Upserts the 5 canonical demo projects into MongoDB with computed "
        "conviction scores. Call this once to bootstrap /emerging_projects "
        "before any real analysis runs have been saved."
    )
)
def endpoint_seed_data():
    try:
        logger.info("POST /seed_data — seeding demo projects into MongoDB")
        result = seed_demo_projects()
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"seed_data failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
