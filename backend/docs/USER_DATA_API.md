# User Data Storage API Documentation

## Overview

The User Data Storage system provides a unified API for managing user profiles (MongoDB) and behavior vectors (ChromaDB). Users are linked via unique identifiers (UIDs) enabling bidirectional lookups.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask API (app.py)                       │
├─────────────────────────────────────────────────────────────┤
│                   UserDataService                           │
│              (Coordinates both stores)                      │
├────────────────────────┬────────────────────────────────────┤
│    MongoDBService      │       ChromaVectorStore            │
│   (User Profiles)      │      (Behavior Vectors)            │
├────────────────────────┼────────────────────────────────────┤
│    MongoDB Atlas       │          ChromaDB                  │
│                        │    (Persistent Storage)            │
└────────────────────────┴────────────────────────────────────┘
```

## Data Models

### User Profile (MongoDB)

```json
{
  "uid": "user_abc123def456",
  "name": "John Doe",
  "instagram_handle": "johndoe",
  "profile_picture": "https://example.com/pic.jpg",
  "current_living_location": {
    "city": "San Francisco",
    "state": "CA",
    "country": "USA",
    "coordinates": [-122.4194, 37.7749]
  },
  "height": 180,
  "ethnicity": "Asian",
  "vector_id": "vec_user_abc123def456",
  "created_at": "2026-01-11T02:30:45.441000",
  "updated_at": "2026-01-11T02:31:35.268000"
}
```

### Behavior Vector (ChromaDB)

```json
{
  "id": "vec_user_abc123def456",
  "vector": [0.5, 0.3, ...],  // 200 dimensions
  "metadata": {
    "uid": "user_abc123def456",
    "message_count": 150,
    "extracted_at": "2026-01-11T02:30:45.000000",
    "created_at": "2026-01-11T02:30:45.000000",
    "updated_at": "2026-01-11T02:31:35.000000"
  }
}
```

---

## API Endpoints

### Health Check

```
GET /health
```

Check system health including MongoDB and ChromaDB status.

**Response:**
```json
{
  "status": "healthy",
  "service": "IGB-AI User Data API",
  "mongodb": {
    "status": "healthy",
    "database": "igb_ai",
    "user_count": 42
  },
  "chromadb": {
    "status": "healthy",
    "storage_type": "chromadb",
    "vector_count": 42
  }
}
```

---

### Create User

```
POST /api/users/create
```

Create a new user with profile and optional behavior vector.

**Request Body:**
```json
{
  "name": "John Doe",
  "instagram_handle": "johndoe",
  "profile_picture": "https://example.com/pic.jpg",
  "current_living_location": {
    "city": "San Francisco",
    "state": "CA",
    "country": "USA"
  },
  "height": 180,
  "ethnicity": "Asian",
  "vector": [0.5, 0.3, ...],
  "vector_metadata": {
    "message_count": 150
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | ✅ | User's full name |
| instagram_handle | string | ❌ | Instagram username (without @) |
| profile_picture | string | ❌ | URL to profile image |
| current_living_location | object/string | ❌ | Location data |
| height | number | ❌ | Height in cm |
| ethnicity | string | ❌ | Ethnicity/race |
| vector | array[float] | ❌ | 200-dimensional behavior vector |
| vector_metadata | object | ❌ | Additional vector metadata |

**Response (201):**
```json
{
  "success": true,
  "uid": "user_abc123def456",
  "profile": { ... },
  "vector_id": "vec_user_abc123def456",
  "has_vector": true
}
```

**Errors:**
- `400` - Missing required field (name) or invalid vector dimensions
- `409` - User with UID already exists

---

### Get User

```
GET /api/users/:uid
```

Get complete user data including profile and vector.

**Response (200):**
```json
{
  "success": true,
  "uid": "user_abc123def456",
  "profile": {
    "uid": "user_abc123def456",
    "name": "John Doe",
    "instagram_handle": "johndoe",
    ...
  },
  "vector": [0.5, 0.3, ...],
  "vector_metadata": {
    "uid": "user_abc123def456",
    "message_count": 150,
    ...
  },
  "has_vector": true
}
```

**Errors:**
- `404` - User not found

---

### Update User Profile

```
PUT /api/users/:uid/profile
```

Update user profile fields.

**Request Body:**
```json
{
  "name": "John Updated",
  "height": 185,
  "current_living_location": {
    "city": "Los Angeles",
    "state": "CA",
    "country": "USA"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "profile": { ... }
}
```

**Errors:**
- `400` - Invalid Instagram handle format
- `404` - User not found

---

### Update User Vector

```
PUT /api/users/:uid/vector
```

Update user's behavior vector.

**Request Body:**
```json
{
  "vector": [0.8, 0.6, ...],
  "metadata": {
    "message_count": 200,
    "updated_reason": "new messages"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| vector | array[float] | ✅ | 200-dimensional behavior vector |
| metadata | object | ❌ | Updated metadata |

**Response (200):**
```json
{
  "success": true,
  "vector_id": "vec_user_abc123def456"
}
```

**Errors:**
- `400` - Missing vector or invalid dimensions (must be 200)
- `404` - User not found

---

### Delete User

```
DELETE /api/users/:uid
```

Delete user from both MongoDB and ChromaDB.

**Response (200):**
```json
{
  "success": true,
  "profile_deleted": true,
  "vector_deleted": true
}
```

**Errors:**
- `404` - User not found

---

### Search by Instagram Handle

```
GET /api/users/search/by-instagram/:handle
```

Find user by Instagram username.

**Parameters:**
- `handle` - Instagram username (with or without @)

**Response (200):**
```json
{
  "success": true,
  "uid": "user_abc123def456",
  "profile": { ... },
  "vector": [0.5, 0.3, ...],
  "vector_metadata": { ... },
  "has_vector": true
}
```

**Errors:**
- `404` - User not found

---

### Search by Similar Vector

```
POST /api/users/search/by-vector
```

Find users with similar behavior vectors using cosine similarity.

**Request Body:**
```json
{
  "query_vector": [0.6, 0.4, ...],
  "top_k": 10
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query_vector | array[float] | ✅ | 200-dimensional query vector |
| top_k | number | ❌ | Number of results (default: 10) |

**Response (200):**
```json
{
  "success": true,
  "results": [
    {
      "uid": "user_abc123def456",
      "similarity": 0.95,
      "profile": { ... },
      "vector_metadata": { ... }
    },
    ...
  ],
  "count": 5
}
```

**Errors:**
- `400` - Missing query_vector or invalid dimensions

---

### List Users

```
GET /api/users?limit=100&skip=0
```

List all users with pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | number | 100 | Max users to return |
| skip | number | 0 | Users to skip |

**Response (200):**
```json
{
  "success": true,
  "users": [ ... ],
  "count": 42,
  "limit": 100,
  "skip": 0
}
```

---

### Get Statistics

```
GET /api/stats
```

Get service statistics.

**Response (200):**
```json
{
  "success": true,
  "user_count": 42,
  "vector_count": 42,
  "mongodb": {
    "status": "healthy",
    "database": "igb_ai",
    "user_count": 42
  },
  "chromadb": {
    "status": "healthy",
    "storage_type": "chromadb",
    "vector_count": 42
  }
}
```

---

## Feature Extraction Endpoints

### Extract Features

```
POST /api/features/extract
```

Extract behavior vector from chat messages.

**Request Body:**
```json
{
  "messages": [
    {"sender": "user", "text": "Hello!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Hi there!", "timestamp": 1715234012}
  ],
  "uid": "user_abc123def456",
  "store": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| messages | array | ✅ | Chat messages to analyze |
| uid | string | ❌ | User ID to associate vector with |
| store | boolean | ❌ | Whether to store the vector |

**Response (200):**
```json
{
  "success": true,
  "vector": [0.5, 0.3, ...],
  "feature_labels": ["temporal_avg_response_time", ...],
  "feature_count": 200,
  "vector_id": "vec_user_abc123def456",
  "uid": "user_abc123def456"
}
```

---

### Extract and Store for User

```
POST /api/features/extract-and-store
```

Extract vector from messages and create a new user.

**Request Body:**
```json
{
  "messages": [ ... ],
  "profile": {
    "name": "John Doe",
    "instagram_handle": "johndoe"
  }
}
```

**Response (201):**
```json
{
  "success": true,
  "uid": "user_abc123def456",
  "vector_id": "vec_user_abc123def456",
  "profile": { ... },
  "vector": [0.5, 0.3, ...],
  "feature_labels": [ ... ],
  "feature_count": 200
}
```

---

## Environment Configuration

```bash
# .env file

# Server
PORT=5000

# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=igb_ai

# ChromaDB (optional - uses defaults)
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION=user_behavior_vectors
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message describing what went wrong"
}
```

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 500 | Internal Server Error |

---

## Usage Examples

### Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Create user
user = requests.post(f"{BASE_URL}/api/users/create", json={
    "name": "John Doe",
    "instagram_handle": "johndoe",
    "vector": [0.5] * 200
}).json()

uid = user["uid"]

# Get user
user_data = requests.get(f"{BASE_URL}/api/users/{uid}").json()

# Search similar users
similar = requests.post(f"{BASE_URL}/api/users/search/by-vector", json={
    "query_vector": [0.6] * 200,
    "top_k": 10
}).json()
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:5000";

// Create user
const createUser = async (profile: UserProfile, vector?: number[]) => {
  const res = await fetch(`${BASE_URL}/api/users/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...profile, vector })
  });
  return res.json();
};

