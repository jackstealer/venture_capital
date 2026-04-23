from llm_client import LLMClient
from datetime import datetime

class MemoGenerator:
    
    def __init__(self):
        self.llm = LLMClient(provider='gemini')
    
    def generate_memo(self, repo_data, analysis_data, scoring_result):
        print(f"📝 Generating investment memo for {repo_data.get('repo_name')}...")
        
        # Generate each section
        executive_summary = self._generate_executive_summary(repo_data, scoring_result)
        market_analysis = self._generate_market_analysis(repo_data, analysis_data)
        product_assessment = self._generate_product_assessment(repo_data, analysis_data)
        traction_metrics = self._generate_traction_section(repo_data)
        investment_thesis = self._generate_investment_thesis(repo_data, scoring_result)
        risk_analysis = self._generate_risk_analysis(repo_data, analysis_data)
        recommendation = self._generate_recommendation(scoring_result)
        
        # Compile full memo
        full_memo = self._compile_memo(
            repo_data,
            executive_summary,
            market_analysis,
            product_assessment,
            traction_metrics,
            investment_thesis,
            risk_analysis,
            recommendation,
            scoring_result
        )
        
        return {
            'memo': full_memo,
            'conviction_score': scoring_result['final_score'],
            'recommendation': scoring_result['recommendation'],
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_executive_summary(self, repo_data, scoring_result):
        """Generate executive summary"""
        prompt = f"""Write a 2-3 sentence executive summary for this investment opportunity:

Project: {repo_data.get('repo_name')}
Description: {repo_data.get('description')}
Score: {scoring_result['final_score']}/100
Recommendation: {scoring_result['recommendation']}

Write a compelling executive summary that captures the essence of this opportunity."""
        
        return self.llm.generate(prompt, temperature=0.7)
    
    def _generate_market_analysis(self, repo_data, analysis_data):
        """Generate market analysis section"""
        topics = ', '.join(repo_data.get('topics', []))
        
        prompt = f"""Analyze the market opportunity for this project:

Project: {repo_data.get('repo_name')}
Category: {topics}
Description: {repo_data.get('description')}

Provide a brief market analysis covering:
1. Target market size
2. Market trends
3. Competitive landscape

Keep it concise (3-4 sentences)."""
        
        return self.llm.generate(prompt, temperature=0.6)
    
    def _generate_product_assessment(self, repo_data, analysis_data):
        """Generate product/technology assessment"""
        prompt = f"""Assess the product and technology for this project:

Project: {repo_data.get('repo_name')}
Technology: {repo_data.get('primary_language')}
Description: {repo_data.get('description')}

Provide a brief assessment covering:
1. Technology stack
2. Innovation level
3. Technical advantages

Keep it concise (3-4 sentences)."""
        
        return self.llm.generate(prompt, temperature=0.6)
    
    def _generate_traction_section(self, repo_data):
        """Generate traction metrics section"""
        stars = repo_data.get('stars', 0)
        forks = repo_data.get('forks', 0)
        age_days = repo_data.get('age_days', 1)
        
        velocity = stars / age_days if age_days > 0 else 0
        
        return f"""
Traction Metrics:
- GitHub Stars: {stars:,}
- Forks: {forks:,}
- Age: {age_days} days
- Star Velocity: {velocity:.2f} stars/day
- Community Engagement: {'High' if stars > 1000 else 'Medium' if stars > 100 else 'Low'}
"""
    
    def _generate_investment_thesis(self, repo_data, scoring_result):
        """Generate investment thesis"""
        score = scoring_result['final_score']
        breakdown = scoring_result['breakdown']
        
        # Find top 2 strengths
        sorted_factors = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        top_strengths = sorted_factors[:2]
        
        prompt = f"""Write an investment thesis for this project:

Project: {repo_data.get('repo_name')}
Score: {score}/100
Top Strengths: {top_strengths[0][0]} ({top_strengths[0][1]}/100), {top_strengths[1][0]} ({top_strengths[1][1]}/100)

Write a compelling 3-4 sentence investment thesis explaining why this is a good (or bad) investment."""
        
        return self.llm.generate(prompt, temperature=0.7)
    
    def _generate_risk_analysis(self, repo_data, analysis_data):
        """Generate risk analysis"""
        age_days = repo_data.get('age_days', 0)
        activity = repo_data.get('activity_score', 0)
        
        risks = []
        if age_days < 90:
            risks.append("Early-stage project with unproven track record")
        if activity < 30:
            risks.append("Low recent activity may indicate abandonment risk")
        if repo_data.get('license') == 'No License':
            risks.append("No license specified - legal uncertainty")
        
        if not risks:
            risks.append("Standard market and execution risks")
        
        return "Key Risks:\n" + "\n".join(f"- {risk}" for risk in risks)
    
    def _generate_recommendation(self, scoring_result):
        """Generate final recommendation"""
        score = scoring_result['final_score']
        recommendation = scoring_result['recommendation']
        grade = scoring_result['grade']
        
        if score >= 80:
            action = "PROCEED with investment. Schedule deep-dive due diligence."
        elif score >= 65:
            action = "CONSIDER investment after additional due diligence."
        elif score >= 50:
            action = "MONITOR for 3-6 months before making decision."
        else:
            action = "PASS on this opportunity. Focus resources elsewhere."
        
        return f"""
Final Recommendation: {recommendation}
Grade: {grade}
Conviction Score: {score}/100

Action: {action}
"""
    
    def _compile_memo(self, repo_data, exec_summary, market, product, traction, thesis, risks, recommendation, scoring):
        """Compile all sections into final memo"""
        memo = f"""
═══════════════════════════════════════════════════════════════
                    INVESTMENT MEMO
═══════════════════════════════════════════════════════════════

Project: {repo_data.get('repo_name')}
URL: {repo_data.get('repo_url')}
Date: {datetime.now().strftime('%B %d, %Y')}
Analyst: AI Investment Analysis System

───────────────────────────────────────────────────────────────
EXECUTIVE SUMMARY
───────────────────────────────────────────────────────────────

{exec_summary}

───────────────────────────────────────────────────────────────
MARKET OPPORTUNITY
───────────────────────────────────────────────────────────────

{market}

───────────────────────────────────────────────────────────────
PRODUCT & TECHNOLOGY ASSESSMENT
───────────────────────────────────────────────────────────────

{product}

───────────────────────────────────────────────────────────────
TRACTION & METRICS
───────────────────────────────────────────────────────────────

{traction}

───────────────────────────────────────────────────────────────
INVESTMENT THESIS
───────────────────────────────────────────────────────────────

{thesis}

───────────────────────────────────────────────────────────────
RISK ANALYSIS
───────────────────────────────────────────────────────────────

{risks}

───────────────────────────────────────────────────────────────
SCORING BREAKDOWN
───────────────────────────────────────────────────────────────

"""
        
        for factor, score in scoring['breakdown'].items():
            memo += f"{factor.title()}: {score}/100\n"
        
        memo += f"""
───────────────────────────────────────────────────────────────
RECOMMENDATION
───────────────────────────────────────────────────────────────

{recommendation}

═══════════════════════════════════════════════════════════════
                    END OF MEMO
═══════════════════════════════════════════════════════════════
"""
        
        return memo
    
    def generate_quick_summary(self, repo_data, scoring_result):
        """Generate a quick one-paragraph summary"""
        prompt = f"""Write a one-paragraph investment summary for:

Project: {repo_data.get('repo_name')}
Description: {repo_data.get('description')}
Score: {scoring_result['final_score']}/100
Stars: {repo_data.get('stars')}

Write a concise summary suitable for a dashboard or email."""
        
        return self.llm.generate(prompt, temperature=0.6)
