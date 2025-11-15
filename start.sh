#!/bin/bash
# Quick start script for Binder Backend

echo "🚀 Starting Binder Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one from .env.example"
    echo "   cp .env.example .env"
    exit 1
fi

# Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "✅ Starting Django development server..."
echo "   Server will be available at http://localhost:8000"
echo "   API docs at http://localhost:8000/api/docs/"
python manage.py runserver

