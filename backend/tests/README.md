# Backend Tests

This directory contains comprehensive tests for the IGB AI backend API.

## Test Structure

### Test Files

- **test_auth_endpoints.py** - Tests for authentication endpoints (signup, login)
- **test_user_endpoints.py** - Tests for user profile and chat upload endpoints
- **test_user_service.py** - Tests for UserService MongoDB operations
- **test_health.py** - Health check endpoint tests
- **test_upload.py** - File upload endpoint tests
- **test_analyze.py** - Text analysis endpoint tests
- **test_chat.py** - Chat endpoint tests
- **test_file_utils.py** - File utility function tests

## Running Tests

### Using pytest (Recommended)
```bash
cd backend
python -m pytest tests/ -v
```

### Run specific test file
```bash
python -m pytest tests/test_auth_endpoints.py -v
```

### Run specific test class
```bash
python -m pytest tests/test_user_service.py::TestUserService -v
```

### Using unittest
```bash
cd backend
python run_tests.py
```

## Test Coverage

### Authentication Endpoints
- ✅ User signup (success, duplicate, missing fields)
- ✅ User login (success, invalid credentials, missing fields)
- ✅ Username/email alias support

### User Endpoints
- ✅ Profile update (success, user not found)
- ✅ Chat data upload (JSON, TXT, user not found, no file)
- ✅ Get user data (success, not found)
- ✅ Complete onboarding

### User Service
- ✅ User creation
- ✅ Duplicate user prevention
- ✅ User authentication
- ✅ Get user by UID
- ✅ Profile updates
- ✅ Vector linking
- ✅ Onboarding completion
- ✅ MongoDB connection handling (with/without MongoDB)

## Test Features

1. **Mocking**: Tests use mocks to avoid external dependencies (MongoDB, feature extractors)
2. **Isolation**: Each test is independent and cleans up after itself
3. **Error Handling**: Tests verify proper error responses for invalid inputs
4. **Edge Cases**: Tests cover edge cases like missing fields, invalid data, etc.

## MongoDB Testing

Tests that require MongoDB will be skipped if MongoDB is not available. The `TestUserServiceNoMongoDB` class tests behavior when MongoDB is unavailable.

## Test Results

All 63 tests pass successfully:
- 7 authentication endpoint tests
- 9 user endpoint tests
- 12 user service tests (10 with MongoDB, 2 without)
- 35 existing tests (health, upload, analyze, chat, file utils)

## Notes

- Tests use a test database (`igb_ai_test`) to avoid affecting production data
- Test data is cleaned up after each test run
- Connection errors are properly handled and return 503 status codes

