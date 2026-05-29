#!/bin/bash

# Healthcare Pre-Authorization Copilot - Startup Script (macOS/Linux)

echo ""
echo "======================================"
echo "Healthcare Pre-Auth Copilot Startup"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

echo "[OK] Python 3 is installed: $(python3 --version)"
echo "[OK] Node.js is installed: $(node --version)"
echo ""

# Start Backend
echo "[*] Starting FastAPI backend on port 8000..."
cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
    echo "[*] Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start Frontend
echo "[*] Starting Next.js frontend on port 3000..."
cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "[*] Installing Node dependencies..."
    npm install -q
fi

npm run dev &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo "Services started successfully!"
echo "======================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Handle cleanup on exit
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT TERM

wait
