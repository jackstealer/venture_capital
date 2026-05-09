"""
services/analysis_service.py
------------------------------
Orchestration Service — Full AI Pipeline (Phase 2 Enhanced)

Now includes:
  • evidence_sources collection (repo_url + Exa article URLs)
  • analysis_time measurement
  • signal_breakdown passthrough
  • risks passthrough
  • compare_projects function

Uses Gemini 2.0 Flash via google.generativeai SDK.
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

import google.generativeai as genai

from config import settings, signals_collection, mongo_db
from utils.resilience import (
    call_llm_with_retry,
    strip_markdown_fences,
    safe_get,
    sanitize_input,
    truncate,
)

from tools.github_analyzer import analyze_repository
from tools.research_tool import research_technology
from tools.founder_simulator import simulate_founder_interview
from agents.trend_agent import validate_trend
from agents.memo_agent import (
    generate_investment_memo,
    compute_conviction_score,
    compute_signal_breakdown
)
from models.schemas import FullAnalysisOutput, CompareProjectsOutput

logger = logging.getLogger(__name__)

# Configure the Gemini SDK with the API key
genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)


# ─────────────────────────────────────────────────────────────────────────────
# FULL PIPELINE RUNNER (Phase 2 enhanced)
# ─────────────────────────────────────────────────────────────────────────────

def run_full_pipeline(repo_data: Dict[str, Any]) -> FullAnalysisOutput:
    """
    Execute the complete 5-step AI pipeline with Phase 2 enhancements:
      • Collects evidence_sources (repo_url + Exa article URLs)
      • Measures total analysis_time
      • Includes signal_breakdown and risks

    Args:
        repo_data: Dict matching RepoInput fields.

    Returns:
        FullAnalysisOutput with all Phase 2 fields populated.
    """
    start_time = time.time()
    repo_name = repo_data.get("repo_name", "Unknown")
    logger.info(f"Starting full pipeline for: {repo_name}")

    # ── Evidence collection starts with the repo URL ─────────────────────────
    evidence_sources = []
    repo_url = repo_data.get("repo_url", "")
    if repo_url:
        evidence_sources.append(repo_url)

    # ── Step 1: Technology Analysis ───────────────────────────────────────────
    tech = analyze_repository(repo_data)
    logger.info("Step 1 complete: technology analysis")

    # ── Step 2: Web Research ──────────────────────────────────────────────────
    research = research_technology(repo_name)
    logger.info("Step 2 complete: web research")

    # Collect Exa article URLs as evidence
    evidence_sources.extend(research.sources)

    # ── Step 3: Trend Validation ──────────────────────────────────────────────
    trend = validate_trend(repo_data)
    logger.info("Step 3 complete: trend validation")

    # ── Step 4: Founder Interview ─────────────────────────────────────────────
    enriched_analysis = {
        **repo_data,
        "technology_summary": tech.technology_summary,
        "key_use_cases":      tech.key_use_cases,
        "industry_impact":    tech.industry_impact
    }
    interview = simulate_founder_interview(enriched_analysis)
    logger.info("Step 4 complete: founder interview simulation")

    # ── Step 5: Investment Memo ───────────────────────────────────────────────
    memo_input = {
        **repo_data,
        "technology_summary": tech.technology_summary,
        "key_use_cases":      tech.key_use_cases,
        "industry_impact":    tech.industry_impact,
        "research_summary":   research.research_summary,
        "trend_strength":     trend.trend_strength
    }
    memo = generate_investment_memo(memo_input)
    logger.info("Step 5 complete: investment memo generated")

    # ── Timing ────────────────────────────────────────────────────────────────
    elapsed = round(time.time() - start_time, 1)
    analysis_time = f"{elapsed} seconds"
    logger.info(f"Full pipeline completed in {analysis_time}")

    # De-duplicate evidence sources while preserving order
    seen = set()
    unique_evidence = []
    for url in evidence_sources:
        if url and url not in seen:
            seen.add(url)
            unique_evidence.append(url)

    # ── Persist to MongoDB (upsert by repo_name) ──────────────────────────────
    try:
        mongo_doc = {
            "repo_name":         repo_data.get("repo_name"),
            "repo_url":          repo_data.get("repo_url", ""),
            "description":       repo_data.get("description", ""),
            "stars":             repo_data.get("stars", 0),
            "contributors":      repo_data.get("contributors", 0),
            "star_velocity":     repo_data.get("star_velocity", 0),
            "social_sentiment":  repo_data.get("social_sentiment", "neutral"),
            "news_mentions":     repo_data.get("news_mentions", 0),
            "technology_summary":tech.technology_summary,
            "key_use_cases":     tech.key_use_cases,
            "industry_impact":   tech.industry_impact,
            "research_summary":  research.research_summary,
            "trend_strength":    trend.trend_strength,
            "conviction_score":  memo.conviction_score,
            "signal_breakdown":  memo.signal_breakdown.model_dump(),
            "risks":             memo.risks,
            "evidence_sources":  unique_evidence,
            "analysis_time":     analysis_time,
            "analysed_at":       datetime.now(timezone.utc).isoformat(),
        }
        signals_collection.update_one(
            {"repo_name": mongo_doc["repo_name"]},
            {"$set": mongo_doc},
            upsert=True
        )
        logger.info(f"Saved '{repo_name}' to MongoDB signals collection")
    except Exception as db_err:
        logger.warning(f"MongoDB save failed (non-fatal): {db_err}")

    return FullAnalysisOutput(
        # Tech analysis
        technology_summary=tech.technology_summary,
        key_use_cases=tech.key_use_cases,
        industry_impact=tech.industry_impact,
        # Research
        research_summary=research.research_summary,
        sources=research.sources,
        # Trend
        trend_strength=trend.trend_strength,
        trend_reasoning=trend.reasoning,
        # Interview
        founder_interview=interview,
        # Memo + conviction
        investment_memo=memo.memo,
        conviction_score=memo.conviction_score,
        # ── Phase 2 fields ──
        signal_breakdown=memo.signal_breakdown,
        risks=memo.risks,
        evidence_sources=unique_evidence,
        analysis_time=analysis_time
    )


# ─────────────────────────────────────────────────────────────────────────────
# MASTER PROMPT ANALYSIS (Unified Single-Step Flow)
# ─────────────────────────────────────────────────────────────────────────────

def build_master_prompt(project: Dict[str, Any]) -> str:
    return f"""
