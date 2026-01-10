# IGB AI - Installation & Run Instructions

## Overview

IGB AI is a behavior vector extraction system that analyzes chat logs to produce ~200 dimensional feature vectors for personality and communication pattern analysis.

## Technology Stack

### Backend
- **FastAPI** - High-performance async API framework
- **spaCy** - NLP pipeline for linguistic analysis
- **HuggingFace Transformers** - Semantic embeddings
- **scikit-learn + XGBoost** - ML clustering and classification
- **ChromaDB** - Vector storage
- **Redis** - Caching layer
- **Ray** - Parallel processing

### Frontend (Web)
- **React + Vite** - Modern web framework
- **Plotly.js** - Interactive charts
- **Cytoscape.js** - Graph visualization
- **TailwindCSS** - Styling

### Frontend (Mobile)
- **React Native + Expo** - Cross-platform mobile

## Architecture

```
IGB-ai/
├── backend/                    # FastAPI server
│   ├── main.py                 # FastAPI app with all routes
│   ├── app_vectors.py          # Legacy Flask API
│   ├── services/               # Core services
│   │   ├── feature_extractor.py
│   │   ├── synthetic_generator.py
│   │   ├── clustering_service.py
│   │   ├── visualization_service.py
│   │   ├── vector_store_chroma.py  # ChromaDB storage
│   │   ├── cache_service.py        # Redis caching
│   │   └── features/               # Feature extraction modules
│   │       ├── temporal_features.py
│   │       ├── text_features.py
│   │       ├── linguistic_features_spacy.py  # spaCy NLP
│   │       ├── semantic_features_hf.py       # HuggingFace
│   │       ├── sentiment_features.py
│   │       ├── behavioral_features.py
│   │       ├── graph_features.py
│   │       └── composite_features.py
│   └── requirements.txt
├── web/                        # React web frontend
│   ├── src/
│   │   ├── pages/              # Page components
│   │   ├── store/              # Zustand state
│   │   └── services/           # API client
│   └── package.json
├── frontend/                   # React Native mobile app
│   ├── src/
│   │   ├── screens/            # App screens
│   │   ├── context/            # Global state
│   │   └── services/           # API client
│   └── package.json
└── shared/                     # Shared schemas & examples
    ├── schemas/
    └── examples/
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **npm or yarn**
- **Redis** (optional, for caching)
- **Expo CLI** (for React Native mobile)

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows (PowerShell)
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 3. Environment Variables

Create `.env` file in `backend/`:

```env
PORT=8000
REDIS_URL=redis://localhost:6379  # Optional
GEMINI_API_KEY=your_gemini_api_key_here  # Optional
OPENAI_API_KEY=your_openai_api_key_here  # Optional
```

### 4. Run Backend Server

```bash
# Run FastAPI server (recommended)
python main.py
# Or with uvicorn directly
uvicorn main:app --reload --port 8000

# Legacy Flask server
python app_vectors.py
```

Server starts at `http://localhost:8000`

### 5. Verify Backend

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "IGB-AI Vector API",
  "feature_count": 160,
  "stored_vectors": 0
}
```

## Web Frontend Setup (React + Vite)

### 1. Install Dependencies

```bash
cd web
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Web app starts at `http://localhost:3000`

## Mobile Frontend Setup (React Native)

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

Edit `src/services/vectorApi.js` if needed:

```javascript
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'  // Development
  : 'https://your-production-api.com';  // Production
```

### 3. Run Mobile App

```bash
# Start Expo development server
npm start

# Or run on specific platform
npm run android
npm run ios
npm run web
```

## API Endpoints

### Feature Extraction

**POST `/api/features/extract`**

Extract behavior vector from chat messages.

```bash
curl -X POST http://localhost:5000/api/features/extract \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"sender": "user", "text": "Hello!", "timestamp": 1715234000},
      {"sender": "bot", "text": "Hi there!", "timestamp": 1715234012}
    ],
    "store": true
  }'
```

### Synthetic Generation

**POST `/api/features/synthetic-generate`**

Generate synthetic behavior vectors.

```bash
curl -X POST http://localhost:5000/api/features/synthetic-generate \
  -H "Content-Type: application/json" \
  -d '{
    "n_synthetic": 10,
    "method": "smote"
  }'
```

Methods: `smote`, `noise`, `jitter`, `interpolate`, `adasyn`

### Vector Management

**GET `/api/vectors/list`** - List all stored vectors

**GET `/api/vectors/<id>`** - Get specific vector

**DELETE `/api/vectors/<id>`** - Delete vector

### Clustering

**POST `/api/vectors/cluster`**

```bash
curl -X POST http://localhost:5000/api/vectors/cluster \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_method": "kmeans",
    "reduce_method": "pca",
    "n_clusters": 5
  }'
```

### Visualization

**GET `/api/visualization/graph`** - Get cluster graph data

**POST `/api/visualization/heatmap`** - Get feature heatmap

**POST `/api/visualization/radar`** - Get radar chart data

## Feature Categories (~160 features)

| Category | Count | Description |
|----------|-------|-------------|
| Temporal | 20 | Response latency, burstiness, circadian patterns |
| Text | 25 | Message length, lexical richness, entropy |
| Linguistic | 30 | POS ratios, tense, formality, readability |
| Semantic | 25 | Embedding stats, coherence, topic diversity |
| Sentiment | 20 | Polarity, emotions, volatility |
| Behavioral | 25 | Engagement, politeness, assertiveness |
| Graph | 10 | Social network metrics |
| Composite | 15 | Derived indices (social energy, EQ proxy) |

## Input Format

```json
{
  "messages": [
    {
      "sender": "user",
      "text": "Message content",
      "timestamp": 1715234000
    }
  ]
}
```

## Output Format

```json
{
  "success": true,
  "vector": [0.1, 0.2, ...],
  "feature_labels": ["temporal_avg_response_latency", ...],
  "feature_count": 160,
  "categories": {
    "temporal": {...},
    "text": {...}
  },
  "vector_id": "vec_abc123_2024-01-01"
}
```

## Troubleshooting

### Backend Issues

1. **ModuleNotFoundError**: Ensure virtual environment is activated
2. **Port in use**: Change PORT in `.env`
3. **Slow first request**: sentence-transformers downloads model on first use

### Frontend Issues

1. **Network error**: Ensure backend is running and URL is correct
2. **Metro bundler issues**: Clear cache with `expo start -c`

## Development

### Running Tests

```bash
# Backend
cd backend
python -m pytest tests/

# Frontend
cd frontend
npm test
```

### Adding New Features

1. Create extractor in `backend/services/features/`
2. Add to `feature_extractor.py`
3. Update frontend screens as needed
