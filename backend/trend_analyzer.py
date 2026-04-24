# PERSON 2: AI-Based Trend Detection
# Detects trending technologies and market patterns

from datetime import datetime, timedelta
import re

class TrendAnalyzer:
    """
    AI-powered trend detection for technology projects
    Identifies emerging trends and market patterns
    """
    
    def __init__(self):
        # Define trending technology categories
        self.trending_categories = {
            'AI/ML': ['ai', 'machine learning', 'deep learning', 'neural', 'llm', 'gpt', 'transformer', 'diffusion'],
            'Web3': ['blockchain', 'crypto', 'web3', 'nft', 'defi', 'smart contract', 'ethereum'],
            'DevTools': ['developer tools', 'cli', 'sdk', 'api', 'framework', 'library'],
            'Cloud Native': ['kubernetes', 'docker', 'serverless', 'microservices', 'cloud'],
            'Data': ['data science', 'analytics', 'visualization', 'big data', 'etl'],
            'Security': ['security', 'encryption', 'authentication', 'cybersecurity'],
            'Frontend': ['react', 'vue', 'angular', 'ui', 'component', 'design system'],
            'Backend': ['api', 'server', 'database', 'backend', 'rest', 'graphql'],
            'Mobile': ['mobile', 'ios', 'android', 'react native', 'flutter'],
            'IoT': ['iot', 'embedded', 'hardware', 'sensor', 'raspberry pi']
        }
        
        # Hot keywords (currently trending)
        self.hot_keywords = [
            'ai', 'llm', 'gpt', 'chatbot', 'agent', 'automation',
            'rust', 'go', 'typescript', 'nextjs', 'tailwind'
        ]
    
    def analyze_trends(self, repo_data):
        """
        Analyze if repository aligns with current trends
        Args:
            repo_data (dict): Repository data
        Returns:
            dict: Trend analysis
        """
        description = repo_data.get('description', '') or ''
        description = description.lower()
        topics = [t.lower() for t in repo_data.get('topics', []) if t]
        language = (repo_data.get('primary_language', '') or '').lower()
        
        # Detect categories
        detected_categories = self._detect_categories(description, topics)
        
        # Calculate trend score
        trend_score = self._calculate_trend_score(repo_data, detected_categories)
        
        # Detect hot keywords
        hot_keywords_found = self._find_hot_keywords(description, topics)
        
        # Analyze growth velocity
        velocity = self._analyze_velocity(repo_data)
        
        # Market timing assessment
        timing = self._assess_market_timing(detected_categories, repo_data)
        
        return {
            'trend_score': trend_score,
            'trending_categories': detected_categories,
            'hot_keywords': hot_keywords_found,
            'growth_velocity': velocity,
            'market_timing': timing,
            'is_trending': trend_score > 60,
            'trend_strength': self._classify_trend_strength(trend_score)
        }
    
    def _detect_categories(self, description, topics):
        """Detect which trending categories the project belongs to"""
        detected = []
        
        combined_text = description + ' ' + ' '.join(topics)
        
        for category, keywords in self.trending_categories.items():
            for keyword in keywords:
                if keyword in combined_text:
                    if category not in detected:
                        detected.append(category)
                    break
        
        return detected
    
    def _find_hot_keywords(self, description, topics):
        """Find hot trending keywords in project"""
        found = []
        combined_text = description + ' ' + ' '.join(topics)
        
        for keyword in self.hot_keywords:
            if keyword in combined_text:
                found.append(keyword)
        
        return found
    
    def _calculate_trend_score(self, repo_data, categories):
        """
        Calculate overall trend score (0-100)
        Based on multiple factors
        """
        score = 0
        
        # Category alignment (30 points)
        if len(categories) > 0:
            score += min(30, len(categories) * 10)
        
        # Star velocity (30 points)
        age_days = repo_data.get('age_days', 1)
        stars = repo_data.get('stars', 0)
        if age_days > 0:
            stars_per_day = stars / age_days
            score += min(30, stars_per_day * 3)
        
        # Recent activity (20 points)
        activity_score = repo_data.get('activity_score', 0)
        score += (activity_score / 100) * 20
        
        # Hot keywords (20 points)
        description = repo_data.get('description', '') or ''
        description = description.lower()
        topics = [t.lower() for t in repo_data.get('topics', []) if t]
        hot_found = self._find_hot_keywords(description, topics)
        score += min(20, len(hot_found) * 5)
        
        return round(min(100, score), 2)
    
    def _analyze_velocity(self, repo_data):
        """
        Analyze growth velocity
        Returns: 'Rapid', 'Fast', 'Moderate', 'Slow'
        """
        age_days = repo_data.get('age_days', 1)
        stars = repo_data.get('stars', 0)
        
        if age_days == 0:
            age_days = 1
        
        stars_per_day = stars / age_days
        
        if stars_per_day > 10:
            return 'Rapid'
        elif stars_per_day > 5:
            return 'Fast'
        elif stars_per_day > 1:
            return 'Moderate'
        else:
            return 'Slow'
    
    def _assess_market_timing(self, categories, repo_data):
        """
        Assess if market timing is good
        Returns: 'Early', 'Peak', 'Late', 'Unknown'
        """
        age_days = repo_data.get('age_days', 0)
        stars = repo_data.get('stars', 0)
        
        # AI/ML is at peak
        if 'AI/ML' in categories:
            if age_days < 180:
                return 'Early'
            else:
                return 'Peak'
        
        # Web3 is late
        if 'Web3' in categories:
            return 'Late'
        
        # DevTools always relevant
        if 'DevTools' in categories:
            return 'Peak'
        
        # General assessment based on age and traction
        if age_days < 90 and stars > 100:
            return 'Early'
        elif age_days < 365 and stars > 1000:
            return 'Peak'
        elif age_days > 730:
            return 'Late'
        
        return 'Unknown'
    
    def _classify_trend_strength(self, score):
        """Classify trend strength based on score"""
        if score > 80:
            return 'Very Strong'
        elif score > 60:
            return 'Strong'
        elif score > 40:
            return 'Moderate'
        elif score > 20:
            return 'Weak'
        else:
            return 'Very Weak'
    
    def predict_future_trend(self, repo_data):
        """
        Predict if project will continue trending
        Args:
            repo_data (dict): Repository data
        Returns:
            dict: Prediction
        """
        trend_analysis = self.analyze_trends(repo_data)
        
        # Factors for prediction
        velocity = trend_analysis['growth_velocity']
        timing = trend_analysis['market_timing']
        categories = trend_analysis['trending_categories']
        
        # Prediction logic
        if velocity in ['Rapid', 'Fast'] and timing in ['Early', 'Peak']:
            prediction = 'Will Continue Trending'
            confidence = 85
        elif velocity == 'Moderate' and timing == 'Peak':
            prediction = 'Likely to Continue'
            confidence = 65
        elif timing == 'Late':
            prediction = 'Trend Declining'
            confidence = 70
        else:
            prediction = 'Uncertain'
            confidence = 40
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'reasoning': f"Based on {velocity} velocity and {timing} market timing",
            'recommended_action': self._recommend_action(prediction)
        }
    
    def _recommend_action(self, prediction):
        """Recommend investment action based on prediction"""
        if prediction == 'Will Continue Trending':
            return 'Strong Buy'
        elif prediction == 'Likely to Continue':
            return 'Buy'
        elif prediction == 'Trend Declining':
            return 'Pass'
        else:
            return 'Monitor'
