#!/bin/bash

# Production startup script for News AI Backend
# This script starts the application using Gunicorn + Uvicorn

set -e

echo "🚀 Starting News AI Backend in Production Mode"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Set default values if not set
export ENVIRONMENT=${ENVIRONMENT:-production}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-4}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo "📋 Configuration:"
echo "   Environment: $ENVIRONMENT"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Workers: $WORKERS"
echo "   Log Level: $LOG_LEVEL"

# Start Gunicorn
echo "🔄 Starting Gunicorn server..."
exec gunicorn \
    --config gunicorn.conf.py \
    app.api.main:app