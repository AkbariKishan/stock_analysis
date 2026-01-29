#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p) 2>/dev/null
}

trap cleanup EXIT

echo "Starting StockMind AI..."

# Start Backend
echo "Starting Backend Server (FastAPI)..."
source venv/bin/activate
uvicorn server.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 2

# Start Frontend
echo "Starting Frontend Client (Vite)..."
cd client
npm run dev

# Wait for both
wait
