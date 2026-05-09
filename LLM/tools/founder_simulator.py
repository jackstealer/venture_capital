"""
tools/founder_simulator.py
---------------------------
Tool 3 — Founder Interview Simulator

Two-stage pipeline:
  Pass 1 → Gemini generates 5 probing investor questions
  Pass 2 → Gemini simulates founder responses using repo context

Includes retry logic with fallback at every stage.
"""

import json
import logging
from typing import Dict, Any, List

import google.generativeai as genai

from config import settings
from models.schemas import InterviewOutput
from utils.prompt_templates import (
    founder_interview_questions_prompt,
    founder_interview_answers_prompt
)
from utils.resilience import (
    call_llm_with_retry,
    strip_markdown_fences,
    safe_get,
)

logger = logging.getLogger(__name__)

# Configure the Gemini SDK with the API key
genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)


def _call_llm(prompt: str) -> str:
    """Call Gemini Flash with retry. Returns empty string on total failure."""
    result, err = call_llm_with_retry(_model, prompt)
    if result is None:
        logger.warning(f"Founder Simulator LLM failed: {err}")
    return result if result is not None else ""


def _parse_json_list(raw: str, key: str) -> List[str]:
    """
    Safely parse a JSON object and extract a list under `key`.
    Handles markdown-fenced responses from Gemini.
    """
    if not raw:
        return []

    text = strip_markdown_fences(raw)

    try:
        data = json.loads(text)
        return data.get(key, [])
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON for key '{key}': {text[:200]}")
        lines = [line.strip(" -•\t") for line in text.splitlines() if line.strip()]
        return lines[:5]


def simulate_founder_interview(repo_analysis: Dict[str, Any]) -> InterviewOutput:
    """
    Simulate a founder interview for a given project.

    Args:
        repo_analysis: Dict containing repo_name, technology_summary,
                       key_use_cases, industry_impact.

    Returns:
        InterviewOutput with matched questions and answers lists.
    """
    repo_name = safe_get(repo_analysis, "repo_name", "Unknown Project")
    logger.info(f"Simulating founder interview for: {repo_name}")

    # ── Pass 1: Generate Questions ────────────────────────────────────────────
    q_raw = _call_llm(founder_interview_questions_prompt(repo_analysis))
    questions = _parse_json_list(q_raw, "questions")

    if not questions:
        logger.warning("Question generation failed — using default questions.")
        questions = [
            f"What core problem does {repo_name} solve that existing tools cannot?",
            "What is your primary competitive moat?",
            "How do you plan to monetise this open-source project?",
            "Who is your target enterprise customer and what is your GTM strategy?",
            "Where do you see this project in three to five years?"
        ]

    # ── Pass 2: Simulate Founder Answers ─────────────────────────────────────
    a_raw = _call_llm(founder_interview_answers_prompt(repo_analysis, questions))
    answers = _parse_json_list(a_raw, "answers")

    if not answers:
        logger.warning("Answer generation failed — using fallback answers.")
        answers = [
            f"{repo_name} addresses a critical gap in the current tooling landscape.",
            "Our moat is built on deep technical expertise and community trust.",
            "We plan a freemium model with enterprise support tiers.",
            "Our initial target is developer-first startups and mid-market tech companies.",
            "We see this becoming the industry standard within 3-5 years."
        ]

    # Align both lists to the same length
    max_len = max(len(questions), len(answers))
    questions = (questions + [""] * max_len)[:max_len]
    answers = (answers + ["[No answer generated]"] * max_len)[:max_len]

    return InterviewOutput(questions=questions, answers=answers)
