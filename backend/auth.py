import os
import jwt
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from functools import wraps
from flask import request, jsonify, session
from user_manager import user_data_manager

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'your-secret-key-change-this')

class AuthManager:
    """Handles authentication and authorization"""
    
    @staticmethod
    def verify_google_token(token: str) -> Optional[Dict]:
        """Verify Google OAuth ID token and return user info"""
        try:
            # Verify the ID token with Google
            response = requests.get(
                f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
            )
            
            if response.status_code != 200:
                return None
            
            token_info = response.json()
            
            # Verify the audience (client ID)
            if token_info.get('aud') != GOOGLE_CLIENT_ID:
                return None
            
            # Return user information
            return {
                'sub': token_info.get('sub'),  # Google user ID
                'email': token_info.get('email'),
                'name': token_info.get('name'),
                'picture': token_info.get('picture')
            }
            
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    @staticmethod
    def generate_jwt_token(user_id: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def generate_token(user_id: str) -> str:
        """Alias for generate_jwt_token for backward compatibility"""
        return AuthManager.generate_jwt_token(user_id)
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[str]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_current_user() -> Optional[str]:
        """Get current user ID from request"""
        # Try to get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            return AuthManager.verify_jwt_token(token)
        
        # Try to get token from session (for web interface)
        token = session.get('jwt_token')
        if token:
            return AuthManager.verify_jwt_token(token)
        
        return None
    
    @staticmethod
    def login_user(google_token: str) -> Optional[Dict]:
        """Login user with Google token"""
        user_info = AuthManager.verify_google_token(google_token)
        if not user_info:
            return None
        
        user_id = user_info['id']
        
        # Update or create user profile
        profile = user_data_manager.load_user_profile(user_id)
        profile.update({
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info['picture'],
            'last_login': datetime.now()
        })
        user_data_manager.save_user_profile(user_id, profile)
        
        # Generate JWT token
        jwt_token = AuthManager.generate_jwt_token(user_id)
        
        return {
            'user': {
                'id': user_id,
                'email': user_info['email'],
                'name': user_info['name'],
                'picture': user_info['picture']
            },
            'token': jwt_token,
            'is_new_user': not user_data_manager.user_exists(user_id) or len(user_data_manager.load_user_topics(user_id)) == 0
        }

def require_auth(f):
    """Decorator to require authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = AuthManager.get_current_user()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Add user_id to request context for compatibility
        request.user_id = user_id
        request.current_user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user_id() -> str:
    """Get current user ID from request context"""
    return getattr(request, 'user_id', None)