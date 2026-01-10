# IGB AI

SB HACKS 2026 - iOS app with React Native frontend and Python Flask backend, featuring Gemini LLM integration for text analysis and AI chat.

## Project Structure

```
IGB-ai/
├── frontend/          # React Native iOS app
│   ├── App.js
│   ├── services/
│   ├── __tests__/
│   └── package.json
├── backend/           # Python Flask API
│   ├── app.py
│   ├── config.py
│   ├── tests/
│   ├── docs/
│   └── requirements.txt
└── README.md
```

## Features

- 📱 **React Native iOS App** - Modern mobile interface
- 🐍 **Flask Backend** - RESTful API server
- 🤖 **Gemini LLM Integration** - Google's Gemini AI for text analysis
- 📄 **File Upload** - Support for large text file uploads (txt, md, pdf, docx)
- 📊 **Text Analysis** - Multiple analysis types (general, summary, sentiment, keywords)
- 💬 **AI Chat** - Conversational interface with Gemini
- 🧪 **Testing** - Comprehensive test suites for frontend and backend
- 📚 **Documentation** - Complete API and integration documentation

## Quick Start

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   PORT=5000
   ```

4. Run the server:
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Run on iOS:
   ```bash
   npm run ios
   ```

**Note**: For iOS Simulator, the API URL is set to `http://localhost:5000`. For physical devices, update the API URL in `frontend/services/api.js` to use your computer's IP address.

## API Endpoints

- `GET /health` - Health check
- `POST /api/upload` - Upload text file
- `POST /api/analyze` - Analyze text with Gemini
- `POST /api/analyze-file` - Upload and analyze file
- `POST /api/chat` - Chat with Gemini AI

See [backend/docs/API_DOCUMENTATION.md](backend/docs/API_DOCUMENTATION.md) for detailed API documentation.

## Testing

### Backend Tests
```bash
cd backend
python -m unittest discover tests
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Documentation

- [API Documentation](backend/docs/API_DOCUMENTATION.md) - Complete API reference
- [Chatbot Integration Guide](backend/docs/CHATBOT_GUIDE.md) - Guide for chatbot integration
- [Development Guide](backend/docs/DEVELOPMENT_GUIDE.md) - Development setup and guidelines
- [Backend README](backend/README.md) - Backend-specific documentation
- [Frontend README](frontend/README.md) - Frontend-specific documentation

## Environment Variables

### Backend
- `GEMINI_API_KEY` - Your Google Gemini API key (required)
- `PORT` - Server port (default: 5000)

### Frontend
Update `API_BASE_URL` in `frontend/services/api.js` for your environment.

## Technologies

- **Frontend**: React Native, Expo, React Native Paper
- **Backend**: Python, Flask, Flask-CORS
- **AI**: Google Gemini (Generative AI)
- **Testing**: Jest, React Testing Library, unittest

## License

This project is created for SB HACKS 2026.
