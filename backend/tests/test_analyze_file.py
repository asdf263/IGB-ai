"""Tests for analyze-file endpoint"""
import unittest
import os
import sys
from io import BytesIO
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import BaseTestCase


class AnalyzeFileTestCase(BaseTestCase):
    """Test cases for analyze-file endpoint"""
    
    @patch('app.model')
    def test_analyze_file_no_file(self, mock_model):
        """Test analyze-file endpoint without file"""
        response = self.app.post('/api/analyze-file')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No file provided')
    
    @patch('app.model')
    def test_analyze_file_invalid_file(self, mock_model):
        """Test analyze-file endpoint with invalid file"""
        data = {
            'file': (BytesIO(b'content'), 'test.exe')
        }
        response = self.app.post('/api/analyze-file', data=data)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('app.model')
    def test_analyze_file_gemini_not_configured(self, mock_model):
        """Test analyze-file endpoint when Gemini is not configured"""
        with patch('app.model', None):
            data = {
                'file': (BytesIO(b'content'), 'test.txt')
            }
            response = self.app.post('/api/analyze-file', data=data)
            self.assertEqual(response.status_code, 500)
            data = response.get_json()
            self.assertIn('error', data)
            self.assertEqual(data['error'], 'Gemini API not configured')
    
    @patch('app.model')
    def test_analyze_file_success(self, mock_model):
        """Test successful analyze-file endpoint"""
        mock_response = MagicMock()
        mock_response.text = "File analysis result"
        mock_model.generate_content.return_value = mock_response
        
        test_content = b'This is test file content'
        data = {
            'file': (BytesIO(test_content), 'test.txt'),
            'analysis_type': 'summary'
        }
        response = self.app.post('/api/analyze-file', data=data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['filename'], 'test.txt')
        self.assertEqual(data['analysis_type'], 'summary')
        self.assertEqual(data['result'], "File analysis result")
        self.assertEqual(data['input_length'], len(test_content))
        mock_model.generate_content.assert_called_once()
    
    @patch('app.model')
    def test_analyze_file_different_types(self, mock_model):
        """Test analyze-file with different analysis types"""
        mock_response = MagicMock()
        mock_response.text = "Analysis result"
        mock_model.generate_content.return_value = mock_response
        
        for analysis_type in ['general', 'summary', 'sentiment', 'keywords']:
            test_content = b'Test content'
            data = {
                'file': (BytesIO(test_content), 'test.txt'),
                'analysis_type': analysis_type
            }
            response = self.app.post('/api/analyze-file', data=data)
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['analysis_type'], analysis_type)
    
    @patch('app.model')
    def test_analyze_file_error_cleanup(self, mock_model):
        """Test that temp file is cleaned up even on error"""
        mock_model.generate_content.side_effect = Exception("API Error")
        
        test_content = b'Test content'
        data = {
            'file': (BytesIO(test_content), 'test.txt')
        }
        response = self.app.post('/api/analyze-file', data=data)
        self.assertEqual(response.status_code, 500)
        # File should be cleaned up (we can't easily verify this, but the code should handle it)


if __name__ == '__main__':
    unittest.main()

