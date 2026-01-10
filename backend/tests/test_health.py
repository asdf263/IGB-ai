"""Tests for health check endpoint"""
import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from test_base import BaseTestCase


class HealthCheckTestCase(BaseTestCase):
    """Test cases for health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('gemini_configured', data)


if __name__ == '__main__':
    unittest.main()

