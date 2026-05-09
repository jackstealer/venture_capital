# PERSON 2: Text Preprocessing
# Prepares text for NLP analysis

import re
from textblob import TextBlob

class TextProcessor:
    """
    Text preprocessing for NLP analysis
    Cleans and prepares text for sentiment and trend analysis
    """
    
    def __init__(self):
        self.stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        ])
    
    def clean_text(self, text):
        """
        Clean and normalize text
        Args:
            text (str): Raw text
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def tokenize(self, text):
        """
        Tokenize text into words
        Args:
            text (str): Text to tokenize
        Returns:
            list: List of tokens
        """
        cleaned = self.clean_text(text)
        return cleaned.split()
    
    def remove_stop_words(self, tokens):
        """
        Remove common stop words
        Args:
            tokens (list): List of tokens
        Returns:
            list: Filtered tokens
        """
        return [token for token in tokens if token not in self.stop_words]
    
    def extract_keywords(self, text, top_n=10):
        """
        Extract important keywords from text
        Args:
            text (str): Text to analyze
            top_n (int): Number of keywords to extract
        Returns:
            list: Top keywords
        """
        # Tokenize and clean
        tokens = self.tokenize(text)
        tokens = self.remove_stop_words(tokens)
        
        # Count frequency
        freq = {}
        for token in tokens:
            if len(token) > 3:  # Only words longer than 3 chars
                freq[token] = freq.get(token, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return [keyword for keyword, count in sorted_keywords[:top_n]]
    
    def get_word_count(self, text):
        """Get word count of text"""
        return len(self.tokenize(text))
    
    def get_sentence_count(self, text):
        """Get sentence count of text"""
        blob = TextBlob(text)
        return len(blob.sentences)
    
    def summarize_text(self, text, max_sentences=3):
        """
        Create a simple extractive summary
        Args:
            text (str): Text to summarize
            max_sentences (int): Maximum sentences in summary
        Returns:
            str: Summary
        """
        blob = TextBlob(text)
        sentences = blob.sentences
        
        if len(sentences) <= max_sentences:
            return text
        
        # Return first N sentences
        summary_sentences = sentences[:max_sentences]
        return ' '.join([str(s) for s in summary_sentences])
    
    def preprocess_for_analysis(self, text):
        """
        Complete preprocessing pipeline
        Args:
            text (str): Raw text
        Returns:
            dict: Preprocessed data
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        keywords = self.extract_keywords(text)
        
        return {
            'original': text,
            'cleaned': cleaned,
            'tokens': tokens,
            'keywords': keywords,
            'word_count': len(tokens),
            'unique_words': len(set(tokens))
        }
