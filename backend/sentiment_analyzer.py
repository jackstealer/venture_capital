# PERSON 2: Sentiment Analysis using NLP
# Analyzes sentiment of project descriptions and README content

from textblob import TextBlob
import re

class SentimentAnalyzer:
    """
    NLP-based sentiment analysis for repository content
    Uses TextBlob for sentiment scoring
    """
    
    def __init__(self):
        self.positive_keywords = [
            'innovative', 'powerful', 'efficient', 'scalable', 'modern',
            'fast', 'easy', 'simple', 'robust', 'reliable', 'secure',
            'revolutionary', 'cutting-edge', 'advanced', 'optimized'
        ]
        
        self.negative_keywords = [
            'deprecated', 'legacy', 'slow', 'complex', 'difficult',
            'unstable', 'buggy', 'outdated', 'limited', 'experimental'
        ]
    
    def analyze_text(self, text):
        """
        Perform sentiment analysis on text
        Args:
            text (str): Text to analyze
        Returns:
            dict: Sentiment analysis results
        """
        if not text:
            return self._default_sentiment()
        
        # Create TextBlob object
        blob = TextBlob(text)
        
        # Get polarity (-1 to 1) and subjectivity (0 to 1)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment = 'Positive'
        elif polarity < -0.1:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        # Calculate confidence (0-100)
        confidence = abs(polarity) * 100
        
        # Detect keywords
        positive_count = self._count_keywords(text, self.positive_keywords)
        negative_count = self._count_keywords(text, self.negative_keywords)
        
        # Calculate enthusiasm level
        enthusiasm = self._calculate_enthusiasm(text, polarity, positive_count)
        
        return {
            'sentiment': sentiment,
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3),
            'confidence': round(confidence, 2),
            'enthusiasm_level': enthusiasm,
            'positive_keywords_found': positive_count,
            'negative_keywords_found': negative_count,
            'word_count': len(text.split()),
            'sentence_count': len(blob.sentences)
        }
    
    def analyze_repository(self, repo_data):
        """
        Analyze sentiment of repository description and README
        Args:
            repo_data (dict): Repository data
        Returns:
            dict: Comprehensive sentiment analysis
        """
        description = repo_data.get('description', '')
        readme = repo_data.get('readme', '')
        
        # Analyze description
        desc_sentiment = self.analyze_text(description)
        
        # Analyze README (first 1000 chars)
        readme_sentiment = self.analyze_text(readme[:1000])
        
        # Combined analysis
        combined_polarity = (desc_sentiment['polarity'] + readme_sentiment['polarity']) / 2
        
        return {
            'description_sentiment': desc_sentiment,
            'readme_sentiment': readme_sentiment,
            'overall_sentiment': 'Positive' if combined_polarity > 0.1 else 'Negative' if combined_polarity < -0.1 else 'Neutral',
            'overall_polarity': round(combined_polarity, 3),
            'sentiment_score': self._polarity_to_score(combined_polarity)
        }
    
    def _count_keywords(self, text, keywords):
        """Count occurrences of keywords in text"""
        text_lower = text.lower()
        count = sum(1 for keyword in keywords if keyword in text_lower)
        return count
    
    def _calculate_enthusiasm(self, text, polarity, positive_count):
        """
        Calculate enthusiasm level (0-100)
        Based on polarity, exclamation marks, and positive keywords
        """
        # Count exclamation marks
        exclamations = text.count('!')
        
        # Base enthusiasm from polarity
        base_enthusiasm = (polarity + 1) * 50  # Convert -1,1 to 0,100
        
        # Boost from positive keywords
        keyword_boost = min(30, positive_count * 5)
        
        # Boost from exclamations
        exclamation_boost = min(20, exclamations * 5)
        
        enthusiasm = base_enthusiasm + keyword_boost + exclamation_boost
        return round(min(100, enthusiasm), 2)
    
    def _polarity_to_score(self, polarity):
        """Convert polarity (-1 to 1) to score (0 to 100)"""
        return round((polarity + 1) * 50, 2)
    
    def _default_sentiment(self):
        """Return default sentiment when no text available"""
        return {
            'sentiment': 'Neutral',
            'polarity': 0.0,
            'subjectivity': 0.0,
            'confidence': 0.0,
            'enthusiasm_level': 50.0,
            'positive_keywords_found': 0,
            'negative_keywords_found': 0,
            'word_count': 0,
            'sentence_count': 0
        }
    
    def extract_key_phrases(self, text, top_n=5):
        """
        Extract key phrases from text
        Args:
            text (str): Text to analyze
            top_n (int): Number of phrases to extract
        Returns:
            list: Key phrases
        """
        blob = TextBlob(text)
        
        # Get noun phrases
        phrases = blob.noun_phrases
        
        # Count frequency
        phrase_freq = {}
        for phrase in phrases:
            phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1
        
        # Sort by frequency
        sorted_phrases = sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N
        return [phrase for phrase, freq in sorted_phrases[:top_n]]
    
    def analyze_community_engagement(self, repo_data):
        """
        Analyze community engagement based on metrics
        Args:
            repo_data (dict): Repository data
        Returns:
            dict: Engagement analysis
        """
        stars = repo_data.get('stars', 0)
        forks = repo_data.get('forks', 0)
        watchers = repo_data.get('watchers', 0)
        issues = repo_data.get('open_issues', 0)
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(stars, forks, watchers, issues)
        
        # Classify engagement level
        if engagement_score > 75:
            level = 'Very High'
        elif engagement_score > 50:
            level = 'High'
        elif engagement_score > 25:
            level = 'Medium'
        else:
            level = 'Low'
        
        return {
            'engagement_level': level,
            'engagement_score': engagement_score,
            'stars': stars,
            'forks': forks,
            'watchers': watchers,
            'open_issues': issues,
            'community_sentiment': 'Positive' if engagement_score > 60 else 'Neutral' if engagement_score > 30 else 'Negative'
        }
    
    def _calculate_engagement_score(self, stars, forks, watchers, issues):
        """Calculate engagement score (0-100)"""
        # Normalize metrics
        star_score = min(100, (stars / 1000) * 50)
        fork_score = min(100, (forks / 200) * 30)
        watcher_score = min(100, (watchers / 100) * 10)
        issue_score = min(100, (issues / 50) * 10)
        
        total = star_score + fork_score + watcher_score + issue_score
        return round(total, 2)
