"""
Full end-to-end test of authentication and onboarding flow
Tests the complete user journey from signup to onboarding completion
"""
import unittest
import os
import sys
import json
from datetime import datetime
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_vectors import app
from services.user_service import UserService
from pymongo import MongoClient


class FullAuthFlowTestCase(unittest.TestCase):
    """Full end-to-end test of auth and onboarding flow"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        cls.app = app.test_client()
        cls.app.testing = True
        
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGODB_DB_NAME', 'igb_ai')
        cls.user_service = UserService(mongodb_uri=mongodb_uri, db_name=db_name)
        cls.mongodb_uri = mongodb_uri
        cls.db_name = db_name
        
        try:
            client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            cls.mongodb_available = True
            print(f"\n✓ MongoDB connection successful")
        except Exception as e:
            cls.mongodb_available = False
            print(f"\n✗ MongoDB connection failed: {e}")
    
    def setUp(self):
        """Set up before each test"""
        if not self.mongodb_available:
            self.skipTest("MongoDB not available")
        self._cleanup_test_users()
        self.test_email = f"flowtest_{datetime.now().timestamp()}@test.com"
        self.test_password = "TestPass123!"
        self.uid = None
    
    def tearDown(self):
        """Clean up after each test"""
        if self.mongodb_available:
            self._cleanup_test_users()
    
    def _cleanup_test_users(self):
        """Remove test users"""
        try:
            client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            db = client[self.db_name]
            db.users.delete_many({'email': {'$regex': '^flowtest_.*@test\\.com$'}})
        except Exception:
            pass
    
    def test_full_flow_signup_to_onboarding(self):
        """Test complete flow: signup -> profile -> chat upload -> complete"""
        
        # Step 1: Signup
        print("\n[1/4] Testing SIGNUP...")
        signup_response = self.app.post('/api/users/signup',
                                       data=json.dumps({
                                           'email': self.test_email,
                                           'password': self.test_password
                                       }),
                                       content_type='application/json')
        
        self.assertEqual(signup_response.status_code, 201, 
                        f"Signup failed: {signup_response.data}")
        signup_data = json.loads(signup_response.data)
        self.assertTrue(signup_data['success'])
        self.uid = signup_data['uid']
        self.assertIsNotNone(self.uid)
        print(f"✓ Signup successful, UID: {self.uid}")
        
        # Verify user in database
        user = self.user_service.get_user_by_uid(self.uid)
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], self.test_email)
        self.assertFalse(user.get('onboarding_complete', False))
        print("✓ User exists in database")
        
        # Step 2: Login
        print("\n[2/4] Testing LOGIN...")
        login_response = self.app.post('/api/users/login',
                                      data=json.dumps({
                                          'email': self.test_email,
                                          'password': self.test_password
                                      }),
                                      content_type='application/json')
        
        self.assertEqual(login_response.status_code, 200)
        login_data = json.loads(login_response.data)
        self.assertTrue(login_data['success'])
        self.assertEqual(login_data['uid'], self.uid)
        print("✓ Login successful")
        
        # Step 3: Update Profile
        print("\n[3/4] Testing PROFILE UPDATE...")
        profile_data = {
            'name': 'Test User',
            'instagram_handle': 'testuser',
            'location': 'Test City, Test State',
            'height': '175',
            'height_unit': 'cm',
            'ethnicity': 'Test'
        }
        
        profile_response = self.app.post(f'/api/users/{self.uid}/profile',
                                        data=json.dumps(profile_data),
                                        content_type='application/json')
        
        self.assertEqual(profile_response.status_code, 200)
        profile_result = json.loads(profile_response.data)
        self.assertTrue(profile_result['success'])
        self.assertEqual(profile_result['profile']['name'], 'Test User')
        print("✓ Profile update successful")
        
        # Verify profile in database
        user = self.user_service.get_user_by_uid(self.uid)
        self.assertEqual(user['profile']['name'], 'Test User')
        print("✓ Profile saved to database")
        
        # Step 4: Get User (verify all data)
        print("\n[4/4] Testing GET USER...")
        get_user_response = self.app.get(f'/api/users/{self.uid}')
        self.assertEqual(get_user_response.status_code, 200)
        user_data = json.loads(get_user_response.data)
        self.assertTrue(user_data['success'])
        self.assertEqual(user_data['metadata']['uid'], self.uid)
        self.assertEqual(user_data['profile']['name'], 'Test User')
        self.assertFalse(user_data['metadata']['onboarding_complete'])
        print("✓ Get user successful")
        
        # Step 5: Complete Onboarding
        print("\n[5/5] Testing COMPLETE ONBOARDING...")
        complete_response = self.app.post(f'/api/users/{self.uid}/complete-onboarding')
        self.assertEqual(complete_response.status_code, 200)
        complete_data = json.loads(complete_response.data)
        self.assertTrue(complete_data['success'])
        print("✓ Onboarding completion successful")
        
        # Verify onboarding complete in database
        user = self.user_service.get_user_by_uid(self.uid)
        self.assertTrue(user.get('onboarding_complete', False))
        print("✓ Onboarding status saved to database")
        
        print("\n" + "="*60)
        print("✓ FULL FLOW TEST PASSED")
        print("="*60)
    
    def test_input_validation(self):
        """Test input validation and safeguards"""
        print("\nTesting INPUT VALIDATION...")
        
        # Test empty email
        response = self.app.post('/api/users/signup',
                                data=json.dumps({'email': '', 'password': 'test'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        print("✓ Empty email rejected")
        
        # Test empty password
        response = self.app.post('/api/users/signup',
                                data=json.dumps({'email': 'test@test.com', 'password': ''}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        print("✓ Empty password rejected")
        
        # Test invalid UID
        response = self.app.get('/api/users/invalid-uid-12345')
        self.assertEqual(response.status_code, 404)
        print("✓ Invalid UID rejected")
        
        # Test profile update with invalid UID
        response = self.app.post('/api/users/invalid-uid-12345/profile',
                                data=json.dumps({'name': 'Test'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 404)
        print("✓ Profile update with invalid UID rejected")
    
    def test_database_safeguards(self):
        """Test database connection safeguards"""
        print("\nTesting DATABASE SAFEGUARDS...")
        
        # Create user first
        signup_response = self.app.post('/api/users/signup',
                                       data=json.dumps({
                                           'email': self.test_email,
                                           'password': self.test_password
                                       }),
                                       content_type='application/json')
        self.assertEqual(signup_response.status_code, 201)
        uid = json.loads(signup_response.data)['uid']
        
        # Verify user exists
        user = self.user_service.get_user_by_uid(uid)
        self.assertIsNotNone(user)
        print("✓ User creation writes to database")
        
        # Test duplicate signup
        duplicate_response = self.app.post('/api/users/signup',
                                          data=json.dumps({
                                              'email': self.test_email,
                                              'password': self.test_password
                                          }),
                                          content_type='application/json')
        self.assertEqual(duplicate_response.status_code, 400)
        print("✓ Duplicate email prevented")
        
        # Test wrong password
        wrong_pass_response = self.app.post('/api/users/login',
                                           data=json.dumps({
                                               'email': self.test_email,
                                               'password': 'wrongpassword'
                                           }),
                                           content_type='application/json')
        self.assertEqual(wrong_pass_response.status_code, 401)
        print("✓ Wrong password rejected")
        
        # Test correct password
        correct_pass_response = self.app.post('/api/users/login',
                                             data=json.dumps({
                                                 'email': self.test_email,
                                                 'password': self.test_password
                                             }),
                                             content_type='application/json')
        self.assertEqual(correct_pass_response.status_code, 200)
        print("✓ Correct password accepted")


if __name__ == '__main__':
    unittest.main(verbosity=2)