// Search by vector
const searchByVector = async (queryVector: number[], topK = 10) => {
  const res = await fetch(`${BASE_URL}/api/users/search/by-vector`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query_vector: queryVector, top_k: topK })
  });
  return res.json();
};
```

### cURL

```bash
# Create user
curl -X POST http://localhost:5000/api/users/create \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "instagram_handle": "johndoe"}'

# Get user
curl http://localhost:5000/api/users/user_abc123def456

# Search by Instagram
curl http://localhost:5000/api/users/search/by-instagram/johndoe

# Delete user
curl -X DELETE http://localhost:5000/api/users/user_abc123def456
```

---

## Vector Dimensions

Behavior vectors are **200-dimensional** feature vectors extracted from chat messages. The dimensions represent:

| Range | Category | Description |
|-------|----------|-------------|
| 0-24 | Temporal | Response times, activity patterns |
| 25-49 | Text | Message length, vocabulary |
| 50-74 | Linguistic | Grammar, complexity |
| 75-99 | Semantic | Topic modeling, embeddings |
| 100-124 | Sentiment | Emotion detection |
| 125-149 | Behavioral | Engagement patterns |
| 150-174 | Graph | Conversation flow |
| 175-199 | Composite | Combined features |

Use `/api/features/labels` to get the full list of feature labels.


