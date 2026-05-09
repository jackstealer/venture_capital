"""
tools/github_analyzer.py
------------------------
Tool 1 — Repository Technology Analyzer

Uses Gemini Flash (google.generativeai SDK) to analyse a repository's technology.
Includes retry logic and fallback responses for robustness.
"""

import json
import logging
from typing import Dict, Any

import google.generativeai as genai

from config import settings
from models.schemas import TechAnalysisOutput
from utils.prompt_templates import technology_analysis_prompt
from utils.resilience import call_llm_with_retry, strip_markdown_fences

logger = logging.getLogger(__name__)

# Configure the Gemini SDK with the API key
genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)


def _call_llm(prompt: str) -> str:
    """
    Call Gemini Flash with retry logic and return the raw text response.
    Returns a fallback string if all retries fail.
    """
    raw, err = call_llm_with_retry(_model, prompt)
    if raw is None:
        safe_err = err.replace('"', "'").replace('\n', ' ')
        return f'{{"technology_summary":"LLM unavailable — analysis could not be completed. Reason: {safe_err}","key_use_cases":"N/A","industry_impact":"N/A"}}'
    return strip_markdown_fences(raw)


def analyze_repository(repo_data: Dict[str, Any]) -> TechAnalysisOutput:
    """
    Analyse a repository using Gemini and return structured technology insights.

    Args:
        repo_data: Dictionary matching the RepoInput schema fields.

    Returns:
        TechAnalysisOutput with technology_summary, key_use_cases,
        and industry_impact.
    """
    logger.info(f"Analysing repository: {repo_data.get('repo_name')}")

    prompt = technology_analysis_prompt(repo_data)
    raw_text = _call_llm(prompt)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse Gemini response as JSON: {raw_text[:200]}")
        data = {
            "technology_summary": raw_text,
            "key_use_cases": "See technology_summary for details.",
            "industry_impact": "Unable to parse structured response."
        }

    return TechAnalysisOutput(
        technology_summary=data.get("technology_summary", ""),
        key_use_cases=data.get("key_use_cases", ""),
        industry_impact=data.get("industry_impact", "")
    )
