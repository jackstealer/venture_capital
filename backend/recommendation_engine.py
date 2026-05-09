# PERSON 3: AI Recommendation Engine
# Generates intelligent investment recommendations

from scoring_engine import ScoringEngine

class RecommendationEngine:
    """
    AI-powered recommendation system for investment decisions
    Combines scoring, analysis, and business logic
    """
    
    def __init__(self):
        self.scoring_engine = ScoringEngine()
    
    def generate_recommendation(self, repo_data, ai_analysis=None, trend_analysis=None, sentiment_analysis=None):
        """
        Generate comprehensive investment recommendation
        Args:
            repo_data (dict): Repository data
            ai_analysis (dict): AI analysis results
            trend_analysis (dict): Trend analysis
            sentiment_analysis (dict): Sentiment analysis
        Returns:
            dict: Complete recommendation
        """
        # Calculate scores
        scoring_result = self.scoring_engine.calculate_score(
            repo_data, ai_analysis, trend_analysis, sentiment_analysis
        )
        
        # Generate recommendation details
        recommendation = {
            'repo_name': repo_data.get('repo_name'),
            'repo_url': repo_data.get('repo_url'),
            'final_score': scoring_result['final_score'],
            'grade': scoring_result['grade'],
            'recommendation': scoring_result['recommendation'],
            'score_breakdown': scoring_result['breakdown'],
            'key_insights': self._generate_insights(repo_data, scoring_result, ai_analysis, trend_analysis),
            'investment_thesis': self._generate_thesis(repo_data, scoring_result),
            'risks': self._identify_risks(repo_data, ai_analysis),
            'opportunities': self._identify_opportunities(repo_data, trend_analysis),
            'next_steps': self._suggest_next_steps(scoring_result['recommendation'])
        }
        
        return recommendation
    
    def _generate_insights(self, repo_data, scoring_result, ai_analysis, trend_analysis):
        """Generate key insights from analysis"""
        insights = []
        
        # Traction insight
        stars = repo_data.get('stars', 0)
        if stars > 10000:
            insights.append(f"Strong community traction with {stars:,} stars")
        elif stars > 1000:
            insights.append(f"Growing community with {stars:,} stars")
        
        # Technology insight
        if ai_analysis and ai_analysis.get('innovation_score', 0) > 75:
            insights.append("Highly innovative technology approach")
        
        # Trend insight
        if trend_analysis and trend_analysis.get('is_trending'):
            insights.append(f"Aligns with trending categories: {', '.join(trend_analysis.get('trending_categories', []))}")
        
        # Activity insight
        activity = repo_data.get('activity_score', 0)
        if activity > 80:
            insights.append("Very active development (recently updated)")
        elif activity < 30:
            insights.append("⚠️ Low recent activity - potential concern")
        
        # Age insight
        age_days = repo_data.get('age_days', 0)
        if age_days < 90:
            insights.append("Early-stage project - high risk, high potential")
        elif age_days > 730:
            insights.append("Mature project with established track record")
        
        return insights
    
    def _generate_thesis(self, repo_data, scoring_result):
        """Generate investment thesis"""
        score = scoring_result['final_score']
        recommendation = scoring_result['recommendation']
        
        if score >= 80:
            thesis = f"Strong investment opportunity. {repo_data.get('repo_name')} demonstrates excellent metrics across all key factors. "
            thesis += "The project shows strong community traction, innovative technology, and alignment with market trends. "
            thesis += "Recommended for immediate investment consideration."
        
        elif score >= 65:
            thesis = f"Promising investment opportunity. {repo_data.get('repo_name')} shows solid performance in most areas. "
            thesis += "While there are some areas for improvement, the overall trajectory is positive. "
            thesis += "Recommended for investment with standard due diligence."
        
        elif score >= 50:
            thesis = f"Moderate opportunity requiring monitoring. {repo_data.get('repo_name')} has potential but shows mixed signals. "
            thesis += "Recommend continued observation before making investment decision. "
            thesis += "Consider revisiting in 3-6 months to assess progress."
        
        else:
            thesis = f"Not recommended for investment at this time. {repo_data.get('repo_name')} shows concerning signals in key areas. "
            thesis += "Significant risks outweigh potential returns. "
            thesis += "Pass on this opportunity and focus resources elsewhere."
        
        return thesis
    
    def _identify_risks(self, repo_data, ai_analysis):
        """Identify key investment risks"""
        risks = []
        
        # Age risk
        age_days = repo_data.get('age_days', 0)
        if age_days < 30:
            risks.append({
                'type': 'Execution Risk',
                'severity': 'High',
                'description': 'Very new project - unproven track record'
            })
        
        # Activity risk
        activity = repo_data.get('activity_score', 0)
        if activity < 30:
            risks.append({
                'type': 'Abandonment Risk',
                'severity': 'Medium',
                'description': 'Low recent activity - project may be abandoned'
            })
        
        # License risk
        if repo_data.get('license') == 'No License':
            risks.append({
                'type': 'Legal Risk',
                'severity': 'Medium',
                'description': 'No license specified - unclear usage rights'
            })
        
        # Competition risk
        stars = repo_data.get('stars', 0)
        if stars < 100:
            risks.append({
                'type': 'Market Risk',
                'severity': 'Medium',
                'description': 'Limited traction - may face strong competition'
            })
        
        # AI-identified risks
        if ai_analysis and 'risk_assessment' in ai_analysis:
            ai_risks = ai_analysis['risk_assessment'].get('technical_risks', [])
            for risk in ai_risks[:2]:  # Top 2 AI risks
                risks.append({
                    'type': 'Technical Risk',
                    'severity': 'Medium',
                    'description': risk
                })
        
        return risks
    
    def _identify_opportunities(self, repo_data, trend_analysis):
        """Identify key opportunities"""
        opportunities = []
        
        # Trend opportunity
        if trend_analysis and trend_analysis.get('is_trending'):
            opportunities.append({
                'type': 'Market Timing',
                'potential': 'High',
                'description': 'Project aligns with current market trends'
            })
        
        # Growth opportunity
        age_days = repo_data.get('age_days', 1)
        stars = repo_data.get('stars', 0)
        if age_days > 0:
            velocity = stars / age_days
            if velocity > 5:
                opportunities.append({
                    'type': 'Rapid Growth',
                    'potential': 'High',
                    'description': f'High star velocity ({velocity:.1f} stars/day)'
                })
        
        # Community opportunity
        forks = repo_data.get('forks', 0)
        if forks > 100:
            opportunities.append({
                'type': 'Community Engagement',
                'potential': 'Medium',
                'description': f'Strong community with {forks} forks'
            })
        
        # Technology opportunity
        topics = repo_data.get('topics', [])
        hot_topics = ['ai', 'machine-learning', 'blockchain', 'cloud']
        matching_topics = [t for t in topics if any(ht in t.lower() for ht in hot_topics)]
        if matching_topics:
            opportunities.append({
                'type': 'Technology Trend',
                'potential': 'High',
                'description': f'Leverages hot technologies: {", ".join(matching_topics)}'
            })
        
        return opportunities
    
    def _suggest_next_steps(self, recommendation):
        """Suggest next steps based on recommendation"""
        if recommendation == 'Strong Invest':
            return [
                'Schedule deep-dive technical review',
                'Initiate founder/maintainer conversations',
                'Prepare term sheet',
                'Conduct competitive analysis',
                'Set up monitoring dashboard'
            ]
        
        elif recommendation == 'Invest':
            return [
                'Conduct additional due diligence',
                'Review code quality in detail',
                'Assess team/maintainer background',
                'Evaluate competitive positioning',
                'Monitor for 2-4 weeks before decision'
            ]
        
        elif recommendation == 'Monitor':
            return [
                'Add to watchlist',
                'Set up automated monitoring',
                'Review again in 3 months',
                'Track star growth and activity',
                'Monitor for major updates or releases'
            ]
        
        else:  # Pass
            return [
                'Archive analysis',
                'Focus resources on higher-scoring opportunities',
                'Optional: Set alert for significant changes',
                'Document reasons for passing'
            ]
    
    def compare_projects(self, project1_data, project2_data):
        """
        Compare two projects and recommend which to invest in
        Args:
            project1_data (dict): First project recommendation
            project2_data (dict): Second project recommendation
        Returns:
            dict: Comparison and recommendation
        """
        score1 = project1_data['final_score']
        score2 = project2_data['final_score']
        
        comparison = self.scoring_engine.compare_scores(
            {'final_score': score1},
            {'final_score': score2}
        )
        
        # Detailed comparison
        winner_name = project1_data['repo_name'] if comparison['winner'] == 'Project 1' else project2_data['repo_name']
        
        return {
            'winner': winner_name,
            'comparison': comparison,
            'recommendation': f"Invest in {winner_name}" if comparison['winner'] != 'Tie' else "Both projects are equally viable",
            'reasoning': self._generate_comparison_reasoning(project1_data, project2_data, comparison)
        }
    
    def _generate_comparison_reasoning(self, proj1, proj2, comparison):
        """Generate reasoning for comparison"""
        if comparison['winner'] == 'Tie':
            return "Both projects score similarly across all factors. Consider other qualitative factors or invest in both."
        
        winner = proj1 if comparison['winner'] == 'Project 1' else proj2
        loser = proj2 if comparison['winner'] == 'Project 1' else proj1
        
        reasoning = f"{winner['repo_name']} outperforms {loser['repo_name']} with a {comparison['score_difference']} point advantage. "
        
        # Find key differentiators
        winner_breakdown = winner['score_breakdown']
        loser_breakdown = loser['score_breakdown']
        
        max_diff = 0
        max_diff_factor = ''
        for factor in winner_breakdown:
            diff = winner_breakdown[factor] - loser_breakdown[factor]
            if abs(diff) > max_diff:
                max_diff = abs(diff)
                max_diff_factor = factor
        
        reasoning += f"The key differentiator is {max_diff_factor} where {winner['repo_name']} scores {winner_breakdown[max_diff_factor]:.1f} vs {loser_breakdown[max_diff_factor]:.1f}."
        
        return reasoning
