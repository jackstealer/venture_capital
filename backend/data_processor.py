# PERSON 2: Data Processing
# Cleans and structures raw GitHub data

from datetime import datetime

class DataProcessor:
    """Processes and cleans raw repository data"""
    
    def process_repo_data(self, raw_repo):
        """
        Transform raw GitHub API response into clean structured data
        Args:
            raw_repo (dict): Raw repository data from GitHub API
        Returns:
            dict: Cleaned and structured repository data
        """
        return {
            'id': raw_repo.get('id'),
            'repo_name': raw_repo.get('name', ''),
            'full_name': raw_repo.get('full_name', ''),
            'repo_url': raw_repo.get('html_url', ''),
            'description': raw_repo.get('description', ''),
            
            # Metrics
            'stars': raw_repo.get('stargazers_count', 0),
            'forks': raw_repo.get('forks_count', 0),
            'watchers': raw_repo.get('watchers_count', 0),
            'open_issues': raw_repo.get('open_issues_count', 0),
            
            # Language and topics
            'primary_language': raw_repo.get('language', 'Unknown'),
            'topics': raw_repo.get('topics', []),
            'languages': raw_repo.get('languages', {}),
            
            # Dates
            'created_at': raw_repo.get('created_at', ''),
            'updated_at': raw_repo.get('updated_at', ''),
            'pushed_at': raw_repo.get('pushed_at', ''),
            
            # Owner info
            'owner': {
                'login': raw_repo.get('owner', {}).get('login', ''),
                'avatar_url': raw_repo.get('owner', {}).get('avatar_url', ''),
                'type': raw_repo.get('owner', {}).get('type', '')
            },
            
            # Additional metrics
            'size': raw_repo.get('size', 0),
            'default_branch': raw_repo.get('default_branch', 'main'),
            'has_wiki': raw_repo.get('has_wiki', False),
            'has_issues': raw_repo.get('has_issues', False),
            'license': self._extract_license(raw_repo.get('license')),
            
            # Contributors (if available)
            'top_contributors': raw_repo.get('top_contributors', []),
            
            # Calculated fields
            'age_days': self._calculate_age(raw_repo.get('created_at')),
            'activity_score': self._calculate_activity_score(raw_repo),
            
            # Timestamp
            'fetched_at': datetime.now().isoformat()
        }
    
    def _extract_license(self, license_data):
        """Extract license information"""
        if not license_data:
            return 'No License'
        return license_data.get('name', 'Unknown')
    
    def _calculate_age(self, created_at):
        """Calculate repository age in days"""
        if not created_at:
            return 0
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = (datetime.now(created.tzinfo) - created).days
            return age
        except:
            return 0
    
    def _calculate_activity_score(self, repo):
        """
        Calculate a simple activity score based on recent updates
        Higher score = more active
        """
        try:
            # Get days since last push
            pushed_at = repo.get('pushed_at', '')
            if pushed_at:
                last_push = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                days_since_push = (datetime.now(last_push.tzinfo) - last_push).days
                
                # Score: 100 if pushed today, decreases over time
                activity_score = max(0, 100 - days_since_push)
                return activity_score
            return 0
        except:
            return 0
    
    def calculate_growth_metrics(self, repo_data):
        """
        Calculate growth and momentum metrics
        Args:
            repo_data (dict): Processed repository data
        Returns:
            dict: Growth metrics
        """
        age_days = repo_data.get('age_days', 1)
        stars = repo_data.get('stars', 0)
        forks = repo_data.get('forks', 0)
        
        # Avoid division by zero
        if age_days == 0:
            age_days = 1
        
        return {
            'stars_per_day': round(stars / age_days, 2),
            'forks_per_day': round(forks / age_days, 2),
            'star_to_fork_ratio': round(stars / forks, 2) if forks > 0 else stars,
            'momentum_score': self._calculate_momentum(repo_data)
        }
    
    def _calculate_momentum(self, repo_data):
        """
        Calculate momentum score (0-100)
        Based on stars, activity, and recency
        """
        stars = repo_data.get('stars', 0)
        activity = repo_data.get('activity_score', 0)
        age_days = repo_data.get('age_days', 1)
        
        # Normalize components
        star_score = min(100, (stars / 100) * 10)  # 1000 stars = 100 points
        activity_score = activity  # Already 0-100
        recency_score = max(0, 100 - (age_days / 365) * 50)  # Newer = higher
        
        # Weighted average
        momentum = (star_score * 0.5 + activity_score * 0.3 + recency_score * 0.2)
        return round(momentum, 2)
