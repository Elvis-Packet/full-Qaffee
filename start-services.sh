#!/bin/bash

# Qaffee Services Startup Script
echo "🚀 Starting Qaffee Services..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

# Check if ports are available
echo "🔍 Checking port availability..."
check_port 5000 || exit 1
check_port 8080 || exit 1

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend (Flask) on port 5000..."
    cd "Qaffee-backend"
    python app.py &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend (React) on port 8080..."
    cd "Qaffee-frontend"
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 3  # Give backend time to start

start_frontend
sleep 5  # Give frontend time to start

echo ""
echo "🎉 Services are starting up!"
echo "📱 Frontend: http://localhost:8080"
echo "🔧 Backend API: http://127.0.0.1:5000"
echo "📚 API Docs: http://127.0.0.1:5000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait 