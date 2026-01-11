#!/usr/bin/env python3
"""
Quick test script to verify the vectorization pipeline works.
Creates a test user, uploads chat data, and verifies the vector was created.

Usage: python test_vectorization.py
"""
import requests
import uuid
import os
import sys

BASE_URL = "http://localhost:5000"

# Path to a sample Instagram ZIP file for testing
SAMPLE_ZIP_PATH = os.path.join(
    os.path.dirname(__file__), 
    "../data/instagram_messages_example/instagram-ethannotethan-2026-01-11-jy11pLNS.zip"
)

def create_test_user():
    """Create a test user with a random email"""
    test_id = str(uuid.uuid4())[:8]
    email = f"test_{test_id}@example.com"
    
    print(f"\n{'='*60}")
    print(f"[1/4] Creating test user: {email}")
    print(f"{'='*60}")
    
    # Use the sync endpoint to create a user (simulates what Supabase flow does)
    response = requests.post(f"{BASE_URL}/api/users/sync", json={
        "uid": test_id,
        "email": email,
        "profile": {
            "name": f"Test User {test_id}",
            "age": 25,
            "instagram_handle": f"test_{test_id}",
            "city": "Test City",
            "country": "Test Country",
        }
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.status_code}")
        print(response.json())
        return None
    
    result = response.json()
    print(f"✅ User created: uid={test_id}")
    return test_id, email


def upload_chat_data(uid):
    """Upload chat data for the test user"""
    print(f"\n{'='*60}")
    print(f"[2/4] Uploading chat data for uid: {uid}")
    print(f"{'='*60}")
    
    if not os.path.exists(SAMPLE_ZIP_PATH):
        print(f"❌ Sample ZIP file not found at: {SAMPLE_ZIP_PATH}")
        print("Please provide a valid Instagram ZIP export file path")
        return None
    
    print(f"📁 Using sample file: {SAMPLE_ZIP_PATH}")
    print(f"   File size: {os.path.getsize(SAMPLE_ZIP_PATH) / (1024*1024):.2f} MB")
    
    with open(SAMPLE_ZIP_PATH, "rb") as f:
        files = {"file": ("instagram_export.zip", f, "application/zip")}
        response = requests.post(
            f"{BASE_URL}/api/users/{uid}/upload-chat",
            files=files,
            timeout=300  # 5 minute timeout for large files
        )
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.json())
        return None
    
    result = response.json()
    vector_id = result.get("vector_id")
    message_count = result.get("message_count")
    feature_count = result.get("feature_count")
    
    print(f"✅ Chat data uploaded successfully!")
    print(f"   Vector ID: {vector_id}")
    print(f"   Messages processed: {message_count}")
    print(f"   Features extracted: {feature_count}")
    
    return vector_id


def verify_user_has_vector(uid):
    """Verify the user now has a vector_id linked"""
    print(f"\n{'='*60}")
    print(f"[3/4] Verifying user has vector linked")
    print(f"{'='*60}")
    
    response = requests.get(f"{BASE_URL}/api/users/{uid}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get user: {response.status_code}")
        return False
    
    result = response.json()
    vector_id = result.get("vector_id")
    
    if vector_id:
        print(f"✅ User has vector_id: {vector_id}")
        return True
    else:
        print(f"❌ User does NOT have vector_id linked!")
        print(f"   Full response: {result}")
        return False


def test_compatibility(uid1, uid2):
    """Test compatibility calculation between two users"""
    print(f"\n{'='*60}")
    print(f"[4/4] Testing compatibility between users")
    print(f"{'='*60}")
    
    response = requests.get(f"{BASE_URL}/api/users/{uid1}/compatibility/{uid2}")
    
    if response.status_code == 400:
        error = response.json().get("detail", "Unknown error")
        print(f"⚠️  Compatibility check failed (400): {error}")
        return False
    elif response.status_code != 200:
        print(f"❌ Compatibility check failed: {response.status_code}")
        print(response.json())
        return False
    
    result = response.json()
    compat = result.get("compatibility", {})
    score = compat.get("overall_score", "N/A")
    
    print(f"✅ Compatibility calculated!")
    print(f"   Overall Score: {score}%")
    print(f"   Strengths: {compat.get('strengths', [])}")
    print(f"   Challenges: {compat.get('challenges', [])}")
    
    return True


def main():
    print("\n" + "="*60)
    print("🧪 VECTORIZATION PIPELINE TEST")
    print("="*60)
    
    # Check server is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print(f"❌ Server not healthy: {health.status_code}")
            sys.exit(1)
        print("✅ Backend server is running")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("   Make sure the backend is running: python main.py")
        sys.exit(1)
    
    # Create first test user
    result1 = create_test_user()
    if not result1:
        sys.exit(1)
    uid1, email1 = result1
    
    # Upload chat data for first user
    vector_id1 = upload_chat_data(uid1)
    if not vector_id1:
        sys.exit(1)
    
    # Verify first user has vector
    if not verify_user_has_vector(uid1):
        sys.exit(1)
    
    # Create second test user for compatibility testing
    result2 = create_test_user()
    if not result2:
        sys.exit(1)
    uid2, email2 = result2
    
    # Upload chat data for second user
    vector_id2 = upload_chat_data(uid2)
    if not vector_id2:
        sys.exit(1)
    
    # Verify second user has vector
    if not verify_user_has_vector(uid2):
        sys.exit(1)
    
    # Test compatibility between the two users
    test_compatibility(uid1, uid2)
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print(f"\nTest User 1: uid={uid1}, email={email1}")
    print(f"Test User 2: uid={uid2}, email={email2}")
    print("\nYou can now test in the mobile app by logging in as these users")
    print("or browse to them to see compatibility scores.\n")


if __name__ == "__main__":
    main()

