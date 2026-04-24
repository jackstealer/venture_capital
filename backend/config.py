import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    GROK_API_KEY = os.getenv('GROK_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # Optional, for higher rate limits
    
    # Database
    DATABASE_FILE = os.getenv('DATABASE_FILE', '../data/projects.json')
    MONGO_URI = os.getenv('MONGO_URI', '')
    
    # API Settings
    GITHUB_API_BASE = 'https://api.github.com'
    GITHUB_TRENDING_URL = 'https://api.github.com/search/repositories'
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Rate Limiting
    GITHUB_RATE_LIMIT = 60  # requests per hour without token
    GITHUB_RATE_LIMIT_WITH_TOKEN = 5000  # requests per hour with token
    
    # Analysis Settings
    DEFAULT_TRENDING_LIMIT = 10
    MAX_TRENDING_LIMIT = 50
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.GEMINI_API_KEY:
            print("⚠️  Warning: GEMINI_API_KEY not set. AI analysis will not work.")
            print("   Get your free API key from: https://makersuite.google.com/app/apikey")
        
        if not Config.GITHUB_TOKEN:
            print("ℹ️  Info: GITHUB_TOKEN not set. Using lower rate limits.")
            print("   Generate token at: https://github.com/settings/tokens")
        
        if not Config.MONGO_URI:
            print("⚠️  Warning: MONGO_URI not set. Database writes will fail unless local JSON file is used or env var provided.")
            print("   Add MONGO_URI to backend/.env or your environment variables.")
        
        return True

# Validate configuration on import
Config.validate()
