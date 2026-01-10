# IGB AI - React Native Frontend

React Native iOS app for text analysis and AI chat using Gemini LLM.

## Setup

1. Install dependencies:
```bash
npm install
```

2. For iOS development, you'll need:
   - Xcode installed
   - CocoaPods installed
   - iOS Simulator or physical device

3. Start the development server:
```bash
npm start
```

4. Run on iOS:
```bash
npm run ios
```

## Configuration

Update the `API_BASE_URL` in `services/api.js` to point to your backend server.

For iOS Simulator, use `http://localhost:5000`
For physical device, use your computer's IP address: `http://192.168.x.x:5000`

## Features

- Text analysis with multiple analysis types (general, summary, sentiment, keywords)
- File upload and analysis
- Chat interface with Gemini AI
- Modern Material Design UI

## Testing

Run tests:
```bash
npm test
```

## Building for Production

For iOS:
```bash
expo build:ios
```

