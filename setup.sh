#!/bin/bash

# EngAI RAG Setup Script

echo "🚀 Setting up EngAI RAG..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p cache logs raw/kfws raw/sanierung raw/berechnungen raw/muster

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before running the server."
fi

# Create cache directory
mkdir -p cache/query_cache

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your OpenRouter API key"
echo "2. Add KfW documents to the raw/ directory"
echo "3. Install CLI: pip install -e ."
echo "4. Run: engaichat status"
echo "5. Run: uvicorn api.main:app --reload"
echo ""