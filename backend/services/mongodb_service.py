"""
MongoDB Service Module
User profile storage and CRUD operations using MongoDB Atlas
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MongoDBService:
    """MongoDB Atlas service for user profile storage."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.users_collection = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB Atlas."""
        try:
            connection_string = os.getenv('MONGODB_URI')
            if not connection_string:
                logger.warning("MONGODB_URI not found, using local MongoDB")
                connection_string = "mongodb://localhost:27017"
            
            database_name = os.getenv('MONGODB_DATABASE', 'igb_ai')
            
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[database_name]
            self.users_collection = self.db['users']
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"MongoDB initialization error: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for fast lookups."""
        try:
            # Unique index on uid
            self.users_collection.create_index([("uid", ASCENDING)], unique=True)
            # Index on instagram_handle for lookups
            self.users_collection.create_index([("instagram_handle", ASCENDING)])
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    @staticmethod
    def generate_uid() -> str:
        """Generate a unique user ID."""
        return f"user_{uuid.uuid4().hex[:16]}"
    
    def create_user(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user profile.
        
        Args:
            profile_data: User profile information
            
        Returns:
            Created user profile with uid
            
        Raises:
            DuplicateKeyError: If uid or instagram_handle already exists
            ValueError: If required fields are missing
        """
        # Generate UID if not provided
        uid = profile_data.get('uid') or self.generate_uid()
        
        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in profile_data or not profile_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate instagram handle format if provided
        instagram_handle = profile_data.get('instagram_handle', '')
        if instagram_handle and not self._validate_instagram_handle(instagram_handle):
            raise ValueError("Invalid Instagram handle format")
        
        # Build user document
        now = datetime.utcnow()
        user_doc = {
            'uid': uid,
            'name': profile_data['name'],
            'instagram_handle': instagram_handle,
            'profile_picture': profile_data.get('profile_picture', ''),
            'current_living_location': self._normalize_location(
                profile_data.get('current_living_location', {})
            ),
            'height': profile_data.get('height'),  # in cm
            'ethnicity': profile_data.get('ethnicity', ''),
            'vector_id': profile_data.get('vector_id'),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            self.users_collection.insert_one(user_doc)
            # Remove MongoDB's _id from response
            user_doc.pop('_id', None)
            return user_doc
        except DuplicateKeyError:
            raise ValueError(f"User with uid '{uid}' already exists")
    
    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by UID.
        
        Args:
            uid: User's unique identifier
            
        Returns:
            User profile dict or None if not found
        """
        user = self.users_collection.find_one({'uid': uid}, {'_id': 0})
        if user:
            # Convert datetime to ISO string for JSON serialization
            user['created_at'] = user['created_at'].isoformat() if user.get('created_at') else None
            user['updated_at'] = user['updated_at'].isoformat() if user.get('updated_at') else None
        return user
    
    def get_user_by_instagram(self, handle: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by Instagram handle.
        
        Args:
            handle: Instagram username (with or without @)
            
        Returns:
            User profile dict or None if not found
        """
        # Normalize handle (remove @ if present)
        handle = handle.lstrip('@').lower()
        user = self.users_collection.find_one(
            {'instagram_handle': {'$regex': f'^{handle}$', '$options': 'i'}},
            {'_id': 0}
        )
        if user:
            user['created_at'] = user['created_at'].isoformat() if user.get('created_at') else None
            user['updated_at'] = user['updated_at'].isoformat() if user.get('updated_at') else None
        return user
    
    def update_user(self, uid: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user profile.
        
        Args:
            uid: User's unique identifier
            updates: Fields to update
            
        Returns:
            Updated user profile or None if user not found
        """
        # Prevent updating uid
        updates.pop('uid', None)
        updates.pop('_id', None)
        updates.pop('created_at', None)
        
        # Validate instagram handle if being updated
        if 'instagram_handle' in updates:
            if updates['instagram_handle'] and not self._validate_instagram_handle(updates['instagram_handle']):
                raise ValueError("Invalid Instagram handle format")
        
        # Normalize location if being updated
        if 'current_living_location' in updates:
            updates['current_living_location'] = self._normalize_location(
                updates['current_living_location']
            )
        
        updates['updated_at'] = datetime.utcnow()
        
        result = self.users_collection.update_one(
            {'uid': uid},
            {'$set': updates}
        )
        
        if result.matched_count == 0:
            return None
        
        return self.get_user(uid)
    
    def delete_user(self, uid: str) -> bool:
        """
        Delete user profile.
        
        Args:
            uid: User's unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        result = self.users_collection.delete_one({'uid': uid})
        return result.deleted_count > 0
    
    def list_users(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        List all users with pagination.
        
        Args:
            limit: Maximum number of users to return
            skip: Number of users to skip
            
        Returns:
            List of user profiles
        """
        cursor = self.users_collection.find({}, {'_id': 0}).skip(skip).limit(limit)
        users = []
        for user in cursor:
            user['created_at'] = user['created_at'].isoformat() if user.get('created_at') else None
            user['updated_at'] = user['updated_at'].isoformat() if user.get('updated_at') else None
            users.append(user)
        return users
    
    def count_users(self) -> int:
        """Get total number of users."""
        return self.users_collection.count_documents({})
    
    def user_exists(self, uid: str) -> bool:
        """Check if user exists."""
        return self.users_collection.count_documents({'uid': uid}) > 0
    
    def update_vector_id(self, uid: str, vector_id: str) -> bool:
        """
        Update the vector_id reference for a user.
        
        Args:
            uid: User's unique identifier
            vector_id: ChromaDB vector reference
            
        Returns:
            True if updated, False if user not found
        """
        result = self.users_collection.update_one(
            {'uid': uid},
            {'$set': {'vector_id': vector_id, 'updated_at': datetime.utcnow()}}
        )
        return result.matched_count > 0
    
    @staticmethod
    def _validate_instagram_handle(handle: str) -> bool:
        """Validate Instagram handle format."""
        import re
        handle = handle.lstrip('@')
        # Instagram handles: 1-30 chars, letters, numbers, periods, underscores
        pattern = r'^[a-zA-Z0-9_.]{1,30}$'
        return bool(re.match(pattern, handle))
    
    @staticmethod
    def _normalize_location(location: Any) -> Dict[str, Any]:
        """Normalize location data to consistent format."""
        if not location:
            return {
                'city': '',
                'state': '',
                'country': '',
                'coordinates': None
            }
        
        if isinstance(location, str):
            # Parse string location like "City, State, Country"
            parts = [p.strip() for p in location.split(',')]
            return {
                'city': parts[0] if len(parts) > 0 else '',
                'state': parts[1] if len(parts) > 1 else '',
                'country': parts[2] if len(parts) > 2 else '',
                'coordinates': None
            }
        
        if isinstance(location, dict):
            return {
                'city': location.get('city', ''),
                'state': location.get('state', ''),
                'country': location.get('country', ''),
                'coordinates': location.get('coordinates')  # [longitude, latitude]
            }
        
        return {
            'city': '',
            'state': '',
            'country': '',
            'coordinates': None
        }
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def health_check(self) -> Dict[str, Any]:
        """Check MongoDB connection health."""
        try:
            self.client.admin.command('ping')
            return {
                'status': 'healthy',
                'database': self.db.name if self.db is not None else None,
                'user_count': self.count_users()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

