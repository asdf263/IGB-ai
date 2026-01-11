"""
Tests for authentication endpoints
"""
import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_vectors import app


class AuthEndpointsTestCase(unittest.TestCase):
    """Test cases for authentication endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Mock user_service to avoid MongoDB dependency
        self.user_service_patcher = patch('app_vectors.user_service')
        self.mock_user_service = self.user_service_patcher.start()
        
        # Setup mock user service methods
        self.mock_user_service.create_user = MagicMock()
        self.mock_user_service.authenticate_user = MagicMock()
        self.mock_user_service.get_user_by_uid = MagicMock()
    
    def tearDown(self):
        """Clean up after tests"""
        self.user_service_patcher.stop()
    
    def test_signup_success(self):
        """Test successful user signup"""
        # Mock successful user creation
        self.mock_user_service.create_user.return_value = {
            'uid': 'test-uid-123',
            'email': 'test@example.com',
            'profile': {},
            'onboarding_complete': False
        }
        
        response = self.app.post('/api/users/signup', 
                                 data=json.dumps({
                                     'email': 'test@example.com',
                                     'password': 'testpass123'
                                 }),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['uid'], 'test-uid-123')
        self.assertIn('message', data)
    
    def test_signup_missing_fields(self):
        """Test signup with missing fields"""
        response = self.app.post('/api/users/signup',
                                data=json.dumps({'email': 'test@example.com'}),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_signup_duplicate_user(self):
        """Test signup with duplicate email"""
        self.mock_user_service.create_user.side_effect = ValueError('User with this email already exists')
        
        response = self.app.post('/api/users/signup',
                                data=json.dumps({
                                    'email': 'existing@example.com',
                                    'password': 'testpass123'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_success(self):
        """Test successful user login"""
        self.mock_user_service.authenticate_user.return_value = {
            'uid': 'test-uid-123',
            'email': 'test@example.com',
            'profile': {'name': 'Test User'},
            'onboarding_complete': True
        }
        
        response = self.app.post('/api/users/login',
                                data=json.dumps({
                                    'email': 'test@example.com',
                                    'password': 'testpass123'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['uid'], 'test-uid-123')
        self.assertIn('user_profile', data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        self.mock_user_service.authenticate_user.return_value = None
        
        response = self.app.post('/api/users/login',
                                data=json.dumps({
                                    'email': 'test@example.com',
                                    'password': 'wrongpass'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = self.app.post('/api/users/login',
                                data=json.dumps({'email': 'test@example.com'}),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_username_alias(self):
        """Test login with 'username' field instead of 'email'"""
        self.mock_user_service.authenticate_user.return_value = {
            'uid': 'test-uid-123',
            'email': 'testuser',
            'profile': {},
            'onboarding_complete': False
        }
        
        response = self.app.post('/api/users/login',
                                data=json.dumps({
                                    'username': 'testuser',
                                    'password': 'testpass123'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main()