You are a senior venture capital analyst.

Analyze the following emerging technology using multiple ecosystem signals.

Technology Data:

Project Name: {sanitize_input(safe_get(project, "repo_name", "Unknown"))}
Description: {truncate(sanitize_input(safe_get(project, "description", "N/A")), 300)}

Developer Activity
GitHub Stars: {safe_get(project, "stars", 0)}
Contributors: {safe_get(project, "contributors", 0)}
Star Velocity: {safe_get(project, "star_velocity", 0)}

Community Interest
Product Hunt Engagement: {safe_get(project, "producthunt_votes", "N/A")}

Market Demand
Google Trends Growth: {safe_get(project, "trend_growth", "N/A")}

Media Coverage
News Mentions: {safe_get(project, "news_mentions", 0)}

Social Sentiment
Developer Sentiment: {sanitize_input(str(safe_get(project, "social_sentiment", "neutral")))}

Provide the analysis in the following sections:

1. TECHNOLOGY SUMMARY
Explain the core technology.

2. KEY USE CASES
List practical applications.

3. INDUSTRY IMPACT
Explain how this technology could disrupt markets.

4. TREND STRENGTH
Evaluate whether this is an emerging trend.

5. INVESTMENT MEMO
Write a venture capital style investment memo.

6. RISKS
List major risks investors should consider.

