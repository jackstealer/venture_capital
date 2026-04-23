import json
import os
from datetime import datetime

class Database:  
    def __init__(self, db_file='../data/projects.json'):
        self.db_file = db_file
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump([], f)
    
    def save_project(self, project_data):
        try:
            projects = self._read_db()
            
            # Add timestamp
            project_data['updated_at'] = datetime.now().isoformat()
            
            # Check if project already exists (by repo_id or url)
            project_id = project_data.get('id') or project_data.get('repo_url')
            existing_index = None
            
            for i, proj in enumerate(projects):
                if proj.get('id') == project_id or proj.get('repo_url') == project_id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # Update existing project
                projects[existing_index] = project_data
            else:
                # Add new project
                projects.append(project_data)
            
            self._write_db(projects)
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    def get_project(self, project_id):
        projects = self._read_db()
        for project in projects:
            if str(project.get('id')) == str(project_id):
                return project
        return None
    
    def get_all_projects(self):
        return self._read_db()
    
    def delete_project(self, project_id):
        """Delete a project by ID"""
        projects = self._read_db()
        projects = [p for p in projects if str(p.get('id')) != str(project_id)]
        self._write_db(projects)
        return True
    
    def _read_db(self):
        """Read data from JSON file"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _write_db(self, data):
        """Write data to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)

from pymongo import MongoClient
import os
from config import Config

class Database:
    def __init__(self):
        mongo_uri = Config.MONGO_URI or os.getenv('MONGO_URI', '')
        if not mongo_uri:
            raise RuntimeError('MONGO_URI not configured. Set MONGO_URI in backend/.env or environment variables.')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['venture_scout']
        self.projects = self.db['projects']
    
    def save_project(self, project_data):
        return self.projects.update_one(
            {'id': project_data['id']},
            {'$set': project_data},
            upsert=True
        )
    
    def get_project(self, project_id):
        return self.projects.find_one({'id': project_id})
    
    def get_all_projects(self):
        return list(self.projects.find())
