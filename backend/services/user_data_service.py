"""
User Data Service Module
Unified service coordinating MongoDB (user profiles) and ChromaDB (behavior vectors)
"""
import logging
from typing import Optional, Dict, Any, List

from services.mongodb_service import MongoDBService
from services.vector_store_chroma import ChromaVectorStore

logger = logging.getLogger(__name__)


class UserDataService:
    """
    Unified service for user data management.
    Coordinates MongoDB for profile storage and ChromaDB for behavior vectors.
    """
    
    EXPECTED_VECTOR_DIM = 200
    
    def __init__(self, 
                 chroma_persist_dir: str = "./data/chroma",
                 chroma_collection: str = "user_behavior_vectors"):
        """
        Initialize UserDataService.
        
        Args:
            chroma_persist_dir: ChromaDB persistence directory
            chroma_collection: ChromaDB collection name
        """
        self.mongodb = MongoDBService()
        self.vector_store = ChromaVectorStore(
            persist_directory=chroma_persist_dir,
            collection_name=chroma_collection
        )
        logger.info("UserDataService initialized")
    
    def create_user(self, 
                   profile_data: Dict[str, Any], 
                   vector_data: Optional[List[float]] = None,
                   vector_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new user with profile and optional behavior vector.
        
        Args:
            profile_data: User profile information (name, instagram_handle, etc.)
            vector_data: Optional initial behavior vector (~200 dimensions)
            vector_metadata: Optional metadata for the vector
            
        Returns:
            Created user data including profile and vector_id
            
        Raises:
            ValueError: If validation fails or user already exists
        """
        # Validate vector dimensions if provided
        if vector_data:
            if len(vector_data) != self.EXPECTED_VECTOR_DIM:
                raise ValueError(
                    f"Invalid vector dimensions: expected {self.EXPECTED_VECTOR_DIM}, got {len(vector_data)}"
                )
        
        uid = None
        vector_id = None
        
        try:
            # Create user profile in MongoDB first
            user_profile = self.mongodb.create_user(profile_data)
            uid = user_profile['uid']
            
            # Create behavior vector in ChromaDB if provided
            if vector_data:
                metadata = vector_metadata or {}
                metadata['uid'] = uid
                vector_id = self.vector_store.add_user_vector(uid, vector_data, metadata)
                
                # Update user profile with vector_id reference
                self.mongodb.update_vector_id(uid, vector_id)
                user_profile['vector_id'] = vector_id
            
            logger.info(f"Created user {uid}")
            
            return {
                'uid': uid,
                'profile': user_profile,
                'vector_id': vector_id,
                'has_vector': vector_data is not None
            }
            
        except Exception as e:
            # Rollback: if MongoDB succeeded but ChromaDB failed, delete from MongoDB
            if uid and vector_data and not vector_id:
                logger.warning(f"Rolling back user creation for {uid} due to vector storage failure")
                self.mongodb.delete_user(uid)
            raise
    
    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get complete user data (profile + vector).
        
        Args:
            uid: User's unique identifier
            
        Returns:
            Dict containing profile, vector, and metadata or None if not found
        """
        profile = self.mongodb.get_user(uid)
        if not profile:
            return None
        
        vector_data = self.vector_store.get_user_vector(uid)
        
        return {
            'uid': uid,
            'profile': profile,
            'vector': vector_data['vector'] if vector_data else None,
            'vector_metadata': vector_data['metadata'] if vector_data else None,
            'has_vector': vector_data is not None
        }
    
    def update_user_profile(self, uid: str, profile_updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user profile information.
        
        Args:
            uid: User's unique identifier
            profile_updates: Fields to update
            
        Returns:
            Updated profile or None if user not found
        """
        updated = self.mongodb.update_user(uid, profile_updates)
        if updated:
            logger.info(f"Updated profile for user {uid}")
        return updated
    
    def update_user_vector(self, 
                          uid: str, 
                          new_vector: List[float],
                          metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Update user's behavior vector.
        
        Args:
            uid: User's unique identifier
            new_vector: New behavior vector
            metadata: Optional updated metadata
            
        Returns:
            Vector ID or None if user not found
        """
        # Validate user exists
        if not self.mongodb.user_exists(uid):
            return None
        
        # Validate vector dimensions
        if len(new_vector) != self.EXPECTED_VECTOR_DIM:
            raise ValueError(
                f"Invalid vector dimensions: expected {self.EXPECTED_VECTOR_DIM}, got {len(new_vector)}"
            )
        
        metadata = metadata or {}
        metadata['uid'] = uid
        
        vector_id = self.vector_store.update_user_vector(uid, new_vector, metadata)
        
        # Update vector_id reference in MongoDB
        self.mongodb.update_vector_id(uid, vector_id)
        
        logger.info(f"Updated vector for user {uid}")
        return vector_id
    
    def delete_user(self, uid: str) -> Dict[str, bool]:
        """
        Delete user from both MongoDB and ChromaDB.
        
        Args:
            uid: User's unique identifier
            
        Returns:
            Dict with deletion status for profile and vector
        """
        profile_deleted = self.mongodb.delete_user(uid)
        vector_deleted = self.vector_store.delete_user_vector(uid)
        
        if profile_deleted or vector_deleted:
            logger.info(f"Deleted user {uid}: profile={profile_deleted}, vector={vector_deleted}")
        
        return {
            'profile_deleted': profile_deleted,
            'vector_deleted': vector_deleted,
            'success': profile_deleted or vector_deleted
        }
    
    def get_user_by_instagram(self, handle: str) -> Optional[Dict[str, Any]]:
        """
        Find user by Instagram handle.
        
        Args:
            handle: Instagram username (with or without @)
            
        Returns:
            Complete user data or None if not found
        """
        profile = self.mongodb.get_user_by_instagram(handle)
        if not profile:
            return None
        
        uid = profile['uid']
        vector_data = self.vector_store.get_user_vector(uid)
        
        return {
            'uid': uid,
            'profile': profile,
            'vector': vector_data['vector'] if vector_data else None,
            'vector_metadata': vector_data['metadata'] if vector_data else None,
            'has_vector': vector_data is not None
        }
    
    def search_users_by_vector(self, 
                               query_vector: List[float], 
                               top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find users with similar behavior vectors.
        
        Args:
            query_vector: Query behavior vector
            top_k: Number of results to return
            
        Returns:
            List of users with similarity scores
        """
        # Validate vector dimensions
        if len(query_vector) != self.EXPECTED_VECTOR_DIM:
            raise ValueError(
                f"Invalid vector dimensions: expected {self.EXPECTED_VECTOR_DIM}, got {len(query_vector)}"
            )
        
        # Search in ChromaDB
        similar_vectors = self.vector_store.search_users_by_vector(query_vector, top_k=top_k)
        
        # Enrich with user profiles
        results = []
        for match in similar_vectors:
            uid = match.get('uid')
            if uid:
                profile = self.mongodb.get_user(uid)
                results.append({
                    'uid': uid,
                    'similarity': match['similarity'],
                    'profile': profile,
                    'vector_metadata': match.get('metadata', {})
                })
        
        return results
    
    def list_users(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        List all users with pagination.
        
        Args:
            limit: Maximum number of users to return
            skip: Number of users to skip
            
        Returns:
            List of user profiles
        """
        return self.mongodb.list_users(limit=limit, skip=skip)
    
    def user_exists(self, uid: str) -> bool:
        """Check if user exists."""
        return self.mongodb.user_exists(uid)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        mongo_health = self.mongodb.health_check()
        chroma_health = self.vector_store.health_check()
        
        return {
            'user_count': self.mongodb.count_users(),
            'vector_count': self.vector_store.count(),
            'mongodb': mongo_health,
            'chromadb': chroma_health
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all services."""
        mongo_status = self.mongodb.health_check()
        chroma_status = self.vector_store.health_check()
        
        overall_healthy = (
            mongo_status.get('status') == 'healthy' and
            chroma_status.get('status') == 'healthy'
        )
        
        return {
            'status': 'healthy' if overall_healthy else 'degraded',
            'mongodb': mongo_status,
            'chromadb': chroma_status
        }
    
    def close(self):
        """Close all connections."""
        self.mongodb.close()
        logger.info("UserDataService connections closed")


