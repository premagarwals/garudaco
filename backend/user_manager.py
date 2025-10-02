import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class UserDataManager:
    """Manages user-specific data storage and retrieval"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.ensure_base_dir()
    
    def ensure_base_dir(self):
        """Ensure the base directory for user data exists"""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def get_user_dir(self, user_id: str) -> str:
        """Get the directory path for a specific user"""
        user_dir = os.path.join(self.base_dir, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir
    
    def ensure_user_directory(self, user_id: str) -> str:
        """Ensure user directory exists - alias for get_user_dir"""
        return self.get_user_dir(user_id)
    
    def get_user_file_path(self, user_id: str, filename: str) -> str:
        """Get the full file path for a user-specific file"""
        return os.path.join(self.get_user_dir(user_id), filename)
    
    def load_user_topics(self, user_id: str) -> List[dict]:
        """Load topics data for a specific user"""
        file_path = self.get_user_file_path(user_id, "topics_data.json")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Convert datetime strings back to datetime objects
                for topic in data:
                    if topic.get('date_added'):
                        topic['date_added'] = datetime.fromisoformat(topic['date_added'])
                    if topic.get('last_seen'):
                        topic['last_seen'] = datetime.fromisoformat(topic['last_seen'])
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_user_topics(self, user_id: str, topics_data: List[dict]):
        """Save topics data for a specific user"""
        file_path = self.get_user_file_path(user_id, "topics_data.json")
        # Convert datetime objects to strings for JSON serialization
        serializable_data = []
        for topic in topics_data:
            topic_copy = topic.copy()
            if topic_copy.get('date_added'):
                topic_copy['date_added'] = topic_copy['date_added'].isoformat()
            if topic_copy.get('last_seen'):
                topic_copy['last_seen'] = topic_copy['last_seen'].isoformat()
            serializable_data.append(topic_copy)
        
        with open(file_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)
    
    def load_user_current_assessment(self, user_id: str) -> Optional[Dict]:
        """Load current assessment data for a specific user"""
        file_path = self.get_user_file_path(user_id, "current_assessment.json")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Convert datetime strings back to datetime objects
                if data.get('timestamp'):
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                for topic in data.get('topics', []):
                    if topic.get('date_added'):
                        topic['date_added'] = datetime.fromisoformat(topic['date_added'])
                    if topic.get('last_seen'):
                        topic['last_seen'] = datetime.fromisoformat(topic['last_seen'])
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def save_user_current_assessment(self, user_id: str, assessment_data: Dict):
        """Save current assessment data for a specific user"""
        file_path = self.get_user_file_path(user_id, "current_assessment.json")
        # Convert datetime objects to strings for JSON serialization
        serializable_data = assessment_data.copy()
        if serializable_data.get('timestamp'):
            serializable_data['timestamp'] = serializable_data['timestamp'].isoformat()
        
        for topic in serializable_data.get('topics', []):
            if topic.get('date_added'):
                topic['date_added'] = topic['date_added'].isoformat()
            if topic.get('last_seen'):
                topic['last_seen'] = topic['last_seen'].isoformat()
        
        with open(file_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)
    
    def clear_user_current_assessment(self, user_id: str):
        """Clear current assessment data for a specific user"""
        file_path = self.get_user_file_path(user_id, "current_assessment.json")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def load_user_profile(self, user_id: str) -> Dict:
        """Load user profile data"""
        file_path = self.get_user_file_path(user_id, "profile.json")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if data.get('created_at'):
                    data['created_at'] = datetime.fromisoformat(data['created_at'])
                if data.get('last_login'):
                    data['last_login'] = datetime.fromisoformat(data['last_login'])
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default profile for new users
            return {
                'user_id': user_id,
                'created_at': datetime.now(),
                'last_login': datetime.now(),
                'total_assessments': 0,
                'total_topics_added': 0
            }
    
    def save_user_profile(self, user_id: str, profile_data: Dict):
        """Save user profile data"""
        file_path = self.get_user_file_path(user_id, "profile.json")
        # Convert datetime objects to strings for JSON serialization
        serializable_data = profile_data.copy()
        if serializable_data.get('created_at'):
            serializable_data['created_at'] = serializable_data['created_at'].isoformat()
        if serializable_data.get('last_login'):
            serializable_data['last_login'] = serializable_data['last_login'].isoformat()
        
        with open(file_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)
    
    def user_exists(self, user_id: str) -> bool:
        """Check if a user directory exists"""
        return os.path.exists(self.get_user_dir(user_id))
    
    def get_all_users(self) -> List[str]:
        """Get list of all user IDs"""
        if not os.path.exists(self.base_dir):
            return []
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

# Global instance
user_data_manager = UserDataManager()