#!/bin/bash
echo "Starting IGB AI Development Environment..."

# Check if MongoDB is accessible (optional check)
if command -v mongosh &> /dev/null; then
    if mongosh --eval "db.version()" &> /dev/null; then
        echo "✅ MongoDB is running"
    else
        echo "⚠️  MongoDB may not be running (continuing anyway...)"
    fi
else
    echo "ℹ️  MongoDB client not found (skipping check)"
fi

# Start backend
echo "🚀 Starting backend on port 5000..."
cd backend
python app_vectors.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:5000"
else
    echo "⚠️  Backend may not be ready yet (check manually)"
fi

# Start frontend
echo "🚀 Starting frontend..."
cd frontend
npx expo start

# Cleanup on exit
trap "echo 'Stopping backend...'; kill $BACKEND_PID 2>/dev/null; exit" EXIT INT TERM
