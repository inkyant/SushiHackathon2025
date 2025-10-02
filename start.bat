@echo off
REM AI-Powered Boat Monitoring System - Demo Launcher for Windows

echo ================================================================
echo    AI-POWERED BOAT MONITORING SYSTEM - DEMO SETUP
echo ================================================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Node.js is not installed. Please install Node.js first.
    echo   Visit: https://nodejs.org/
    pause
    exit /b 1
)

echo ✓ Node.js detected
echo.

REM Install dependencies if needed
if not exist "node_modules\" (
    echo Installing server dependencies...
    call npm install --silent
)

if not exist "client\node_modules\" (
    echo Installing client dependencies...
    cd client
    call npm install --silent
    cd ..
)

echo.
echo ================================================================
echo           LAUNCHING BOAT MONITORING SYSTEM
echo ================================================================
echo.
echo Starting WebSocket server for real-time sensor data...
echo Initializing AI anomaly detection...
echo Activating fish detection system...
echo.
echo ----------------------------------------------------------------
echo.
echo    Dashboard will open at: http://localhost:3000
echo    Server running on: http://localhost:3001
echo.
echo    Press Ctrl+C to stop the demo
echo.
echo ----------------------------------------------------------------
echo.

REM Start the server and client concurrently
call npm run dev
