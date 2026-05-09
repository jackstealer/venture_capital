"""
agents/memo_agent.py
---------------------
Agent — Investment Memo Generator

Now returns:
  • memo text
  • conviction_score
  • signal_breakdown (component-level scores)
  • risks (extracted structured risk list)

Includes retry logic on all LLM calls and fallback responses.
"""

import json
import logging
from typing import Dict, Any, List

import google.generativeai as genai

from config import settings
from models.schemas import MemoOutput, SignalBreakdown
from utils.prompt_templates import investment_memo_prompt
from utils.resilience import (
    call_llm_with_retry,
    strip_markdown_fences,
    safe_get,
    sanitize_input,
    truncate,
)

logger = logging.getLogger(__name__)

# Configure the Gemini SDK with the API key
genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)

# ── Normalisation ceilings ────────────────────────────────────────────────────
MAX_STAR_VELOCITY = 200.0
MAX_CONTRIBUTORS  = 500.0
MAX_NEWS_MENTIONS = 50.0

SENTIMENT_MAP = {
    "positive": 1.0,
    "neutral":  0.5,
    "negative": 0.0
}

# ── Default fallback risks ───────────────────────────────────────────────────
_FALLBACK_RISKS = [
    "Technology is still in early-stage development",
    "Competitive pressure from established frameworks",
    "Limited enterprise adoption and revenue model uncertainty"
]


def _normalise(value: float, ceiling: float) -> float:
    """Linear normalisation clamped to [0, 1]."""
    if ceiling <= 0:
        return 0.0
    return round(max(0.0, min(1.0, value / ceiling)), 2)


def compute_signal_breakdown(repo_data: Dict[str, Any]) -> SignalBreakdown:
    """
    Compute individual signal component scores.

    Returns:
        SignalBreakdown with github_velocity, community_strength,
        developer_sentiment, and media_presence scores.
    """
    return SignalBreakdown(
        github_velocity=_normalise(float(safe_get(repo_data, "star_velocity", 0)), MAX_STAR_VELOCITY),
        community_strength=_normalise(float(safe_get(repo_data, "contributors", 0)), MAX_CONTRIBUTORS),
        developer_sentiment=SENTIMENT_MAP.get(
            str(safe_get(repo_data, "social_sentiment", "neutral")).lower(), 0.5
        ),
        media_presence=_normalise(float(safe_get(repo_data, "news_mentions", 0)), MAX_NEWS_MENTIONS)
    )


def compute_conviction_score(repo_data: Dict[str, Any]) -> float:
    """
    Compute the weighted conviction score from signal breakdown.

    Formula:
      CS = 0.4×github_velocity + 0.3×community_strength
         + 0.2×developer_sentiment + 0.1×media_presence
    """
    sb = compute_signal_breakdown(repo_data)
    cs = (
        0.4 * sb.github_velocity
        + 0.3 * sb.community_strength
        + 0.2 * sb.developer_sentiment
        + 0.1 * sb.media_presence
    )
    return round(max(0.0, min(1.0, cs)), 2)


def _extract_risks(memo_text: str, repo_data: Dict[str, Any]) -> List[str]:
    """
    Extract structured risks from the memo text using Gemini (with retry).
    Falls back to default risks on failure.
    """
    safe_name = sanitize_input(safe_get(repo_data, "repo_name", "Unknown"))
    safe_memo = truncate(memo_text, 2000)

    prompt = f"""
You are a risk analyst at a venture capital firm.

Given this investment memo about "{safe_name}":

{safe_memo}

Extract exactly 3-5 key investment risks. Each risk should be a single
concise sentence (max 15 words).

Respond in EXACTLY this JSON format (no markdown fences, pure JSON):
{{
  "risks": [
    "<risk 1>",
    "<risk 2>",
    "<risk 3>"
  ]
}}
""".strip()

    try:
        raw, err = call_llm_with_retry(_model, prompt)
        if raw is None:
            logger.warning(f"LLM unavailable for risk extraction ({err}) — using fallback.")
            return list(_FALLBACK_RISKS)

        raw = strip_markdown_fences(raw)
        data = json.loads(raw)
        risks = data.get("risks", [])
        return risks if risks else list(_FALLBACK_RISKS)
    except Exception as e:
        logger.warning(f"Risk extraction failed: {e}. Using fallback risks.")
        return list(_FALLBACK_RISKS)


def generate_investment_memo(project_data: Dict[str, Any]) -> MemoOutput:
    """
    Generate a structured VC investment memo with conviction score,
    signal breakdown, and extracted risks.

    Args:
        project_data: Combined dict of repo signals + analysis outputs.

    Returns:
        MemoOutput with memo, conviction_score, signal_breakdown, risks.
    """
    repo_name = safe_get(project_data, "repo_name", "Unknown")
    logger.info(f"Generating investment memo for: {repo_name}")

    # Compute conviction score and signal breakdown
    signal_breakdown = compute_signal_breakdown(project_data)
    conv_score = round(
        0.4 * signal_breakdown.github_velocity
        + 0.3 * signal_breakdown.community_strength
        + 0.2 * signal_breakdown.developer_sentiment
        + 0.1 * signal_breakdown.media_presence,
        2
    )
    project_data["conviction_score"] = conv_score

    # Generate memo text via Gemini Flash (with retry)
    prompt = investment_memo_prompt(project_data)
    memo_text, err = call_llm_with_retry(_model, prompt)

    if memo_text is None:
        logger.warning(f"LLM unavailable for memo generation ({err}) — using fallback memo.")
        safe_err = err.replace('\n', ' ')
        memo_text = (
            f"## Investment Memo — {repo_name}\n\n"
            f"AI-generated memo unavailable due to LLM service issues. Reason: {safe_err}. "
            f"Conviction score: {conv_score:.2f}/1.00. "
            f"Please retry or review quantitative signals manually."
        )

    # Extract structured risks from the memo
    risks = _extract_risks(memo_text, project_data)

    return MemoOutput(
        memo=memo_text,
        conviction_score=conv_score,
        signal_breakdown=signal_breakdown,
        risks=risks
    )
