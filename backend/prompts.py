# Prompt Engineering Templates
# Collection of carefully crafted prompts for different analysis tasks

class PromptTemplates:
    """
    Prompt engineering templates for Gen AI analysis
    Each prompt is optimized for specific tasks
    """
    
    @staticmethod
    def repository_analysis_prompt(repo_data):
        """
        Prompt for analyzing repository technology and potential
        """
        schema = {
            "technology_summary": "string",
            "innovation_score": 75,
            "technical_complexity": "Medium",
            "scalability_potential": "High",
            "key_strengths": ["strength1", "strength2"],
            "technical_risks": ["risk1", "risk2"],
            "market_fit": "string",
            "competitive_advantage": "string",
            "recommendation": "Monitor"
        }
        
        return f"""You are an expert venture capital analyst specializing in technology evaluation.

Analyze this GitHub repository and provide a comprehensive technical assessment:

Repository: {repo_data.get('repo_name')}
Description: {repo_data.get('description', 'No description')}
Stars: {repo_data.get('stars', 0)}
Forks: {repo_data.get('forks', 0)}
Primary Language: {repo_data.get('primary_language', 'Unknown')}
Topics: {', '.join(repo_data.get('topics', [])) or 'None'}
Age: {repo_data.get('age_days', 0)} days

Provide your analysis in EXACTLY this JSON format (no extra text):
{{
    "technology_summary": "Brief overview of the technology stack and architecture",
    "innovation_score": 75,
    "technical_complexity": "Medium",
    "scalability_potential": "High",
    "key_strengths": ["strength1", "strength2", "strength3"],
    "technical_risks": ["risk1", "risk2"],
    "market_fit": "Assessment of product-market fit",
    "competitive_advantage": "What makes this unique",
    "recommendation": "Monitor"
}}"""
    
    @staticmethod
    def investment_memo_prompt(analysis_data):
        """
        Prompt for generating investment memo
        """
        return f"""You are a senior venture capital partner writing an investment memo.

Based on the following analysis, create a comprehensive investment memo:

Project: {analysis_data.get('repo_name')}
Technology Summary: {analysis_data.get('technology_summary')}
Market Potential: {analysis_data.get('market_potential')}
Team Strength: {analysis_data.get('team_strength')}
Traction: {analysis_data.get('stars')} stars, {analysis_data.get('forks')} forks

Write a professional investment memo covering:
1. Executive Summary (2-3 sentences)
2. Market Opportunity
3. Product/Technology Assessment
4. Traction & Metrics
5. Investment Thesis
6. Key Risks
7. Recommendation (Invest/Pass/Monitor)
8. Conviction Score (0-100)

Format as a clear, professional memo."""
    
    @staticmethod
    def sentiment_analysis_prompt(text):
        """
        Prompt for sentiment analysis of project description
        """
        return f"""Analyze the sentiment and tone of this project description:

"{text or 'No description provided'}"

Provide analysis in EXACTLY this JSON format (no extra text):
{{
    "sentiment": "Positive",
    "confidence": 80,
    "key_emotions": ["enthusiasm", "innovation"],
    "enthusiasm_level": 75,
    "professionalism_score": 85,
    "market_positioning": "How the project positions itself"
}}"""
    
    @staticmethod
    def trend_detection_prompt(repo_data, market_context):
        """
        Prompt for detecting if project aligns with trends
        """
        return f"""You are a technology trend analyst for venture capital.

Evaluate if this project aligns with current technology trends:

Project: {repo_data.get('repo_name')}
Description: {repo_data.get('description', 'No description')}
Technology: {repo_data.get('primary_language', 'Unknown')}
Topics: {', '.join(repo_data.get('topics', [])) or 'None'}

Current Market Context:
{market_context}

Provide trend analysis in EXACTLY this JSON format (no extra text):
{{
    "trend_alignment": 75,
    "trending_categories": ["AI/ML", "DevTools"],
    "market_timing": "Peak",
    "growth_potential": 80,
    "trend_sustainability": "Long-term",
    "competitive_landscape": "Description of competition",
    "recommendation": "Buy"
}}"""
    
    @staticmethod
    def code_quality_prompt(readme_content, language):
        """
        Prompt for evaluating code quality from README
        """
        return f"""As a senior software architect, evaluate the code quality and engineering practices based on this README:

Language: {language}
README Content:
{readme_content[:1000]}...

Evaluate and respond in JSON:
{{
    "documentation_quality": 0-100,
    "architecture_clarity": 0-100,
    "best_practices": ["practice1", "practice2"],
    "red_flags": ["flag1", "flag2"],
    "maintainability_score": 0-100,
    "testing_approach": "Description",
    "overall_quality": 0-100
}}

Evaluation:"""
    
    @staticmethod
    def competitive_analysis_prompt(repo1_data, repo2_data):
        """
        Prompt for comparing two projects
        """
        return f"""Compare these two projects from an investment perspective:

PROJECT A:
Name: {repo1_data.get('repo_name')}
Description: {repo1_data.get('description')}
Stars: {repo1_data.get('stars')}
Technology: {repo1_data.get('primary_language')}

PROJECT B:
Name: {repo2_data.get('repo_name')}
Description: {repo2_data.get('description')}
Stars: {repo2_data.get('stars')}
Technology: {repo2_data.get('primary_language')}

Provide comparative analysis in JSON:
{{
    "winner": "Project A/Project B/Tie",
    "project_a_score": 0-100,
    "project_b_score": 0-100,
    "comparison": {{
        "technology": "Which has better tech",
        "market_fit": "Which has better market fit",
        "traction": "Which has better traction",
        "team": "Which has better team indicators"
    }},
    "investment_recommendation": "Which to invest in and why",
    "key_differentiators": ["diff1", "diff2"]
}}

Analysis:"""
    
    @staticmethod
    def risk_assessment_prompt(repo_data):
        """
        Prompt for identifying investment risks
        """
        return f"""As a venture capital risk analyst, identify potential risks for this investment:

Project: {repo_data.get('repo_name')}
Description: {repo_data.get('description', 'No description')}
Age: {repo_data.get('age_days', 0)} days
Activity: Last updated {repo_data.get('updated_at', 'Unknown')}
License: {repo_data.get('license', 'Unknown')}

Identify risks in EXACTLY this JSON format (no extra text):
{{
    "technical_risks": ["risk1", "risk2"],
    "market_risks": ["risk1", "risk2"],
    "execution_risks": ["risk1", "risk2"],
    "competitive_risks": ["risk1", "risk2"],
    "overall_risk_level": "Medium",
    "risk_score": 60,
    "mitigation_strategies": ["strategy1", "strategy2"]
}}"""
    
    @staticmethod
    def market_sizing_prompt(repo_data):
        """
        Prompt for estimating market size
        """
        return f"""Estimate the total addressable market (TAM) for this project:

Project: {repo_data.get('repo_name')}
Description: {repo_data.get('description', 'No description')}
Category: {', '.join(repo_data.get('topics', [])) or 'General'}

Provide market analysis in EXACTLY this JSON format (no extra text):
{{
    "tam_estimate": "$100M - $500M",
    "target_market": "Description of target users",
    "market_growth_rate": "15%",
    "market_maturity": "Growing",
    "addressable_segment": "Specific segment this targets",
    "monetization_potential": 70,
    "market_size_score": 75
}}"""