7. FINAL CONVICTION SCORE
Provide a score between 0 and 1.
"""

def analyze_project_master(project: Dict[str, Any]) -> str:
    """
    Runs a single, unified LLM prompt to generate the entire analysis stack
    (Tech Summary, Use Cases, Industry Impact, Trend, Memo, Risks, Score).
    """
    logger.info(f"Running universal master prompt analysis for {project.get('repo_name')}")
    prompt = build_master_prompt(project)
    
    result, err = call_llm_with_retry(_model, prompt)
    if not result:
        return f"Master analysis failed due to LLM unavailability. Reason: {err}"
        
    return strip_markdown_fences(result)


# ─────────────────────────────────────────────────────────────────────────────
# COMPARE PROJECTS (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────


def compare_projects(
    repo1_data: Dict[str, Any],
    repo2_data: Dict[str, Any]
) -> CompareProjectsOutput:
    """
    Compare two projects side-by-side on signal breakdown, conviction scores,
    and generate an AI-powered comparative analysis.

    Args:
        repo1_data: Dict for first repository.
        repo2_data: Dict for second repository.

    Returns:
        CompareProjectsOutput with scores, breakdowns, and recommendation.
    """
    start_time = time.time()

    name1 = sanitize_input(safe_get(repo1_data, "repo_name", "Project 1"))
    name2 = sanitize_input(safe_get(repo2_data, "repo_name", "Project 2"))
    logger.info(f"Comparing projects: {name1} vs {name2}")

    # Compute individual signals
    sb1 = compute_signal_breakdown(repo1_data)
    sb2 = compute_signal_breakdown(repo2_data)
    cs1 = compute_conviction_score(repo1_data)
    cs2 = compute_conviction_score(repo2_data)

    # Sanitize user-supplied fields before building prompt
    desc1 = truncate(sanitize_input(safe_get(repo1_data, 'description', '')), 300)
    desc2 = truncate(sanitize_input(safe_get(repo2_data, 'description', '')), 300)
    sent1 = sanitize_input(str(safe_get(repo1_data, 'social_sentiment', 'neutral')))
    sent2 = sanitize_input(str(safe_get(repo2_data, 'social_sentiment', 'neutral')))

    # Use Gemini Flash for a qualitative comparison (with retry)
    prompt = f"""
You are a senior VC investment analyst comparing two open-source projects.

Project 1: {name1}
  - Description: {desc1}
  - Stars: {safe_get(repo1_data, 'stars', 0):,} | Velocity: {safe_get(repo1_data, 'star_velocity', 0)} stars/day
  - Contributors: {safe_get(repo1_data, 'contributors', 0)}
  - Sentiment: {sent1}
  - News Mentions: {safe_get(repo1_data, 'news_mentions', 0)}
  - Conviction Score: {cs1:.2f}

Project 2: {name2}
  - Description: {desc2}
  - Stars: {safe_get(repo2_data, 'stars', 0):,} | Velocity: {safe_get(repo2_data, 'star_velocity', 0)} stars/day
  - Contributors: {safe_get(repo2_data, 'contributors', 0)}
  - Sentiment: {sent2}
  - News Mentions: {safe_get(repo2_data, 'news_mentions', 0)}
  - Conviction Score: {cs2:.2f}

Write TWO sections:

COMPARISON: A 3-4 sentence comparative analysis covering technology potential,
community momentum, and market timing.

RECOMMENDATION: One clear sentence stating which project is the stronger
investment bet and the single most important reason why.

