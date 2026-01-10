import unittest
import os
import sys
import tempfile
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, allowed_file


class FlaskAppTestCase(unittest.TestCase):
    """Test cases for Flask application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_allowed_file(self):
        """Test file extension validation"""
        self.assertTrue(allowed_file('test.txt'))
        self.assertTrue(allowed_file('test.md'))
        self.assertFalse(allowed_file('test.exe'))
        self.assertFalse(allowed_file('test'))
    
    def test_upload_no_file(self):
        """Test upload endpoint without file"""
        response = self.app.post('/api/upload')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        data = {
            'file': (BytesIO(b'fake content'), 'test.exe')
        }
        response = self.app.post('/api/upload', data=data)
        self.assertEqual(response.status_code, 400)
    
    def test_analyze_no_text(self):
        """Test analyze endpoint without text"""
        response = self.app.post('/api/analyze', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_analyze_empty_text(self):
        """Test analyze endpoint with empty text"""
        response = self.app.post('/api/analyze', json={'text': ''})
        self.assertEqual(response.status_code, 400)
    
    def test_chat_no_message(self):
        """Test chat endpoint without message"""
        response = self.app.post('/api/chat', json={})
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()

