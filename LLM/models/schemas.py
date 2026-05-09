"""
models/schemas.py
-----------------
Pydantic v2 data models for all API inputs and outputs.
Includes Phase 2 enhancements: evidence links, signal breakdown,
risk analysis, timing, demo projects, and project comparison.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# INPUT SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class RepoInput(BaseModel):
    """Structured input representing a GitHub repository with social signals."""
    repo_name: str = Field(..., example="LangGraph", description="Name of the repository")
    repo_url: str = Field(..., example="https://github.com/langchain-ai/langgraph", description="GitHub URL")
    description: str = Field(..., example="Framework for building AI agents", description="Short repo description")
    stars: int = Field(..., ge=0, example=12000, description="Total GitHub stars")
    contributors: int = Field(..., ge=1, example=85, description="Number of contributors")
    star_velocity: float = Field(..., ge=0, example=45.0, description="Stars gained per day (recent average)")
    social_sentiment: str = Field(..., example="positive", description="Sentiment: positive / neutral / negative")
    news_mentions: int = Field(..., ge=0, example=12, description="Number of recent news/blog mentions")


class CompareProjectsInput(BaseModel):
    """Input for comparing two projects side-by-side."""
    repo1: RepoInput = Field(..., description="First repository to compare")
    repo2: RepoInput = Field(..., description="Second repository to compare")


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL BREAKDOWN (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────

class SignalBreakdown(BaseModel):
    """Individual component scores that make up the conviction score."""
    github_velocity: float = Field(..., ge=0.0, le=1.0, description="Normalised star velocity score")
    community_strength: float = Field(..., ge=0.0, le=1.0, description="Normalised contributor diversity score")
    developer_sentiment: float = Field(..., ge=0.0, le=1.0, description="Sentiment score (positive=1.0, neutral=0.5, negative=0.0)")
    media_presence: float = Field(..., ge=0.0, le=1.0, description="Normalised news/blog mentions score")


# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT SCHEMAS — individual features
# ─────────────────────────────────────────────────────────────────────────────

class TechAnalysisOutput(BaseModel):
    """Output of the Repository Technology Analyzer."""
    technology_summary: str = Field(..., description="What the technology does")
    key_use_cases: str = Field(..., description="Primary developer use-cases")
    industry_impact: str = Field(..., description="Industries this technology disrupts or enables")


class ResearchOutput(BaseModel):
    """Output of the Web Research Validator."""
    research_summary: str = Field(..., description="Aggregated insights from web research")
    sources: List[str] = Field(default_factory=list, description="List of article URLs retrieved")


class TrendOutput(BaseModel):
    """Output of the Trend Validation Agent."""
    trend_strength: str = Field(..., description="Low / Medium / High")
    reasoning: str = Field(..., description="Gemini's reasoning for the trend assessment")


class InterviewOutput(BaseModel):
    """Output of the Founder Interview Simulator."""
    questions: List[str] = Field(..., description="VC due-diligence questions")
    answers: List[str] = Field(..., description="Simulated founder answers")


class MemoOutput(BaseModel):
    """Output of the Investment Memo Generator."""
    memo: str = Field(..., description="Full structured VC investment memo text")
    conviction_score: float = Field(..., ge=0.0, le=1.0, description="Normalised conviction score 0–1")
    signal_breakdown: SignalBreakdown = Field(..., description="Individual component scores")
    risks: List[str] = Field(default_factory=list, description="Identified investment risks")


# ─────────────────────────────────────────────────────────────────────────────
# FULL PIPELINE OUTPUT (Phase 2 enhanced)
# ─────────────────────────────────────────────────────────────────────────────

class FullAnalysisOutput(BaseModel):
    """Combined output of the entire AI pipeline with Phase 2 enhancements."""
    # Tech analysis
    technology_summary: str
    key_use_cases: str
    industry_impact: str
    # Research
    research_summary: str
    sources: List[str]
    # Trend
    trend_strength: str
    trend_reasoning: str
    # Interview
    founder_interview: InterviewOutput
    # Memo + conviction
    investment_memo: str
    conviction_score: float
    # ── Phase 2 enhancements ──
    signal_breakdown: SignalBreakdown = Field(..., description="Component-level conviction breakdown")
    risks: List[str] = Field(default_factory=list, description="Key investment risks")
    evidence_sources: List[str] = Field(default_factory=list, description="All URLs backing this analysis")
    analysis_time: str = Field(default="", description="Total pipeline processing time")


# ─────────────────────────────────────────────────────────────────────────────
# DEMO & COMPARISON OUTPUTS (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────

class DemoProject(BaseModel):
    """A pre-loaded trending repository for demo purposes."""
    repo_name: str
    repo_url: str
    description: str
    stars: int
    contributors: int
    star_velocity: float
    social_sentiment: str
    news_mentions: int
    category: str = Field(default="", description="Technology category (e.g. AI Agents, DevTools)")


class DemoProjectsOutput(BaseModel):
    """Response for GET /demo_projects."""
    projects: List[DemoProject]
    total: int


class CompareProjectsOutput(BaseModel):
    """Side-by-side comparison of two projects."""
    project1_name: str
    project2_name: str
    project1_score: float
    project2_score: float
    project1_breakdown: SignalBreakdown
    project2_breakdown: SignalBreakdown
    comparison_summary: str = Field(..., description="AI-generated comparative analysis")
    recommendation: str = Field(..., description="Which project is the stronger investment and why")
    analysis_time: str = Field(default="", description="Processing time")
