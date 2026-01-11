"""
Tests for UserService
"""
import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import UserService


class TestUserService(unittest.TestCase):
    """Test cases for UserService"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use a test database
        self.test_db_name = 'igb_ai_test'
        self.test_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        # Try to create service with test DB
        try:
            self.user_service = UserService(mongodb_uri=self.test_uri, db_name=self.test_db_name)
            if self.user_service.client is None:
                self.skipTest("MongoDB not available")
        except Exception as e:
            self.skipTest(f"MongoDB connection failed: {str(e)}")
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'user_service') and self.user_service.client:
            # Clean up test data
            self.user_service.users_collection.delete_many({})
    
    def test_create_user(self):
        """Test user creation"""
        email = "test@example.com"
        password = "testpass123"
        
        user = self.user_service.create_user(email, password)
        
        self.assertIn('uid', user)
        self.assertEqual(user['email'], email)
        self.assertEqual(user['profile'], {})
        self.assertFalse(user['onboarding_complete'])
    
    def test_create_duplicate_user(self):
        """Test that duplicate users cannot be created"""
        email = "duplicate@example.com"
        password = "testpass123"
        
        # Create first user
        self.user_service.create_user(email, password)
        
        # Try to create duplicate
        with self.assertRaises(ValueError):
            self.user_service.create_user(email, password)
    
    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        email = "auth@example.com"
        password = "authpass123"
        
        # Create user
        created_user = self.user_service.create_user(email, password)
        
        # Authenticate
        authenticated = self.user_service.authenticate_user(email, password)
        
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated['uid'], created_user['uid'])
        self.assertEqual(authenticated['email'], email)
    
    def test_authenticate_user_failure(self):
        """Test failed user authentication"""
        email = "wrong@example.com"
        password = "wrongpass"
        
        result = self.user_service.authenticate_user(email, password)
        self.assertIsNone(result)
    
    def test_get_user_by_uid(self):
        """Test getting user by UID"""
        email = "getuser@example.com"
        password = "testpass123"
        
        created_user = self.user_service.create_user(email, password)
        uid = created_user['uid']
        
        retrieved_user = self.user_service.get_user_by_uid(uid)
        
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user['uid'], uid)
        self.assertEqual(retrieved_user['email'], email)
    
    def test_get_nonexistent_user(self):
        """Test getting non-existent user"""
        result = self.user_service.get_user_by_uid("nonexistent-uid")
        self.assertIsNone(result)
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        email = "update@example.com"
        password = "testpass123"
        
        created_user = self.user_service.create_user(email, password)
        uid = created_user['uid']
        
        profile_data = {
            'name': 'Test User',
            'instagram_handle': 'testuser',
            'location': 'Test City',
            'height': '180',
            'height_unit': 'cm',
            'ethnicity': 'Test'
        }
        
        updated_user = self.user_service.update_user_profile(uid, profile_data)
        
        self.assertEqual(updated_user['profile']['name'], 'Test User')
        self.assertEqual(updated_user['profile']['instagram_handle'], 'testuser')
        self.assertEqual(updated_user['profile']['location'], 'Test City')
    
    def test_update_nonexistent_user_profile(self):
        """Test updating profile for non-existent user"""
        profile_data = {'name': 'Test'}
        
        with self.assertRaises(ValueError):
            self.user_service.update_user_profile("nonexistent-uid", profile_data)
    
    def test_link_vector_to_user(self):
        """Test linking vector to user"""
        email = "vector@example.com"
        password = "testpass123"
        
        created_user = self.user_service.create_user(email, password)
        uid = created_user['uid']
        vector_id = "test-vector-id-123"
        
        self.user_service.link_vector_to_user(uid, vector_id)
        
        user = self.user_service.get_user_by_uid(uid)
        self.assertEqual(user['vector_id'], vector_id)
    
    def test_mark_onboarding_complete(self):
        """Test marking onboarding as complete"""
        email = "onboard@example.com"
        password = "testpass123"
        
        created_user = self.user_service.create_user(email, password)
        uid = created_user['uid']
        
        self.user_service.mark_onboarding_complete(uid)
        
        user = self.user_service.get_user_by_uid(uid)
        self.assertTrue(user['onboarding_complete'])


class TestUserServiceNoMongoDB(unittest.TestCase):
    """Test UserService behavior when MongoDB is not available"""
    
    @patch('services.user_service.MongoClient')
    def test_initialization_without_mongodb(self, mock_mongo):
        """Test that service can be initialized without MongoDB"""
        mock_mongo.side_effect = Exception("Connection failed")
        
        service = UserService()
        self.assertIsNone(service.client)
        self.assertIsNone(service.users_collection)
    
    @patch('services.user_service.MongoClient')
    def test_operations_without_connection(self, mock_mongo):
        """Test that operations raise ConnectionError when MongoDB is unavailable"""
        mock_mongo.side_effect = Exception("Connection failed")
        
        service = UserService()
        
        with self.assertRaises(ConnectionError):
            service.create_user("test@example.com", "password")


if __name__ == '__main__':
    unittest.main()

