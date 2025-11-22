#!/bin/bash
# Build script for production deployment (Render/OLS)

echo "🔨 Building Binder Backend for production..."

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build complete!"

