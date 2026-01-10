# Backend API

Flask backend with Gemini LLM integration for text analysis and file processing.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
```

3. Run the application:
```bash
python app.py
```

## API Endpoints

### Health Check
- `GET /health` - Check API health status

### File Upload
- `POST /api/upload` - Upload a text file
  - Form data: `file` (file)
  - Returns: File content preview

### Text Analysis
- `POST /api/analyze` - Analyze text using Gemini
  - JSON body: `{ "text": "...", "analysis_type": "general|summary|sentiment|keywords|qa" }`
  - Returns: Analysis result

### File Analysis
- `POST /api/analyze-file` - Upload and analyze file in one request
  - Form data: `file` (file), `analysis_type` (optional)
  - Returns: Analysis result

### Chat
- `POST /api/chat` - Chat with Gemini
  - JSON body: `{ "message": "...", "context": "..." }`
  - Returns: Chat response

## Testing

Run tests:
```bash
python -m pytest tests/
```

Or:
```bash
python -m unittest discover tests
```

