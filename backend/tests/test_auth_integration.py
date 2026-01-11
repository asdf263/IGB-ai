"""
Integration tests for authentication endpoints with real MongoDB
"""
import unittest
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_vectors import app
from services.user_service import UserService
from pymongo import MongoClient


class AuthIntegrationTestCase(unittest.TestCase):
    """Integration tests for authentication with real MongoDB"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        cls.app = app.test_client()
        cls.app.testing = True
        
        # Get MongoDB connection details - use same database as app for integration testing
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGODB_DB_NAME', 'igb_ai')
        
        # Use same database as app for integration tests
        cls.user_service = UserService(mongodb_uri=mongodb_uri, db_name=db_name)
        
        # Store database name for cleanup
        cls.test_db_name = db_name
        cls.mongodb_uri = mongodb_uri
        
        # Verify MongoDB connection
        try:
            client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            cls.mongodb_available = True
            print(f"\n✓ MongoDB connection successful: {mongodb_uri}")
            print(f"✓ Using database: {db_name}")
        except Exception as e:
            cls.mongodb_available = False
            print(f"\n✗ MongoDB connection failed: {e}")
            print("  Tests will be skipped")
    
    def setUp(self):
        """Set up before each test"""
        if not self.mongodb_available:
            self.skipTest("MongoDB not available")
        
        # Clean up any existing test users
        self._cleanup_test_users()
    
    def tearDown(self):
        """Clean up after each test"""
        if self.mongodb_available:
            self._cleanup_test_users()
    
    def _cleanup_test_users(self):
        """Remove test users from database"""
        try:
            test_email = f"test_{datetime.now().strftime('%Y%m%d')}@test.com"
            # Remove any users with test email pattern
            client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            db = client[self.test_db_name]
            db.users.delete_many({'email': {'$regex': '^test_.*@test\\.com$'}})
        except Exception as e:
            print(f"Warning: Could not cleanup test users: {e}")
    
    def test_mongodb_connection(self):
        """Test that MongoDB connection is working"""
        self.assertTrue(self.mongodb_available, "MongoDB should be available")
        self.assertIsNotNone(self.user_service.client, "UserService should have MongoDB client")
    
    def test_signup_success(self):
        """Test successful user signup"""
        email = f"test_{datetime.now().timestamp()}@test.com"
        password = "testpass123"
        
        response = self.app.post('/api/users/signup',
                                data=json.dumps({
                                    'email': email,
                                    'password': password
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 201, 
                        f"Expected 201, got {response.status_code}. Response: {response.data}")
        
        data = json.loads(response.data)
        self.assertTrue(data['success'], f"Response: {data}")
        self.assertIn('uid', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User created successfully')
        
        # Verify user exists in database
        user = self.user_service.get_user_by_uid(data['uid'])
        self.assertIsNotNone(user, "User should exist in database")
        self.assertEqual(user['email'], email)
    
    def test_signup_duplicate_email(self):
        """Test signup with duplicate email"""
        email = f"test_dup_{datetime.now().timestamp()}@test.com"
        password = "testpass123"
        
        # First signup should succeed
        response1 = self.app.post('/api/users/signup',
                                 data=json.dumps({
                                     'email': email,
                                     'password': password
                                 }),
                                 content_type='application/json')
        self.assertEqual(response1.status_code, 201)
        
        # Second signup with same email should fail
        response2 = self.app.post('/api/users/signup',
                                 data=json.dumps({
                                     'email': email,
                                     'password': password
                                 }),
                                 content_type='application/json')
        self.assertEqual(response2.status_code, 400)
        data = json.loads(response2.data)
        self.assertIn('error', data)
        self.assertIn('already exists', data['error'].lower())
    
    def test_signup_missing_email(self):
        """Test signup with missing email"""
        response = self.app.post('/api/users/signup',
                                data=json.dumps({
                                    'password': 'testpass123'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_signup_missing_password(self):
        """Test signup with missing password"""
        response = self.app.post('/api/users/signup',
                                data=json.dumps({
                                    'email': 'test@test.com'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_success(self):
        """Test successful login"""
        email = f"test_login_{datetime.now().timestamp()}@test.com"
        password = "testpass123"
        
        # First create user
        signup_response = self.app.post('/api/users/signup',
                                       data=json.dumps({
                                           'email': email,
                                           'password': password
                                       }),
                                       content_type='application/json')
        self.assertEqual(signup_response.status_code, 201)
        signup_data = json.loads(signup_response.data)
        uid = signup_data['uid']
        
        # Now test login
        login_response = self.app.post('/api/users/login',
                                      data=json.dumps({
                                          'email': email,
                                          'password': password
                                      }),
                                      content_type='application/json')
        
        self.assertEqual(login_response.status_code, 200,
                         f"Expected 200, got {login_response.status_code}. Response: {login_response.data}")
        
        login_data = json.loads(login_response.data)
        self.assertTrue(login_data['success'], f"Response: {login_data}")
        self.assertEqual(login_data['uid'], uid)
        self.assertIn('user_profile', login_data)
        self.assertEqual(login_data['user_profile']['email'], email)
    
    def test_login_invalid_email(self):
        """Test login with non-existent email"""
        response = self.app.post('/api/users/login',
                                data=json.dumps({
                                    'email': 'nonexistent@test.com',
                                    'password': 'testpass123'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Invalid credentials', data['error'])
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        email = f"test_wrongpass_{datetime.now().timestamp()}@test.com"
        password = "correctpass123"
        
        # Create user
        signup_response = self.app.post('/api/users/signup',
                                       data=json.dumps({
                                           'email': email,
                                           'password': password
                                       }),
                                       content_type='application/json')
        self.assertEqual(signup_response.status_code, 201)
        
        # Try login with wrong password
        login_response = self.app.post('/api/users/login',
                                      data=json.dumps({
                                          'email': email,
                                          'password': 'wrongpassword'
                                      }),
                                      content_type='application/json')
        
        self.assertEqual(login_response.status_code, 401)
        data = json.loads(login_response.data)
        self.assertIn('error', data)
        self.assertIn('Invalid credentials', data['error'])
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        # Missing password
        response = self.app.post('/api/users/login',
                                data=json.dumps({
                                    'email': 'test@test.com'
                                }),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Missing email
        response = self.app.post('/api/users/login',
                                data=json.dumps({
                                    'password': 'testpass123'
                                }),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_signup_username_alias(self):
        """Test signup accepts 'username' field as alias for 'email'"""
        email = f"test_username_{datetime.now().timestamp()}@test.com"
        password = "testpass123"
        
        response = self.app.post('/api/users/signup',
                                data=json.dumps({
                                    'username': email,  # Using username instead of email
                                    'password': password
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_login_username_alias(self):
        """Test login accepts 'username' field as alias for 'email'"""
        email = f"test_loginuser_{datetime.now().timestamp()}@test.com"
        password = "testpass123"
        
        # Create user
        signup_response = self.app.post('/api/users/signup',
                                       data=json.dumps({
                                           'email': email,
                                           'password': password
                                       }),
                                       content_type='application/json')
        self.assertEqual(signup_response.status_code, 201)
        
        # Login with username field
        login_response = self.app.post('/api/users/login',
                                      data=json.dumps({
                                          'username': email,  # Using username instead of email
                                          'password': password
                                      }),
                                      content_type='application/json')
        
        self.assertEqual(login_response.status_code, 200)
        data = json.loads(login_response.data)
        self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

