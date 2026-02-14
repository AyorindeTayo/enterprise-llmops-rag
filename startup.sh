#!/bin/bash

# Enterprise LLMOps RAG Startup Script
# This script sets up and starts the entire system

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "================================================"
echo "🚀 Enterprise LLMOps RAG System Startup"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "llmops-env" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv llmops-env"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source llmops-env/bin/activate

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env.template <<EOF
# OpenAI Configuration
OPENAI_API_KEY=your-key-here

# System Configuration
USE_DEMO_MODE=true
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_PORT=8501
EOF
    echo "Please configure .env file with your API keys"
    echo ""
fi

# Install/update requirements
echo "📚 Checking dependencies..."
pip install -q -r requirements.txt 2>/dev/null || echo "Some dependencies may already be installed"

echo ""
echo "================================================"
echo "✓ System Ready"
echo "================================================"
echo ""
echo "📌 To start the system, run in separate terminals:"
echo ""
echo "  1️⃣  API Server (Backend):"
echo "     uvicorn api_gateway.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  2️⃣  Frontend (Streamlit):"
echo "     streamlit run frontend_streamlit/app.py --server.port 8501"
echo ""
echo "  3️⃣  (Optional) For automatic startup, use:"
echo "     python start.py"
echo ""
echo "📱 Access the Frontend:"
echo "   http://localhost:8501"
echo ""
echo "🔗 API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "================================================"
