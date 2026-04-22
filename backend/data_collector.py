# PERSON 2: Data Collection & Processing
# Main module for fetching and processing GitHub data

from github_api import GitHubAPI
from data_processor import DataProcessor
from datetime import datetime, timedelta

class DataCollector:
    """Collects and processes data from GitHub"""
    
    def __init__(self):
        self.github = GitHubAPI()
        self.processor = DataProcessor()
    
    def fetch_trending_repos(self, limit=10):
        """
        Fetch trending repositories from GitHub
        Args:
            limit (int): Number of repositories to fetch
        Returns:
            list: Processed repository data
        """
        print(f"📡 Fetching top {limit} trending repositories...")
        
        # Fetch raw data from GitHub
        raw_repos = self.github.get_trending_repos(limit)
        
        # Process and clean the data
        processed_repos = []
        for repo in raw_repos:
            processed = self.processor.process_repo_data(repo)
            processed_repos.append(processed)
        
        print(f"✅ Successfully fetched {len(processed_repos)} repositories")
        return processed_repos
    
    def fetch_repo_details(self, repo_url):
        """
        Fetch detailed information about a specific repository
        Args:
            repo_url (str): GitHub repository URL or owner/repo format
        Returns:
            dict: Detailed repository information
        """
        print(f"🔍 Fetching details for: {repo_url}")
        
        # Extract owner and repo name from URL
        owner, repo_name = self._parse_repo_url(repo_url)
        
        # Fetch repository details
        repo_data = self.github.get_repo_details(owner, repo_name)
        
        # Fetch additional metrics
        languages = self.github.get_repo_languages(owner, repo_name)
        contributors = self.github.get_repo_contributors(owner, repo_name)
        
        # Combine all data
        repo_data['languages'] = languages
        repo_data['top_contributors'] = contributors[:5]  # Top 5 contributors
        
        # Process the combined data
        processed = self.processor.process_repo_data(repo_data)
        
        print(f"✅ Successfully fetched details for {owner}/{repo_name}")
        return processed
    
    def _parse_repo_url(self, repo_url):
        """
        Parse GitHub URL to extract owner and repo name
        Args:
            repo_url (str): URL like 'https://github.com/owner/repo' or 'owner/repo'
        Returns:
            tuple: (owner, repo_name)
        """
        # Remove https://github.com/ if present
        repo_url = repo_url.replace('https://github.com/', '')
        repo_url = repo_url.replace('http://github.com/', '')
        
        # Split by /
        parts = repo_url.strip('/').split('/')
        
        if len(parts) >= 2:
            return parts[0], parts[1]
        else:
            raise ValueError(f"Invalid repository URL: {repo_url}")
    
    def get_trending_by_language(self, language, limit=10):
        """
        Fetch trending repositories for a specific programming language
        Args:
            language (str): Programming language (e.g., 'python', 'javascript')
            limit (int): Number of repositories
        Returns:
            list: Trending repositories for that language
        """
        print(f"📡 Fetching trending {language} repositories...")
        
        raw_repos = self.github.get_trending_repos(limit, language=language)
        processed_repos = [self.processor.process_repo_data(repo) for repo in raw_repos]
        
        return processed_repos
    
    def get_recently_updated_repos(self, days=7, limit=10):
        """
        Fetch repositories with recent activity
        Args:
            days (int): Number of days to look back
            limit (int): Number of repositories
        Returns:
            list: Recently updated repositories
        """
        date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        raw_repos = self.github.get_trending_repos(
            limit, 
            sort='updated',
            since=date_threshold
        )
        
        processed_repos = [self.processor.process_repo_data(repo) for repo in raw_repos]
        return processed_repos
