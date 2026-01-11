"""
Tests for user profile and chat upload endpoints
"""
import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_vectors import app


class UserEndpointsTestCase(unittest.TestCase):
    """Test cases for user endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Mock services
        self.user_service_patcher = patch('app_vectors.user_service')
        self.feature_extractor_patcher = patch('app_vectors.feature_extractor')
        self.vector_store_patcher = patch('app_vectors.vector_store')
        
        self.mock_user_service = self.user_service_patcher.start()
        self.mock_feature_extractor = self.feature_extractor_patcher.start()
        self.mock_vector_store = self.vector_store_patcher.start()
        
        # Setup link_vector_to_user mock
        self.mock_user_service.link_vector_to_user = MagicMock()
        
        # Setup default mocks
        self.test_uid = 'test-uid-123'
        self.mock_user_service.get_user_by_uid.return_value = {
            'uid': self.test_uid,
            'email': 'test@example.com',
            'profile': {},
            'onboarding_complete': False
        }
        
        self.mock_user_service.update_user_profile.return_value = {
            'uid': self.test_uid,
            'email': 'test@example.com',
            'profile': {'name': 'Test User'},
            'onboarding_complete': False
        }
        
        self.mock_feature_extractor.extract.return_value = (
            [0.1] * 200,  # Mock vector
            ['feature_1', 'feature_2']  # Mock labels
        )
        
        self.mock_vector_store.add.return_value = 'vector-id-123'
    
    def tearDown(self):
        """Clean up after tests"""
        self.user_service_patcher.stop()
        self.feature_extractor_patcher.stop()
        self.vector_store_patcher.stop()
    
    def test_update_profile_success(self):
        """Test successful profile update"""
        profile_data = {
            'name': 'Test User',
            'instagram_handle': 'testuser',
            'location': 'Test City',
            'height': '180',
            'height_unit': 'cm',
            'ethnicity': 'Test'
        }
        
        response = self.app.post(f'/api/users/{self.test_uid}/profile',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('profile', data)
        self.mock_user_service.update_user_profile.assert_called_once()
    
    def test_update_profile_user_not_found(self):
        """Test profile update for non-existent user"""
        self.mock_user_service.update_user_profile.side_effect = ValueError('User not found')
        
        profile_data = {'name': 'Test User'}
        
        response = self.app.post('/api/users/nonexistent-uid/profile',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_upload_chat_data_json(self):
        """Test chat data upload with JSON file"""
        chat_data = {
            'messages': [
                {'sender': 'user', 'text': 'Hello', 'timestamp': 1234567890},
                {'sender': 'bot', 'text': 'Hi there!', 'timestamp': 1234567891}
            ]
        }
        
        file_content = json.dumps(chat_data).encode('utf-8')
        
        response = self.app.post(f'/api/users/{self.test_uid}/upload-chat',
                                data={'file': (BytesIO(file_content), 'chat.json', 'application/json')},
                                content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('vector_id', data)
        self.mock_feature_extractor.extract.assert_called_once()
        self.mock_vector_store.add.assert_called_once()
        self.mock_user_service.link_vector_to_user.assert_called_once()
    
    def test_upload_chat_data_txt(self):
        """Test chat data upload with TXT file"""
        txt_content = "Hello\nHow are you?\nI'm fine, thanks!"
        file_content = txt_content.encode('utf-8')
        
        response = self.app.post(f'/api/users/{self.test_uid}/upload-chat',
                                data={'file': (BytesIO(file_content), 'chat.txt', 'text/plain')},
                                content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('vector_id', data)
    
    def test_upload_chat_data_user_not_found(self):
        """Test chat upload for non-existent user"""
        self.mock_user_service.get_user_by_uid.return_value = None
        
        chat_data = {'messages': [{'sender': 'user', 'text': 'Hello'}]}
        file_content = json.dumps(chat_data).encode('utf-8')
        
        response = self.app.post('/api/users/nonexistent-uid/upload-chat',
                                data={'file': (BytesIO(file_content), 'chat.json', 'application/json')},
                                content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_upload_chat_data_no_file(self):
        """Test chat upload without file"""
        response = self.app.post(f'/api/users/{self.test_uid}/upload-chat',
                                content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_user_success(self):
        """Test getting user data"""
        self.mock_user_service.get_user_by_uid.return_value = {
            'uid': self.test_uid,
            'email': 'test@example.com',
            'profile': {'name': 'Test User'},
            'onboarding_complete': True,
            'vector_id': 'vector-id-123'
        }
        
        self.mock_vector_store.get.return_value = {
            'vector': [0.1] * 200,
            'metadata': {'message_count': 10}
        }
        
        response = self.app.get(f'/api/users/{self.test_uid}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('profile', data)
        self.assertIn('vector', data)
        self.assertIn('metadata', data)
    
    def test_get_user_not_found(self):
        """Test getting non-existent user"""
        self.mock_user_service.get_user_by_uid.return_value = None
        
        response = self.app.get('/api/users/nonexistent-uid')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_complete_onboarding(self):
        """Test marking onboarding as complete"""
        self.mock_user_service.mark_onboarding_complete = MagicMock()
        
        response = self.app.post(f'/api/users/{self.test_uid}/complete-onboarding')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.mock_user_service.mark_onboarding_complete.assert_called_once_with(self.test_uid)


if __name__ == '__main__':
    unittest.main()

