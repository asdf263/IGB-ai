"""
User Service - MongoDB operations for user authentication and profiles
"""
import os
import ssl
import certifi
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing users in MongoDB"""
    
    def __init__(self, mongodb_uri=None, db_name=None):
        """Initialize MongoDB connection"""
        self.mongodb_uri = mongodb_uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = db_name or os.getenv('MONGODB_DB_NAME', 'igb_ai')
        self.client = None
        self.db = None
        self.users_collection = None
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            # Check if using MongoDB Atlas (contains mongodb+srv or .mongodb.net)
            is_atlas = 'mongodb+srv' in self.mongodb_uri or '.mongodb.net' in self.mongodb_uri
            
            if is_atlas:
                # MongoDB Atlas requires TLS with proper certificate verification
                # Use ssl context for better compatibility
                import ssl
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                ssl_context.check_hostname = True
                ssl_context.verify_mode = ssl.CERT_REQUIRED
                
                self.client = MongoClient(
                    self.mongodb_uri,
                    serverSelectionTimeoutMS=10000,
                    tls=True,
                    tlsCAFile=certifi.where(),
                )
            else:
                # Local MongoDB
                self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            
            self.db = self.client[self.db_name]
            self.users_collection = self.db['users']
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.db_name}")
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB: {str(e)}. User service will not be available.")
            # Don't raise - allow app to start without MongoDB for testing
            self.client = None
            self.db = None
            self.users_collection = None
    
    def _ensure_connected(self):
        """Ensure MongoDB connection is available"""
        if self.client is None:
            self._connect()
        if self.client is None:
            raise ConnectionError("MongoDB connection not available")
    
    def create_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Create a new user account
        
        Args:
            email: User email/username
            password: Plain text password (for simulation)
            
        Returns:
            User document with uid
        """
        self._ensure_connected()
        # Check if user already exists
        existing = self.users_collection.find_one({'email': email})
        if existing:
            raise ValueError('User with this email already exists')
        
        # Generate UID
        uid = str(uuid.uuid4())
        
        # Create user document
        user_doc = {
            'uid': uid,
            'email': email,
            'password': password,  # Plain text for simulation
            'profile': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'onboarding_complete': False
        }
        
        result = self.users_collection.insert_one(user_doc)
        user_doc['_id'] = str(result.inserted_id)
        
        return {
            'uid': uid,
            'email': email,
            'profile': {},
            'onboarding_complete': False
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email/username
            password: Plain text password
            
        Returns:
            User document if authenticated, None otherwise
        """
        self._ensure_connected()
        user = self.users_collection.find_one({'email': email, 'password': password})
        
        if not user:
            return None
        
        return {
            'uid': user['uid'],
            'email': user['email'],
            'profile': user.get('profile', {}),
            'onboarding_complete': user.get('onboarding_complete', False)
        }
    
    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user by UID
        
        Args:
            uid: User UID
            
        Returns:
            User document or None
        """
        self._ensure_connected()
        user = self.users_collection.find_one({'uid': uid})
        
        if not user:
            return None
        
        return {
            'uid': user['uid'],
            'email': user['email'],
            'profile': user.get('profile', {}),
            'onboarding_complete': user.get('onboarding_complete', False),
            'vector_id': user.get('vector_id')
        }
    
    def update_user_profile(self, uid: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile
        
        Args:
            uid: User UID
            profile_data: Profile data to update
            
        Returns:
            Updated user document
        """
        self._ensure_connected()
        update_data = {
            'profile': profile_data,
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.users_collection.update_one(
            {'uid': uid},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            raise ValueError('User not found')
        
        return self.get_user_by_uid(uid)
    
    def link_vector_to_user(self, uid: str, vector_id: str) -> None:
        """
        Link a vector to a user
        
        Args:
            uid: User UID
            vector_id: Vector ID
        """
        self._ensure_connected()
        self.users_collection.update_one(
            {'uid': uid},
            {'$set': {'vector_id': vector_id, 'updated_at': datetime.now().isoformat()}}
        )
    
    def mark_onboarding_complete(self, uid: str) -> None:
        """
        Mark user onboarding as complete
        
        Args:
            uid: User UID
        """
        self._ensure_connected()
        self.users_collection.update_one(
            {'uid': uid},
            {'$set': {'onboarding_complete': True, 'updated_at': datetime.now().isoformat()}}
        )

