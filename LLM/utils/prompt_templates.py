"""
utils/prompt_templates.py
--------------------------
Reusable, parameterised prompt strings for all Gemini calls.

Design principles:
  • Each builder function accepts typed arguments and returns a plain str.
  • Prompts are explicit and structured so Gemini returns predictable outputs.
  • All prompts instruct the model to stay factual and concise (hackathon-safe).
  • All user-supplied fields are sanitized and truncated before interpolation.
"""

from typing import Dict, Any, List

from utils.resilience import safe_get, sanitize_input, truncate


# ─────────────────────────────────────────────────────────────────────────────
# 1. TECHNOLOGY ANALYSIS PROMPT
# ─────────────────────────────────────────────────────────────────────────────

def technology_analysis_prompt(repo_data: Dict[str, Any]) -> str:
    """
    Builds a prompt asking Gemini to analyse a repository's technology.

    Args:
        repo_data: dict with keys repo_name, description, stars, contributors.

    Returns:
        Formatted prompt string.
    """
    name  = sanitize_input(safe_get(repo_data, "repo_name", "Unknown"))
    desc  = truncate(sanitize_input(safe_get(repo_data, "description", "N/A")), 500)
    stars = safe_get(repo_data, "stars", 0)
    contribs = safe_get(repo_data, "contributors", 0)
    velocity = safe_get(repo_data, "star_velocity", 0)

    return f"""
You are a senior technology analyst at a top venture capital firm.

Analyse the following open-source repository and provide a structured assessment.

Repository Details:
  - Name        : {name}
  - Description : {desc}
  - GitHub Stars: {stars:,}
  - Contributors: {contribs}
  - Star Velocity (stars/day): {velocity}

Respond in EXACTLY this JSON format (no markdown fences, pure JSON):
{{
  "technology_summary": "<2-3 sentence explanation of what this technology does and how it works>",
  "key_use_cases": "<comma-separated list of 3-5 primary developer use-cases>",
  "industry_impact": "<which industries this technology disrupts or enables and why>"
}}
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# 2. TREND VALIDATION PROMPT
# ─────────────────────────────────────────────────────────────────────────────

def trend_validation_prompt(metrics: Dict[str, Any]) -> str:
    """
    Builds a prompt asking Gemini to evaluate whether a project represents
    an emerging tech trend.

    Args:
        metrics: dict with star_velocity, contributors, social_sentiment,
                 news_mentions.

    Returns:
        Formatted prompt string.
    """
    velocity  = safe_get(metrics, "star_velocity", 0)
    contribs  = safe_get(metrics, "contributors", 0)
    sentiment = sanitize_input(str(safe_get(metrics, "social_sentiment", "neutral")))
    mentions  = safe_get(metrics, "news_mentions", 0)

    return f"""
You are a venture capital trend analyst specialising in emerging technologies.

Evaluate the following project signals and determine the strength of the
technology trend this project represents.

Signals:
  - Star Velocity (stars added per day) : {velocity}
  - Number of Contributors              : {contribs}
  - Social Sentiment                    : {sentiment}
  - News / Blog Mentions (recent)       : {mentions}

Trend Strength Criteria:
  High   → Rapidly growing community, positive sentiment, multiple news mentions
  Medium → Moderate growth, mixed signals, some traction
  Low    → Slow growth, limited community, little external validation

Respond in EXACTLY this JSON format (no markdown fences, pure JSON):
{{
  "trend_strength": "<High|Medium|Low>",
  "reasoning": "<3-4 sentences explaining your assessment based on the signals above>"
}}
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# 3. FOUNDER INTERVIEW PROMPT
# ─────────────────────────────────────────────────────────────────────────────

def founder_interview_questions_prompt(repo_analysis: Dict[str, Any]) -> str:
    """
    Prompt: generate VC due-diligence questions for this project.

    Args:
        repo_analysis: dict with technology_summary, key_use_cases,
                       industry_impact, repo_name.

    Returns:
        Formatted prompt string.
    """
    name     = sanitize_input(safe_get(repo_analysis, "repo_name", "Unknown"))
    tech     = truncate(sanitize_input(safe_get(repo_analysis, "technology_summary", "")), 500)
    uses     = truncate(sanitize_input(safe_get(repo_analysis, "key_use_cases", "")), 500)
    impact   = truncate(sanitize_input(safe_get(repo_analysis, "industry_impact", "")), 500)

    return f"""
You are a Partner at a top-tier venture capital firm conducting a first-meeting
due diligence call with the founders of the following project:

Project: {name}
Technology Summary: {tech}
Key Use Cases: {uses}
Industry Impact: {impact}

Generate exactly 5 sharp, probing VC due-diligence questions covering:
  1. The core problem being solved
  2. Competitive advantage / moat
  3. Monetisation model
  4. Target market and customer segment
  5. Long-term vision (3-5 year)

Respond in EXACTLY this JSON format (no markdown fences, pure JSON):
{{
  "questions": [
    "<question 1>",
    "<question 2>",
    "<question 3>",
    "<question 4>",
    "<question 5>"
  ]
}}
""".strip()


