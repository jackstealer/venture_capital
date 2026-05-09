import requests
from datetime import datetime, timedelta
from config import Config

class GitHubAPI:    
    def __init__(self):
        self.base_url = Config.GITHUB_API_BASE
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Add token if available for higher rate limits
        if Config.GITHUB_TOKEN:
            self.headers['Authorization'] = f'token {Config.GITHUB_TOKEN}'
    
    def get_trending_repos(self, limit=10, language=None, sort='stars', since=None):
        # Build query
        query_parts = []
        
        # Date filter for trending (last 7 days by default)
        if not since:
            since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        query_parts.append(f'created:>{since}')
        
        # Language filter
        if language:
            query_parts.append(f'language:{language}')
        
        # Combine query
        query = ' '.join(query_parts)
        
        # API endpoint
        url = f'{self.base_url}/search/repositories'
        params = {
            'q': query,
            'sort': sort,
            'order': 'desc',
            'per_page': limit
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trending repos: {e}")
            return []
    
    def get_repo_details(self, owner, repo_name):
        url = f'{self.base_url}/repos/{owner}/{repo_name}'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repo details: {e}")
            return {}
    
    def get_repo_languages(self, owner, repo_name):
        """Get programming languages used in repository"""
        url = f'{self.base_url}/repos/{owner}/{repo_name}/languages'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except:
            return {}
    
    def get_repo_contributors(self, owner, repo_name, limit=5):
        """Get top contributors to repository"""
        url = f'{self.base_url}/repos/{owner}/{repo_name}/contributors'
        params = {'per_page': limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except:
            return []
    
    def get_repo_readme(self, owner, repo_name):
        """Fetch repository README content"""
        url = f'{self.base_url}/repos/{owner}/{repo_name}/readme'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            readme_data = response.json()
            
            # Get the actual content
            content_url = readme_data.get('download_url')
            if content_url:
                content_response = requests.get(content_url)
                return content_response.text
            return ""
        except:
            return ""