Respond in EXACTLY this JSON format (no markdown fences, pure JSON):
{{
  "comparison_summary": "<comparison text>",
  "recommendation": "<recommendation text>"
}}
""".strip()

    # Fallback values in case LLM fails
    winner = name1 if cs1 >= cs2 else name2
    comparison_summary = (
        f"{name1} scores {cs1:.2f} vs {name2} at {cs2:.2f}. "
        f"Based on quantitative signals, {winner} shows stronger momentum."
    )
    recommendation = f"{winner} is the stronger investment based on overall signal strength."

    raw, err = call_llm_with_retry(_model, prompt)
    if raw is not None:
        try:
            raw = strip_markdown_fences(raw)
            data = json.loads(raw)
            comparison_summary = data.get("comparison_summary", comparison_summary)
            recommendation = data.get("recommendation", recommendation)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Comparison response parse failed: {e}. Using quantitative fallback.")
    else:
        logger.warning(f"Comparison LLM unavailable ({err}) — using quantitative fallback.")
        comparison_summary += f" [LLM Analysis Unavailable: {err}]"

    elapsed = round(time.time() - start_time, 1)

    return CompareProjectsOutput(
        project1_name=name1,
        project2_name=name2,
        project1_score=cs1,
        project2_score=cs2,
        project1_breakdown=sb1,
        project2_breakdown=sb2,
        comparison_summary=comparison_summary,
        recommendation=recommendation,
        analysis_time=f"{elapsed} seconds"
    )


# ─────────────────────────────────────────────────────────────────────────────
# LANGCHAIN AGENT RUNNER (lazy imports — bonus feature)
# ─────────────────────────────────────────────────────────────────────────────

def run_langchain_agent(repo_data: Dict[str, Any]) -> str:
    """
    Run a LangChain agent over the pipeline tools (lazy-loaded).
    Falls back to sequential pipeline on any import failure.
    """
    logger.info(f"Running LangChain agent for: {repo_data.get('repo_name')}")

    try:
        from langchain_core.tools import Tool
        from langchain_google_genai import ChatGoogleGenerativeAI

        try:
            from langgraph.prebuilt import create_react_agent as _create_agent
            _use_langgraph = True
        except ImportError:
            _use_langgraph = False

        def _repo_tool(_: str) -> str:
            r = analyze_repository(repo_data)
            return f"Summary: {r.technology_summary}\nUses: {r.key_use_cases}\nImpact: {r.industry_impact}"

        def _research_tool(_: str) -> str:
            r = research_technology(repo_data.get("repo_name", ""))
            return f"Research: {r.research_summary}\nSources: {', '.join(r.sources[:3])}"

        def _trend_tool(_: str) -> str:
            r = validate_trend(repo_data)
            return f"Trend: {r.trend_strength}\nReasoning: {r.reasoning}"

        def _score_tool(_: str) -> str:
            return f"Conviction Score: {compute_conviction_score(repo_data):.2f}"

        tools = [
            Tool(name="repository_analyzer", func=_repo_tool,
                 description="Analyses a repository's technology and impact."),
            Tool(name="web_research", func=_research_tool,
                 description="Searches the web for articles about the technology."),
            Tool(name="trend_validator", func=_trend_tool,
                 description="Determines trend strength from project signals."),
            Tool(name="score_calculator", func=_score_tool,
                 description="Computes conviction score on a 0–1 scale."),
        ]

        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3
        )

        query = (
            f"Analyse '{repo_data.get('repo_name')}': use all tools in sequence, "
            f"then summarise your investment thesis."
        )

        if _use_langgraph:
            agent = _create_agent(llm, tools)
            result = agent.invoke({"messages": [("user", query)]})
            msgs = result.get("messages", [])
            return msgs[-1].content if msgs else "Agent completed."
        else:
            return "LangChain agent unavailable. Use /full_analysis instead."

    except Exception as e:
        logger.warning(f"LangChain agent failed: {e}")
        full = run_full_pipeline(repo_data)
        return f"Technology: {full.technology_summary}\nTrend: {full.trend_strength}\nScore: {full.conviction_score}"


# ─────────────────────────────────────────────────────────────────────────────
# EMERGING PROJECTS FROM MONGODB
# ─────────────────────────────────────────────────────────────────────────────

def get_emerging_projects(limit: int = 10):
    """
    Fetch top projects from MongoDB signals collection,
    sorted by conviction_score descending.

    Returns:
        List of project dicts with _id converted to string.
    """
    try:
        cursor = signals_collection.find({}).sort("conviction_score", -1).limit(limit)
        projects = list(cursor)
        for project in projects:
            project["_id"] = str(project["_id"])
        logger.info(f"Fetched {len(projects)} emerging projects from MongoDB")
        return projects
    except Exception as e:
        logger.error(f"get_emerging_projects failed: {e}", exc_info=True)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# SEED DEMO DATA INTO MONGODB
# ─────────────────────────────────────────────────────────────────────────────

DEMO_SEED_PROJECTS = [
    {
        "repo_name": "LangGraph",
        "repo_url": "https://github.com/langchain-ai/langgraph",
        "description": "Framework for building stateful AI agents with LLMs",
        "stars": 12000, "contributors": 85, "star_velocity": 45,
        "social_sentiment": "positive", "news_mentions": 12,
        "category": "AI Agents",
    },
    {
        "repo_name": "CrewAI",
        "repo_url": "https://github.com/crewaiinc/crewai",
        "description": "Framework for orchestrating role-playing autonomous AI agents",
        "stars": 22000, "contributors": 120, "star_velocity": 60,
        "social_sentiment": "positive", "news_mentions": 18,
        "category": "AI Agents",
    },
    {
        "repo_name": "Ollama",
        "repo_url": "https://github.com/ollama/ollama",
        "description": "Get up and running with large language models locally",
        "stars": 105000, "contributors": 400, "star_velocity": 120,
        "social_sentiment": "positive", "news_mentions": 35,
        "category": "Local AI / Inference",
    },
    {
        "repo_name": "Dify",
        "repo_url": "https://github.com/langgenius/dify",
        "description": "Open-source LLM app development platform with visual workflow",
        "stars": 60000, "contributors": 300, "star_velocity": 80,
        "social_sentiment": "positive", "news_mentions": 20,
        "category": "LLM Platform",
    },
    {
        "repo_name": "Pydantic AI",
        "repo_url": "https://github.com/pydantic/pydantic-ai",
        "description": "Agent Framework / shim to use Pydantic with LLMs",
        "stars": 5000, "contributors": 45, "star_velocity": 25,
        "social_sentiment": "positive", "news_mentions": 8,
        "category": "AI DevTools",
    },
]


def seed_demo_projects() -> dict:
    """
    Upsert the 5 canonical demo projects into MongoDB signals collection.
    Computes conviction scores from the signal data.
    Useful for bootstrapping /emerging_projects before any real analysis has run.

    Returns:
        Summary dict with upserted_count and project names.
    """
    logger.info("Seeding demo projects into MongoDB signals collection...")
    seeded = []

    for proj in DEMO_SEED_PROJECTS:
        sb = compute_signal_breakdown(proj)
        conviction = round(
            0.4 * sb.github_velocity
            + 0.3 * sb.community_strength
            + 0.2 * sb.developer_sentiment
            + 0.1 * sb.media_presence,
            2
        )
        doc = {
            **proj,
            "conviction_score":  conviction,
            "signal_breakdown":  sb.model_dump(),
            "technology_summary": "",
            "key_use_cases":      "",
            "industry_impact":    "",
            "research_summary":   "",
            "trend_strength":     "High" if conviction >= 0.6 else "Medium",
            "risks":              [],
            "evidence_sources":   [proj["repo_url"]],
            "analysis_time":      "seeded",
            "analysed_at":        datetime.now(timezone.utc).isoformat(),
        }
        signals_collection.update_one(
            {"repo_name": proj["repo_name"]},
            {"$set": doc},
            upsert=True
        )
        seeded.append(proj["repo_name"])
        logger.info(f"Seeded '{proj['repo_name']}' (conviction={conviction})")

    logger.info(f"Seeded {len(seeded)} demo projects into MongoDB")
    return {"seeded": len(seeded), "projects": seeded}
