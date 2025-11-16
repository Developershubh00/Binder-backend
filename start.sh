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

# Ensure .env exists, create from template if missing
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "🧪 Creating .env from .env.example..."
        cp .env.example .env
    else
        echo "⚠️  .env file not found and .env.example missing."
        echo "   Proceeding with built-in defaults (SQLite, DEBUG=True)."
    fi
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

