"""Tests for file upload endpoint"""
import unittest
import os
import sys
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import BaseTestCase


class UploadTestCase(BaseTestCase):
    """Test cases for file upload endpoint"""
    
    def test_upload_no_file(self):
        """Test upload endpoint without file"""
        response = self.app.post('/api/upload')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No file provided')
    
    def test_upload_empty_filename(self):
        """Test upload with empty filename"""
        data = {
            'file': (BytesIO(b'fake content'), '')
        }
        response = self.app.post('/api/upload', data=data)
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
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'File type not allowed')
    
    def test_upload_valid_txt_file(self):
        """Test successful upload of text file"""
        test_content = b'This is a test file content'
        data = {
            'file': (BytesIO(test_content), 'test.txt')
        }
        response = self.app.post('/api/upload', data=data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['filename'], 'test.txt')
        self.assertEqual(data['content_length'], len(test_content))
        self.assertIn('preview', data)
    
    def test_upload_valid_md_file(self):
        """Test successful upload of markdown file"""
        test_content = b'# Test Markdown\n\nThis is a test.'
        data = {
            'file': (BytesIO(test_content), 'test.md')
        }
        response = self.app.post('/api/upload', data=data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['filename'], 'test.md')
    
    def test_upload_preview_truncation(self):
        """Test that preview is truncated to 500 characters"""
        long_content = b'A' * 1000
        data = {
            'file': (BytesIO(long_content), 'test.txt')
        }
        response = self.app.post('/api/upload', data=data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['preview']), 500)
        self.assertEqual(data['content_length'], 1000)


if __name__ == '__main__':
    unittest.main()

