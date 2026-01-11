#!/usr/bin/env python3
"""
Quick verification script for auth endpoints
Run this to verify signup and login are working
"""
import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
TEST_EMAIL = f"verify_{os.getpid()}@test.com"
TEST_PASSWORD = "testpass123"

def test_signup():
    """Test signup endpoint"""
    print(f"\n{'='*60}")
    print("Testing SIGNUP endpoint")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/users/signup"
    data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success') and 'uid' in result:
                print("✓ SIGNUP SUCCESS")
                return result.get('uid')
            else:
                print("✗ SIGNUP FAILED - Invalid response format")
                return None
        else:
            print(f"✗ SIGNUP FAILED - Status {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"✗ CONNECTION ERROR - Is the server running at {BASE_URL}?")
        return None
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return None

def test_login(uid=None):
    """Test login endpoint"""
    print(f"\n{'='*60}")
    print("Testing LOGIN endpoint")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/users/login"
    data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and 'uid' in result:
                print("✓ LOGIN SUCCESS")
                if uid and result.get('uid') == uid:
                    print("✓ UID matches signup")
                return True
            else:
                print("✗ LOGIN FAILED - Invalid response format")
                return False
        else:
            print(f"✗ LOGIN FAILED - Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ CONNECTION ERROR - Is the server running at {BASE_URL}?")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_login_wrong_password():
    """Test login with wrong password"""
    print(f"\n{'='*60}")
    print("Testing LOGIN with wrong password")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/users/login"
    data = {
        'email': TEST_EMAIL,
        'password': 'wrongpassword'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("✓ Correctly rejected wrong password")
            return True
        else:
            print(f"✗ Should return 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    """Run all verification tests"""
    print(f"\n{'='*60}")
    print("AUTH ENDPOINTS VERIFICATION")
    print(f"{'='*60}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    
    # Test signup
    uid = test_signup()
    if not uid:
        print("\n✗ SIGNUP FAILED - Cannot proceed with login test")
        sys.exit(1)
    
    # Test login
    login_success = test_login(uid)
    if not login_success:
        print("\n✗ LOGIN FAILED")
        sys.exit(1)
    
    # Test wrong password
    wrong_pass_test = test_login_wrong_password()
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print("✓ Signup: PASSED")
    print("✓ Login: PASSED")
    if wrong_pass_test:
        print("✓ Wrong password rejection: PASSED")
    else:
        print("✗ Wrong password rejection: FAILED")
    
    print(f"\n{'='*60}")
    print("All tests completed!")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()

