"""Tests for chat endpoint"""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import BaseTestCase


class ChatTestCase(BaseTestCase):
    """Test cases for chat endpoint"""
    
    @patch('app.model')
    def test_chat_no_message(self, mock_model):
        """Test chat endpoint without message"""
        response = self.app.post('/api/chat', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No message provided')
    
    @patch('app.model')
    def test_chat_gemini_not_configured(self, mock_model):
        """Test chat endpoint when Gemini is not configured"""
        with patch('app.model', None):
            response = self.app.post('/api/chat', json={'message': 'Hello'})
            self.assertEqual(response.status_code, 500)
            data = response.get_json()
            self.assertIn('error', data)
            self.assertEqual(data['error'], 'Gemini API not configured')
    
    @patch('app.model')
    def test_chat_success(self, mock_model):
        """Test successful chat endpoint"""
        mock_response = MagicMock()
        mock_response.text = "Hello! How can I help you?"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/chat', json={
            'message': 'Hello'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['response'], "Hello! How can I help you?")
        mock_model.generate_content.assert_called_once()
    
    @patch('app.model')
    def test_chat_with_context(self, mock_model):
        """Test chat endpoint with context"""
        mock_response = MagicMock()
        mock_response.text = "Response with context"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/chat', json={
            'message': 'What did I say before?',
            'context': 'Previous conversation context'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        # Verify context is included in prompt
        call_args = mock_model.generate_content.call_args[0][0]
        self.assertIn('Previous conversation context', call_args)
        self.assertIn('What did I say before?', call_args)
    
    @patch('app.model')
    def test_chat_empty_context(self, mock_model):
        """Test chat endpoint with empty context"""
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/chat', json={
            'message': 'Hello',
            'context': ''
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
    
    @patch('app.model')
    def test_chat_gemini_error(self, mock_model):
        """Test chat endpoint when Gemini API raises an error"""
        mock_model.generate_content.side_effect = Exception("API Error")
        
        response = self.app.post('/api/chat', json={
            'message': 'Hello'
        })
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('Chat failed', data['error'])
    
    @patch('app.model')
    def test_chat_response_without_text_attribute(self, mock_model):
        """Test chat endpoint when response doesn't have text attribute"""
        mock_response = MagicMock()
        del mock_response.text
        mock_response.__str__ = lambda x: "String response"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/chat', json={
            'message': 'Hello'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main()

