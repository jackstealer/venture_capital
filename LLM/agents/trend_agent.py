"""
agents/trend_agent.py
----------------------
Agent — Trend Validation

Uses Gemini Flash (google.generativeai SDK) to assess trend strength.
Includes retry logic with heuristic fallback when LLM is unavailable.
"""

import json
import logging
from typing import Dict, Any

import google.generativeai as genai

from config import settings
from models.schemas import TrendOutput
from utils.prompt_templates import trend_validation_prompt
from utils.resilience import (
    call_llm_with_retry,
    strip_markdown_fences,
    safe_get,
)

logger = logging.getLogger(__name__)

# Configure the Gemini SDK with the API key
genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)


def _heuristic_trend(metrics: Dict[str, Any]) -> TrendOutput:
    """
    Compute trend strength from raw signals when LLM is unavailable.
    """
    sv = float(safe_get(metrics, "star_velocity", 0))
    sentiment = str(safe_get(metrics, "social_sentiment", "neutral")).lower()
    mentions = int(safe_get(metrics, "news_mentions", 0))

    if sv > 30 and sentiment == "positive" and mentions >= 10:
        trend_strength = "High"
    elif sv > 10 or (sentiment == "positive" and mentions >= 5):
        trend_strength = "Medium"
    else:
        trend_strength = "Low"

    reasoning = (
        f"Heuristic assessment: velocity={sv}, sentiment={sentiment}, mentions={mentions}"
    )
    return TrendOutput(trend_strength=trend_strength, reasoning=reasoning)


def validate_trend(metrics: Dict[str, Any]) -> TrendOutput:
    """
    Evaluate project signals and determine trend strength.

    Args:
        metrics: Dict with star_velocity, contributors, social_sentiment,
                 news_mentions.

    Returns:
        TrendOutput with trend_strength (Low/Medium/High) and reasoning.
    """
    logger.info(
        f"Validating trend — velocity={metrics.get('star_velocity')}, "
        f"sentiment={metrics.get('social_sentiment')}"
    )

    prompt = trend_validation_prompt(metrics)
    raw_text, err = call_llm_with_retry(_model, prompt)

    # Total LLM failure → fall back to heuristic
    if raw_text is None:
        logger.warning(f"LLM unavailable for trend validation ({err}) — using heuristic fallback.")
        return _heuristic_trend(metrics)

    raw_text = strip_markdown_fences(raw_text)

    try:
        data = json.loads(raw_text)
        trend_strength = data.get("trend_strength", "Medium")
        reasoning = data.get("reasoning", raw_text)
    except json.JSONDecodeError:
        logger.warning("Could not parse Gemini trend response as JSON. Using heuristic fallback.")
        return _heuristic_trend(metrics)

    # Normalise capitalisation
    if trend_strength not in {"High", "Medium", "Low"}:
        trend_strength = "Medium"

    return TrendOutput(trend_strength=trend_strength, reasoning=reasoning)
