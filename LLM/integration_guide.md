# Venture-Alpha AI Intelligence Layer - Integration Guide

This document outlines the architecture, technology stack, and integration details for the **Venture-Alpha AI Intelligence Layer**.

## 🚀 Technology Stack

The project is built using a modern, lightweight, and AI-native stack:

- **Framework**: `FastAPI` (High-performance web framework for APIs)
- **Server**: `Uvicorn` (ASGI web server implementation for Python)
- **AI / LLM Orchestration**: `LangChain` & `langchain-google-genai`
- **Primary LLM**: **Google Gemini** (`gemini-2.0-flash` / `gemini-1.5-flash`) via `google-generativeai`
- **Web Research / Search**: `Exa Search` via `exa-py`
- **Data Validation & Schemas**: `Pydantic`
- **Environment Management**: `python-dotenv`
- **Networking**: `requests`
- **Language**: `Python 3.x`

## 🏗️ Architecture & Modules Built

The backend follows a modular, agent-based architecture designed for AI workflows:

### 1. API Entry Point (`app.py`)
Provides REST API endpoints using FastAPI with CORS enabled.

### 2. Configuration (`config.py` & `.env`)
Centralized configuration management. It loads API keys (Gemini, Exa Search) from the environment.

### 3. Data Models (`models/schemas.py`)
Uses Pydantic for strict input/output validation, ensuring structured JSON responses to the frontend.
Contains schemas like:
- `RepoInput`: Structured GitHub repo data.
- Outputs: `TechAnalysisOutput`, `TrendOutput`, `InterviewOutput`, `MemoOutput`, `FullAnalysisOutput`, `CompareProjectsOutput`.

### 4. AI Tools (`tools/`)
Specific tools designated for discrete analytical tasks.
- **`github_analyzer.py`**: Analyzes repository structure, architecture, and technology capabilities using Gemini.
- **`research_tool.py`**: Executes live web searches using the Exa Search API to find external validations, news, and discussions.
- **`founder_simulator.py`**: Generates a simulated VC founder interview with key Q&A based on the repository's tech.

### 5. AI Agents (`agents/`)
Agents that orchestrate tools and use LLMs for higher-level reasoning.
- **`trend_agent.py`**: Validates whether a project represents an emerging market trend.
- **`memo_agent.py`**: Synthesizes all data to generate an investment memo, computes a composite `conviction_score (0-100)`, outlines key risk factors, and provides a nuanced signal breakdown (e.g., tech, team, market).

### 6. Services / Workflows (`services/`)
- **`analysis_service.py`**: Orchestrates the multi-step full pipeline (Technology -> Research -> Trend -> Interview -> Memo) and Handles project comparisons.

## 🔌 API Endpoints for Integration

The following endpoints are exposed for frontend or external service integration:

| Method | Endpoint | Description |
|---|---|---|
| **GET** | `/` | Health check endpoint to verify service status. |
| **POST** | `/analyze_repository` | Performs a deep technical analysis of a GitHub repository input. |
| **POST** | `/validate_trend` | Analyzes market strength and confirms if the repo matches an emerging trend. |
| **POST** | `/founder_interview` | Simulates a due-diligence founder interview based on the tech stack. |
| **POST** | `/generate_memo` | Generates a final VC investment memo with conviction score and risk breakdown. |
| **POST** | `/full_analysis` | **(Recommended)** Executes the entire 5-step pipeline and returns a comprehensive combined JSON report. |
| **GET** | `/demo_projects` | Instantly returns 5 curated trending repositories for demo and UI testing purposes without triggering AI calls. |
| **POST** | `/compare_projects` | Compares two distinct repositories side-by-side, analyzing differences and delivering a holistic winner recommendation. |

## 🔗 How to Integrate (Frontend / Client)

1. Ensure the backend is running locally or deployed:
   ```bash
   uvicorn app:app --reload --port 8000
   ```
2. The interactive Swagger UI documentation is available at:
   - **`http://127.0.0.1:8000/docs`**
   - You can view the exact JSON payload structures required for each endpoint there.
3. Make standard HTTP POST requests from your frontend passing the `RepoInput` payload (containing GitHub stars, description, url, languages, etc.) as application/json.

## 🔑 Environment Variables Required

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
EXA_API_KEY=your_exa_search_api_key
```