def founder_interview_answers_prompt(
    repo_analysis: Dict[str, Any],
    questions: List[str]
) -> str:
    """
    Prompt: simulate founder answers to the given VC questions.

    Args:
        repo_analysis: same dict used for questions.
        questions: list of question strings.

    Returns:
        Formatted prompt string.
    """
    name   = sanitize_input(safe_get(repo_analysis, "repo_name", "this project"))
    tech   = truncate(sanitize_input(safe_get(repo_analysis, "technology_summary", "")), 500)
    uses   = truncate(sanitize_input(safe_get(repo_analysis, "key_use_cases", "")), 500)
    impact = truncate(sanitize_input(safe_get(repo_analysis, "industry_impact", "")), 500)

    # Sanitize each question too
    safe_questions = [sanitize_input(truncate(q, 300)) for q in questions]
    questions_text = "\n".join(
        f"  Q{i+1}: {q}" for i, q in enumerate(safe_questions)
    )

    return f"""
You are the founder of {name}.

Project context:
  Technology: {tech}
  Use Cases : {uses}
  Industries: {impact}

Answer the following VC questions as the founder. Be confident, specific,
and data-driven. Each answer should be 2-4 sentences.

{questions_text}

Respond in EXACTLY this JSON format (no markdown fences, pure JSON):
{{
  "answers": [
    "<answer to Q1>",
    "<answer to Q2>",
    "<answer to Q3>",
    "<answer to Q4>",
    "<answer to Q5>"
  ]
}}
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# 4. INVESTMENT MEMO PROMPT
# ─────────────────────────────────────────────────────────────────────────────

def investment_memo_prompt(project_data: Dict[str, Any]) -> str:
    """
    Builds a prompt asking Gemini to write a structured VC investment memo.

    Args:
        project_data: combined dict of repo signals + analysis results.

    Returns:
        Formatted prompt string.
    """
    name      = sanitize_input(safe_get(project_data, "repo_name", "Unknown"))
    desc      = truncate(sanitize_input(safe_get(project_data, "description", "")), 500)
    stars     = safe_get(project_data, "stars", 0)
    contribs  = safe_get(project_data, "contributors", 0)
    velocity  = safe_get(project_data, "star_velocity", 0)
    sentiment = sanitize_input(str(safe_get(project_data, "social_sentiment", "neutral")))
    mentions  = safe_get(project_data, "news_mentions", 0)
    trend     = sanitize_input(safe_get(project_data, "trend_strength", "Unknown"))
    conv      = safe_get(project_data, "conviction_score", 0)
    tech_sum  = truncate(sanitize_input(safe_get(project_data, "technology_summary", "")), 800)
    research  = truncate(sanitize_input(safe_get(project_data, "research_summary", "")), 800)

    return f"""
You are a Managing Partner at a top venture capital firm.

Write a professional investment memo for the following project.
The memo will be shared with the investment committee.

Project Data:
  - Repository      : {name}
  - Description     : {desc}
  - GitHub Stars    : {stars:,}
  - Contributors    : {contribs}
  - Star Velocity   : {velocity} stars/day
  - Social Sentiment: {sentiment}
  - News Mentions   : {mentions}
  - Trend Strength  : {trend}
  - Conviction Score: {conv:.2f} / 1.00

Technology Analysis:
  {tech_sum}

Research Insights:
  {research}

Write the memo with EXACTLY these five sections:

## Technology Overview
<What it is and how it works>

## Market Opportunity
<Total addressable market, growth drivers, timing>

## Key Signals
<Star velocity, contributor growth, sentiment, and news as investment signals>

## Risks
<Key technical, market, and competitive risks>

## Investment Recommendation
<Clear recommendation: Invest / Watch / Pass — and rationale>

Keep the memo concise but professional. This is a real investment document.
""".strip()
