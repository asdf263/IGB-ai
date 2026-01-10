"""Tests for text analyze endpoint"""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import BaseTestCase


class AnalyzeTestCase(BaseTestCase):
    """Test cases for text analyze endpoint"""
    
    @patch('app.model')
    def test_analyze_no_text(self, mock_model):
        """Test analyze endpoint without text"""
        response = self.app.post('/api/analyze', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No text provided')
    
    @patch('app.model')
    def test_analyze_empty_text(self, mock_model):
        """Test analyze endpoint with empty text"""
        response = self.app.post('/api/analyze', json={'text': ''})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Text is empty')
    
    @patch('app.model')
    def test_analyze_gemini_not_configured(self, mock_model):
        """Test analyze endpoint when Gemini is not configured"""
        # Set model to None
        with patch('app.model', None):
            response = self.app.post('/api/analyze', json={'text': 'test'})
            self.assertEqual(response.status_code, 500)
            data = response.get_json()
            self.assertIn('error', data)
            self.assertEqual(data['error'], 'Gemini API not configured')
    
    @patch('app.model')
    def test_analyze_general(self, mock_model):
        """Test analyze endpoint with general analysis type"""
        mock_response = MagicMock()
        mock_response.text = "This is a general analysis result"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/analyze', json={
            'text': 'Test text to analyze',
            'analysis_type': 'general'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['analysis_type'], 'general')
        self.assertEqual(data['result'], "This is a general analysis result")
        self.assertEqual(data['input_length'], len('Test text to analyze'))
        mock_model.generate_content.assert_called_once()
    
    @patch('app.model')
    def test_analyze_summary(self, mock_model):
        """Test analyze endpoint with summary analysis type"""
        mock_response = MagicMock()
        mock_response.text = "Summary: This is a summary"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/analyze', json={
            'text': 'Long text to summarize',
            'analysis_type': 'summary'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['analysis_type'], 'summary')
        mock_model.generate_content.assert_called_once()
    
    @patch('app.model')
    def test_analyze_sentiment(self, mock_model):
        """Test analyze endpoint with sentiment analysis type"""
        mock_response = MagicMock()
        mock_response.text = "Sentiment: Positive"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/analyze', json={
            'text': 'I love this product!',
            'analysis_type': 'sentiment'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['analysis_type'], 'sentiment')
    
    @patch('app.model')
    def test_analyze_keywords(self, mock_model):
        """Test analyze endpoint with keywords analysis type"""
        mock_response = MagicMock()
        mock_response.text = "Keywords: test, analysis, keywords"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/analyze', json={
            'text': 'Test text for keyword extraction',
            'analysis_type': 'keywords'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['analysis_type'], 'keywords')
    
    @patch('app.model')
    def test_analyze_qa(self, mock_model):
        """Test analyze endpoint with Q&A analysis type"""
        mock_response = MagicMock()
        mock_response.text = "Answer: The main points are..."
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/analyze', json={
            'text': 'Some text content',
            'analysis_type': 'qa',
            'question': 'What are the main points?'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['analysis_type'], 'qa')
        # Verify question is included in prompt
        call_args = mock_model.generate_content.call_args[0][0]
        self.assertIn('What are the main points?', call_args)
    
    @patch('app.model')
    def test_analyze_invalid_type_defaults_to_general(self, mock_model):
        """Test analyze endpoint with invalid analysis type defaults to general"""
        mock_response = MagicMock()
        mock_response.text = "General analysis"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/analyze', json={
            'text': 'Test text',
            'analysis_type': 'invalid_type'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['analysis_type'], 'invalid_type')
    
    @patch('app.model')
    def test_analyze_gemini_error(self, mock_model):
        """Test analyze endpoint when Gemini API raises an error"""
        mock_model.generate_content.side_effect = Exception("API Error")
        
        response = self.app.post('/api/analyze', json={
            'text': 'Test text',
            'analysis_type': 'general'
        })
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('Analysis failed', data['error'])
    
    @patch('app.model')
    def test_analyze_response_without_text_attribute(self, mock_model):
        """Test analyze endpoint when response doesn't have text attribute"""
        mock_response = MagicMock()
        del mock_response.text  # Remove text attribute
        mock_response.__str__ = lambda x: "String representation"
        mock_model.generate_content.return_value = mock_response
        
        response = self.app.post('/api/analyze', json={
            'text': 'Test text',
            'analysis_type': 'general'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main()

