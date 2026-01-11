#!/usr/bin/env python
"""
Test runner for all backend tests
"""
import unittest
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_tests():
    """Load all test modules"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Discover all tests in the tests directory
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite.addTests(loader.discover(test_dir, pattern='test_*.py'))
    
    return suite

if __name__ == '__main__':
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    suite = load_tests()
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

