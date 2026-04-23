from llm_client import LLMClient
from prompts import PromptTemplates
import json

class AIAnalyzer:
     def __init__(self, provider='gemini'):
        self.llm = LLMClient(provider=provider)
        self.prompts = PromptTemplates()
    
    def analyze_repository(self, repo_data):
        print(f"🤖 AI analyzing repository: {repo_data.get('repo_name')}")
        
        # Generate prompt
        prompt = self.prompts.repository_analysis_prompt(repo_data)
        
        # Get AI analysis
        analysis = self.llm.generate_structured(prompt)
        
        # Add metadata
        analysis['analyzed_by'] = 'AI'
        analysis['model'] = 'gemini-pro'
        analysis['repo_name'] = repo_data.get('repo_name')
        
        return analysis
    
    def generate_investment_memo(self, analysis_data):
        print(f"📝 Generating investment memo...")
        
        prompt = self.prompts.investment_memo_prompt(analysis_data)
        memo_text = self.llm.generate(prompt, temperature=0.7)
        
        # Extract conviction score from memo
        conviction_score = self._extract_conviction_score(memo_text)
        
        return {
            'memo': memo_text,
            'conviction_score': conviction_score,
            'recommendation': self._extract_recommendation(memo_text)
        }
    
    def analyze_sentiment(self, text):
        prompt = self.prompts.sentiment_analysis_prompt(text)
        return self.llm.generate_structured(prompt)
    
    def detect_trends(self, repo_data, market_context="Current trends: AI/ML, Web3, DevTools, Cloud Native"):
        print(f"📊 Detecting trends...")
        
        prompt = self.prompts.trend_detection_prompt(repo_data, market_context)
        return self.llm.generate_structured(prompt)
    
    def assess_risks(self, repo_data):
        print(f"⚠️  Assessing risks...")
        
        prompt = self.prompts.risk_assessment_prompt(repo_data)
        return self.llm.generate_structured(prompt)
    
    def compare_projects(self, repo1_data, repo2_data):
        print(f"⚖️  Comparing projects...")
        
        prompt = self.prompts.competitive_analysis_prompt(repo1_data, repo2_data)
        return self.llm.generate_structured(prompt)
    
    def estimate_market_size(self, repo_data):
        prompt = self.prompts.market_sizing_prompt(repo_data)
        return self.llm.generate_structured(prompt)
    
    def analyze_code_quality(self, readme_content, language):
        prompt = self.prompts.code_quality_prompt(readme_content, language)
        return self.llm.generate_structured(prompt)
    
    def _extract_conviction_score(self, memo_text):
        """Extract conviction score from memo text"""
        try:
            # Look for conviction score in text
            if 'Conviction Score:' in memo_text:
                score_line = [line for line in memo_text.split('\n') if 'Conviction Score' in line][0]
                score = int(''.join(filter(str.isdigit, score_line)))
                return min(100, max(0, score))
        except:
            pass
        return 50  # Default
    
    def _extract_recommendation(self, memo_text):
        """Extract recommendation from memo text"""
        memo_lower = memo_text.lower()
        if 'strong buy' in memo_lower or 'highly recommend' in memo_lower:
            return 'Invest'
        elif 'pass' in memo_lower or 'do not invest' in memo_lower:
            return 'Pass'
        elif 'monitor' in memo_lower or 'watch' in memo_lower:
            return 'Monitor'
        return 'Monitor'  # Default
    
    def full_analysis(self, repo_data):
        print(f"\n🚀 Running full AI analysis for: {repo_data.get('repo_name')}\n")
        
        # 1. Repository Analysis
        repo_analysis = self.analyze_repository(repo_data)
        
        # 2. Sentiment Analysis
        sentiment = self.analyze_sentiment(repo_data.get('description', ''))
        
        # 3. Trend Detection
        trends = self.detect_trends(repo_data)
        
        # 4. Risk Assessment
        risks = self.assess_risks(repo_data)
        
        # 5. Market Sizing
        market = self.estimate_market_size(repo_data)
        
        # 6. Generate Investment Memo
        combined_data = {
            **repo_data,
            'technology_summary': repo_analysis.get('technology_summary'),
            'market_potential': market.get('market_size_score'),
            'team_strength': 'Unknown'  # Would need more data
        }
        memo = self.generate_investment_memo(combined_data)
        
        return {
            'repo_name': repo_data.get('repo_name'),
            'repo_url': repo_data.get('repo_url'),
            'repository_analysis': repo_analysis,
            'sentiment_analysis': sentiment,
            'trend_analysis': trends,
            'risk_assessment': risks,
            'market_analysis': market,
            'investment_memo': memo,
            'final_score': self._calculate_final_score(repo_analysis, trends, risks, market),
            'recommendation': memo.get('recommendation')
        }
    
    def _calculate_final_score(self, repo_analysis, trends, risks, market):
        """Calculate weighted final score"""
        try:
            innovation = repo_analysis.get('innovation_score', 50)
            trend_score = trends.get('trend_alignment', 50)
            risk_score = 100 - risks.get('risk_score', 50)  # Invert risk
            market_score = market.get('market_size_score', 50)
            
            # Weighted average
            final = (innovation * 0.3 + trend_score * 0.3 + risk_score * 0.2 + market_score * 0.2)
            return round(final, 2)
        except:
            return 50.0
