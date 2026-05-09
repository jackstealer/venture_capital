# PERSON 3: Smart Scoring Engine
# Multi-factor scoring algorithm for investment decisions

class ScoringEngine:
    """
    AI-powered scoring engine for repository evaluation
    Combines multiple factors into a final investment score
    """
    
    def __init__(self):
        # Define scoring weights
        self.weights = {
            'traction': 0.25,        # Stars, forks, community
            'technology': 0.20,      # Tech quality, innovation
            'market': 0.20,          # Market size, timing
            'trend': 0.15,           # Trend alignment
            'sentiment': 0.10,       # Community sentiment
            'risk': 0.10             # Risk assessment (inverted)
        }
    
    def calculate_score(self, repo_data, ai_analysis=None, trend_analysis=None, sentiment_analysis=None):
        """
        Calculate comprehensive investment score
        Args:
            repo_data (dict): Repository metrics
            ai_analysis (dict): AI analysis results
            trend_analysis (dict): Trend analysis
            sentiment_analysis (dict): Sentiment analysis
        Returns:
            dict: Scoring breakdown and final score
        """
        # Calculate individual scores
        traction_score = self._calculate_traction_score(repo_data)
        technology_score = self._calculate_technology_score(repo_data, ai_analysis)
        market_score = self._calculate_market_score(repo_data, ai_analysis)
        trend_score = self._calculate_trend_score(trend_analysis)
        sentiment_score = self._calculate_sentiment_score(sentiment_analysis)
        risk_score = self._calculate_risk_score(repo_data, ai_analysis)
        
        # Calculate weighted final score
        final_score = (
            traction_score * self.weights['traction'] +
            technology_score * self.weights['technology'] +
            market_score * self.weights['market'] +
            trend_score * self.weights['trend'] +
            sentiment_score * self.weights['sentiment'] +
            risk_score * self.weights['risk']
        )
        
        return {
            'final_score': round(final_score, 2),
            'breakdown': {
                'traction': round(traction_score, 2),
                'technology': round(technology_score, 2),
                'market': round(market_score, 2),
                'trend': round(trend_score, 2),
                'sentiment': round(sentiment_score, 2),
                'risk': round(risk_score, 2)
            },
            'grade': self._score_to_grade(final_score),
            'recommendation': self._score_to_recommendation(final_score)
        }
    
    def _calculate_traction_score(self, repo_data):
        """Calculate traction score based on GitHub metrics"""
        stars = repo_data.get('stars', 0)
        forks = repo_data.get('forks', 0)
        watchers = repo_data.get('watchers', 0)
        age_days = repo_data.get('age_days', 1)
        
        # Normalize metrics
        star_score = min(100, (stars / 1000) * 50)
        fork_score = min(100, (forks / 200) * 30)
        watcher_score = min(100, (watchers / 100) * 20)
        
        # Consider velocity
        if age_days > 0:
            velocity_bonus = min(20, (stars / age_days) * 2)
        else:
            velocity_bonus = 0
        
        total = star_score + fork_score + watcher_score + velocity_bonus
        return min(100, total)
    
    def _calculate_technology_score(self, repo_data, ai_analysis):
        """Calculate technology quality score"""
        if ai_analysis and 'innovation_score' in ai_analysis:
            return ai_analysis['innovation_score']
        
        # Fallback: basic assessment
        language = repo_data.get('primary_language', '')
        topics = repo_data.get('topics', [])
        
        score = 50  # Base score
        
        # Modern languages bonus
        modern_languages = ['Python', 'TypeScript', 'Rust', 'Go', 'Swift']
        if language in modern_languages:
            score += 15
        
        # Topic diversity bonus
        score += min(20, len(topics) * 3)
        
        # Has documentation
        if repo_data.get('has_wiki'):
            score += 10
        
        return min(100, score)
    
    def _calculate_market_score(self, repo_data, ai_analysis):
        """Calculate market potential score"""
        if ai_analysis and 'market_analysis' in ai_analysis:
            return ai_analysis['market_analysis'].get('market_size_score', 50)
        
        # Fallback: estimate from topics
        topics = repo_data.get('topics', [])
        description = repo_data.get('description', '') or ''
        description = description.lower()
        
        # Large market keywords
        large_market_keywords = ['ai', 'cloud', 'data', 'security', 'mobile', 'web']
        market_indicators = sum(1 for kw in large_market_keywords if kw in description or kw in ' '.join(topics).lower())
        
        score = 40 + (market_indicators * 10)
        return min(100, score)
    
    def _calculate_trend_score(self, trend_analysis):
        """Calculate trend alignment score"""
        if trend_analysis:
            return trend_analysis.get('trend_score', 50)
        return 50
    
    def _calculate_sentiment_score(self, sentiment_analysis):
        """Calculate sentiment score"""
        if sentiment_analysis:
            return sentiment_analysis.get('sentiment_score', 50)
        return 50
    
    def _calculate_risk_score(self, repo_data, ai_analysis):
        """Calculate risk score (higher is better - lower risk)"""
        if ai_analysis and 'risk_assessment' in ai_analysis:
            risk_level = ai_analysis['risk_assessment'].get('risk_score', 50)
            return 100 - risk_level  # Invert: low risk = high score
        
        # Fallback: basic risk assessment
        score = 70  # Base score (moderate risk)
        
        # Age factor (very new or very old = higher risk)
        age_days = repo_data.get('age_days', 0)
        if age_days < 30:
            score -= 20  # Too new
        elif age_days > 1825:  # 5 years
            score -= 15  # Possibly outdated
        
        # Activity factor
        activity = repo_data.get('activity_score', 0)
        if activity < 20:
            score -= 15  # Low activity = higher risk
        
        # License factor
        license_name = repo_data.get('license', '')
        if license_name == 'No License':
            score -= 10
        
        return max(0, min(100, score))
    
    def _score_to_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        else:
            return 'D'
    
    def _score_to_recommendation(self, score):
        """Convert score to investment recommendation"""
        if score >= 80:
            return 'Strong Invest'
        elif score >= 65:
            return 'Invest'
        elif score >= 50:
            return 'Monitor'
        else:
            return 'Pass'
    
    def compare_scores(self, score1, score2):
        """
        Compare two project scores
        Args:
            score1 (dict): First project score
            score2 (dict): Second project score
        Returns:
            dict: Comparison results
        """
        diff = score1['final_score'] - score2['final_score']
        
        if abs(diff) < 5:
            winner = 'Tie'
            margin = 'Very Close'
        elif diff > 0:
            winner = 'Project 1'
            margin = 'Significant' if abs(diff) > 15 else 'Moderate'
        else:
            winner = 'Project 2'
            margin = 'Significant' if abs(diff) > 15 else 'Moderate'
        
        return {
            'winner': winner,
            'score_difference': round(abs(diff), 2),
            'margin': margin,
            'project1_score': score1['final_score'],
            'project2_score': score2['final_score']
        }
    
    def generate_score_explanation(self, scoring_result):
        """
        Generate human-readable explanation of score
        Args:
            scoring_result (dict): Scoring results
        Returns:
            str: Explanation
        """
        score = scoring_result['final_score']
        breakdown = scoring_result['breakdown']
        
        # Find strongest and weakest factors
        sorted_factors = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        strongest = sorted_factors[0]
        weakest = sorted_factors[-1]
        
        explanation = f"""
Investment Score: {score}/100 (Grade: {scoring_result['grade']})

Recommendation: {scoring_result['recommendation']}

Key Strengths:
- {strongest[0].title()}: {strongest[1]}/100 (Excellent performance)

Areas of Concern:
- {weakest[0].title()}: {weakest[1]}/100 (Needs improvement)

Score Breakdown:
"""
        for factor, value in breakdown.items():
            explanation += f"- {factor.title()}: {value}/100\n"
        
        return explanation
