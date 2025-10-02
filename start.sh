#!/bin/bash

# AI-Powered Boat Monitoring System - Demo Launcher
# Single command to start the entire application

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🚤 AI-POWERED BOAT MONITORING SYSTEM - DEMO SETUP        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js detected: $(node --version)"
echo ""
# Ensure Flask and flask-cors are installed for Python components
if ! python -c "import flask" &> /dev/null; then
    echo "📦 Installing Flask for Python..."
    pip install flask
fi

if ! python -c "import flask_cors" &> /dev/null; then
    echo "📦 Installing flask-cors for Python..."
    pip install flask-cors
fi
# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing server dependencies..."
    npm install --silent
fi

if [ ! -d "client/node_modules" ]; then
    echo "📦 Installing client dependencies..."
    cd client && npm install --silent && cd ..
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🚀 LAUNCHING BOAT MONITORING SYSTEM           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📡 Starting WebSocket server for real-time sensor data..."
echo "🤖 Initializing AI anomaly detection..."
echo "🐟 Activating fish detection system..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   Dashboard will open at: http://localhost:3000"
echo "   Server running on: http://localhost:3001"
echo ""
echo "   Press Ctrl+C to stop the demo"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Flask LLM backend
echo "🧠 Starting Flask LLM backend on http://localhost:5000"
python -u ./llm_backbone/server.py &

# Start maintenance model helper (optional)
echo "🔧 Starting maintenance model helper"
python -u ./maintainance_model/run_maintainance.py &

# Start the Node server and React client concurrently
echo "🌐 Starting Node API/WebSocket server and React client"
npm run dev
