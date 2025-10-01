#!/bin/bash

# Garudaco Startup Script

echo "🚀 Starting Garudaco Learning Platform..."
echo ""

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f "./.env" ]; then
    echo "⚠️  Warning: No .env file found in the root directory."
    echo "   The application will use mock responses instead of real AI."
    echo "   To use real AI, create .env file with your OpenRouter API key:"
    echo "   OPENAI_API_KEY=sk-or-v1-your-actual-api-key-here"
    echo ""
    echo "   Get your API key from: https://openrouter.ai/"
    echo ""
fi

# Start the application
echo "🔧 Building and starting containers..."
docker-compose up --build

echo ""
echo "✅ Garudaco is now running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:5000"
echo ""
echo "To stop the application, press Ctrl+C"