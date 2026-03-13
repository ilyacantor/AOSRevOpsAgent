#!/bin/bash
# Production start script for Pipeline Health Monitor
# Builds frontend and starts FastAPI server

echo "🚀 Starting Pipeline Health Monitor..."

# Build frontend if not already built
if [ ! -d "frontend/dist" ]; then
    echo "📦 Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "✅ Frontend built successfully"
else
    echo "✅ Frontend already built (frontend/dist exists)"
fi

# Start FastAPI server
echo "🌐 Starting FastAPI server..."
uvicorn api:app --host 0.0.0.0 --port ${PORT:-5000}
