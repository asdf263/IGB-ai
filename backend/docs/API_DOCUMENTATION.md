# API Documentation

This document provides comprehensive API documentation for the IGB AI backend service.

## Base URL

- Development: `http://localhost:5000`
- Production: `https://your-production-api.com`

## Authentication

Currently, the API does not require authentication. In production, implement proper authentication mechanisms.

## Endpoints

### Health Check

**GET** `/health`

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "gemini_configured": true
}
```

---

### Upload File

**POST** `/api/upload`

Upload a text file to the server.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file` (file): Text file to upload (txt, md, pdf, docx)

**Response:**
```json
{
  "success": true,
  "filename": "document.txt",
  "content_length": 1234,
  "preview": "First 500 characters of the file..."
}
```

**Error Response:**
```json
{
  "error": "No file provided"
}
```

---

### Analyze Text

**POST** `/api/analyze`

Analyze text using Gemini LLM.

**Request:**
```json
{
  "text": "Text to analyze...",
  "analysis_type": "general"
}
```

**Analysis Types:**
- `general`: General analysis and insights
- `summary`: Comprehensive summary
- `sentiment`: Sentiment analysis
- `keywords`: Extract key topics and keywords
- `qa`: Question answering (requires `question` field)

**Response:**
```json
{
  "success": true,
  "analysis_type": "general",
  "result": "Analysis result from Gemini...",
  "input_length": 1234
}
```

**Error Response:**
```json
{
  "error": "No text provided"
}
```

---

### Analyze File

**POST** `/api/analyze-file`

Upload and analyze a file in one request.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file` (file): Text file to analyze
  - `analysis_type` (string, optional): Type of analysis (default: "general")

**Response:**
```json
{
  "success": true,
  "filename": "document.txt",
  "analysis_type": "general",
  "result": "Analysis result from Gemini...",
  "input_length": 1234
}
```

---

### Chat

**POST** `/api/chat`

Chat with Gemini AI.

**Request:**
```json
{
  "message": "User message here",
  "context": "Optional conversation context"
}
```

**Response:**
```json
{
  "success": true,
  "response": "AI response from Gemini..."
}
```

**Error Response:**
```json
{
  "error": "No message provided"
}
```

## Error Codes

- `400`: Bad Request - Invalid input
- `500`: Internal Server Error - Server-side error

## Rate Limiting

Currently, there is no rate limiting implemented. Consider adding rate limiting for production use.

## File Size Limits

Maximum file size: 50MB

## Supported File Types

- `.txt` - Plain text
- `.md` - Markdown
- `.pdf` - PDF documents
- `.docx` - Word documents

