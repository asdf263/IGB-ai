# Chatbot Integration Guide

This guide helps chatbots and AI assistants understand how to interact with the IGB AI backend API.

## Overview

The IGB AI backend provides text analysis and conversational AI capabilities using Google's Gemini LLM. Chatbots can use this API to:

1. Analyze user-uploaded text files
2. Perform various types of text analysis
3. Engage in conversational interactions
4. Process large text documents

## Quick Start

### Base URL
```
http://localhost:5000  (Development)
https://your-production-api.com  (Production)
```

### Health Check
Before making requests, check if the API is available:
```
GET /health
```

## Common Use Cases

### 1. Analyzing User Text

When a user provides text for analysis:

```python
POST /api/analyze
{
  "text": "User's text here",
  "analysis_type": "summary"  # or "general", "sentiment", "keywords"
}
```

**Analysis Types:**
- `general`: Get general insights and analysis
- `summary`: Get a comprehensive summary
- `sentiment`: Analyze emotional tone
- `keywords`: Extract main topics and keywords

### 2. Processing File Uploads

When a user uploads a file:

```python
POST /api/analyze-file
Form Data:
  - file: [file object]
  - analysis_type: "summary"  # optional
```

### 3. Conversational Interaction

For chat-based interactions:

```python
POST /api/chat
{
  "message": "User's question or message",
  "context": "Previous conversation context (optional)"
}
```

## Best Practices for Chatbots

1. **Error Handling**: Always check for error responses and provide user-friendly error messages
2. **Context Management**: Maintain conversation context when using the chat endpoint
3. **File Size**: Warn users about the 50MB file size limit
4. **Analysis Type Selection**: Help users choose the appropriate analysis type based on their needs
5. **Rate Limiting**: Be mindful of API usage and implement appropriate delays

## Example Integration

### Python Example

```python
import requests

API_BASE = "http://localhost:5000"

def analyze_text(text, analysis_type="general"):
    response = requests.post(
        f"{API_BASE}/api/analyze",
        json={"text": text, "analysis_type": analysis_type}
    )
    return response.json()

def chat_with_ai(message, context=""):
    response = requests.post(
        f"{API_BASE}/api/chat",
        json={"message": message, "context": context}
    )
    return response.json()
```

### JavaScript Example

```javascript
const API_BASE = "http://localhost:5000";

async function analyzeText(text, analysisType = "general") {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, analysis_type: analysisType })
  });
  return await response.json();
}

async function chatWithAI(message, context = "") {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context })
  });
  return await response.json();
}
```

## Response Format

All successful responses follow this pattern:
```json
{
  "success": true,
  "result": "...",
  ...
}
```

Error responses:
```json
{
  "error": "Error message here"
}
```

## Troubleshooting

1. **"Gemini API not configured"**: Ensure GEMINI_API_KEY is set in environment variables
2. **File upload fails**: Check file size (max 50MB) and file type (txt, md, pdf, docx)
3. **Timeout errors**: Large files may take time to process, increase timeout settings
4. **CORS errors**: Ensure CORS is properly configured for your frontend domain

