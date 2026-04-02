#!/bin/bash
set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Function to clean up background processes on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    if [ -n "$DJANGO_PID" ]; then
        echo "  → Stopping Django server (PID $DJANGO_PID)..."
        kill "$DJANGO_PID" 2>/dev/null || true
        wait "$DJANGO_PID" 2>/dev/null || true
    fi
    if [ -n "$NPM_PID" ]; then
        echo "  → Stopping npm dev server (PID $NPM_PID)..."
        kill "$NPM_PID" 2>/dev/null || true
        wait "$NPM_PID" 2>/dev/null || true
    fi
    echo "Done."
    exit 0
}
trap cleanup INT TERM

# Default ports (can be overridden by .env)
DJANGO_PORT=${DJANGO_PORT:-8000}
DJANGO_VITE_SERVER_PORT=${DJANGO_VITE_SERVER_PORT:-5173}

# Start servers
echo "🚀 Starting development environment..."
echo "   Django → http://localhost:$DJANGO_PORT"
echo "   Vite   → http://localhost:$DJANGO_VITE_SERVER_PORT"
echo ""
uv run manage.py runserver "$DJANGO_PORT" &
DJANGO_PID=$!
npm run dev &
NPM_PID=$!
wait
