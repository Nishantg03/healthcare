@echo off
REM Healthcare Pre-Authorization Copilot - Startup Script (Windows)

echo.
echo ======================================
echo Healthcare Pre-Auth Copilot Startup
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    exit /b 1
)

echo [OK] Python is installed
echo [OK] Node.js is installed
echo.

REM Start Backend in a new window
echo [*] Starting FastAPI backend on port 8000...
start "Healthcare Backend" cmd /k ^
    cd /d "%~dp0\backend" ^& ^
    python -m venv venv 2>nul ^& ^
    call venv\Scripts\activate.bat ^& ^
    pip install -r requirements.txt >nul 2>&1 ^& ^
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

REM Wait a moment for backend to start
timeout /t 3

REM Start Frontend in a new window
echo [*] Starting Next.js frontend on port 3000...
start "Healthcare Frontend" cmd /k ^
    cd /d "%~dp0\frontend" ^& ^
    call npm install >nul 2>&1 ^& ^
    npm run dev

echo.
echo ======================================
echo Services are starting...
echo ======================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo Docs:     http://localhost:8000/docs
echo.
echo Press Ctrl+C in each window to stop services
echo.
