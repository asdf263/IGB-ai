#!/bin/bash

echo "🚀 Setting up IGB AI project..."

# Backend setup
echo "📦 Setting up backend..."
cd backend
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please update backend/.env with your GEMINI_API_KEY"
fi

if command -v pip3 &> /dev/null; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
else
    echo "⚠️  pip3 not found. Please install Python dependencies manually:"
    echo "   cd backend && pip install -r requirements.txt"
fi
cd ..

# Frontend setup
echo "📱 Setting up frontend..."
cd frontend
if command -v npm &> /dev/null; then
    echo "Installing Node dependencies..."
    npm install
else
    echo "⚠️  npm not found. Please install Node.js and run:"
    echo "   cd frontend && npm install"
fi
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your GEMINI_API_KEY"
echo "2. Start backend: cd backend && python app.py"
echo "3. Start frontend: cd frontend && npm start"
echo "4. Run on iOS: cd frontend && npm run ios"

