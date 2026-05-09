"""
utils/resilience.py
--------------------
Centralised robustness and security helpers used by every AI module.

Provides:
  • safe_get        — missing-field-safe dict accessor
  • call_llm_with_retry — exponential-backoff wrapper around genai
  • sanitize_input  — strip prompt-injection markers from user text
  • truncate        — hard-cap string length
  • strip_markdown_fences — shared ```json fence removal
"""

import re
import time
import logging
from typing import Any, Dict, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# SAFE DATA ACCESS
# ─────────────────────────────────────────────────────────────────────────────

def safe_get(data: Dict[str, Any], key: str, default: Any = "N/A") -> Any:
    """
    Safely retrieve a value from a dict, returning *default* when the key
    is missing **or** when the stored value is None.
    """
    value = data.get(key, default)
    return value if value is not None else default


# ─────────────────────────────────────────────────────────────────────────────
# INPUT SANITIZATION (Prompt Injection Protection)
# ─────────────────────────────────────────────────────────────────────────────

# Patterns that could trick the LLM into changing behaviour
_INJECTION_PATTERNS = re.compile(
    r"("
    r"IGNORE\s+(ALL\s+)?(PREVIOUS|ABOVE|PRIOR)\s+(INSTRUCTIONS?|PROMPTS?|RULES?)"
    r"|SYSTEM\s*:"
    r"|<\s*/?\s*(?:system|assistant|user)\s*>"       # role-override tags
    r"|```\s*(?:system|instruction)"                  # fenced injection
    r"|(?:^|\n)\s*(?:You are now|Act as|Pretend)"     # persona hijack
    r")",
    re.IGNORECASE,
)

# Characters that could break prompt structure
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_input(text: str) -> str:
    """
    Clean user-supplied text before interpolating it into a prompt.

    Steps:
      1. Strip control characters
      2. Replace known prompt-injection patterns with [REDACTED]
      3. Collapse excessive whitespace
      4. Enforce max length (2000 chars)
    """
    if not isinstance(text, str):
        return str(text)

    text = _CONTROL_CHARS.sub("", text)
    text = _INJECTION_PATTERNS.sub("[REDACTED]", text)
    text = re.sub(r"\s{3,}", "  ", text)       # collapse runs of 3+ spaces
    text = re.sub(r"\n{3,}", "\n\n", text)     # collapse runs of 3+ newlines
    return text[:2000]


# ─────────────────────────────────────────────────────────────────────────────
# TRUNCATION
# ─────────────────────────────────────────────────────────────────────────────

def truncate(text: str, max_len: int = 500) -> str:
    """Hard-cap a string to *max_len* characters."""
    if not isinstance(text, str):
        return str(text)[:max_len]
    return text[:max_len]


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN FENCE STRIPPING
# ─────────────────────────────────────────────────────────────────────────────

def strip_markdown_fences(raw: str) -> str:
    """
    Remove ```json ... ``` wrappers that Gemini sometimes adds
    even when the prompt says "no markdown fences".
    """
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return text


# ─────────────────────────────────────────────────────────────────────────────
# LLM CALL WITH RETRY + EXPONENTIAL BACKOFF
# ─────────────────────────────────────────────────────────────────────────────

def call_llm_with_retry(
    model: genai.GenerativeModel,
    prompt: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> tuple[Optional[str], str]:
    """
    Call *model.generate_content(prompt)* with exponential backoff.

    Returns:
        A tuple of (text, error_message). On success, text is the stripped 
        response and error_message is empty. On failure, text is None and 
        error_message contains the exception details.
    """
    delay = initial_delay
    last_error = "Unknown error"

    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(prompt)

            # Gemini may return a response with no text (safety filter, empty)
            if response and response.text:
                return response.text.strip(), ""

            last_error = "LLM returned empty response (safety filter or empty output)"
            logger.warning(
                f"LLM returned empty response (attempt {attempt}/{max_retries})"
            )
        except Exception as e:
            last_error = str(e)
            logger.warning(
                f"LLM call failed (attempt {attempt}/{max_retries}): {e}"
            )

        if attempt < max_retries:
            logger.info(f"Retrying in {delay:.1f}s …")
            time.sleep(delay)
            delay *= 2       # exponential backoff: 1s → 2s → 4s

    logger.error(f"LLM call failed after {max_retries} retries. Last error: {last_error}")
    return None, last_error
