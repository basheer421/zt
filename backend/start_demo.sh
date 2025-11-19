#!/bin/bash
# Quick start script for presentation demo

echo "=================================="
echo "🚀 ZT-Verify Presentation Demo"
echo "=================================="
echo ""

# Check if in backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Run this script from the backend directory"
    echo "   cd backend && ./start_demo.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Create it first: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../.venv/bin/activate

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Server already running on port 8000"
    echo ""
    read -p "Kill existing server and restart? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "python.*main.py"
        sleep 2
    else
        echo "✅ Using existing server"
        echo ""
        echo "📖 Open in browser:"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "🎯 Run demo:"
        echo "   python presentation_demo.py"
        exit 0
    fi
fi

# Start backend server
echo ""
echo "🚀 Starting backend server..."
python main.py > server.log 2>&1 &
BACKEND_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
for i in {1..10}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Check if server started successfully
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "❌ Failed to start server"
    echo "Check server.log for errors"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ Backend Server Started!"
echo "=================================="
echo ""
echo "📊 Server Info:"
echo "   PID: $BACKEND_PID"
echo "   URL: http://localhost:8000"
echo "   Logs: server.log"
echo ""
echo "=================================="
echo "🎯 Choose Your Demo Method:"
echo "=================================="
echo ""
echo "1️⃣  Automated Python Demo (Recommended)"
echo "   python presentation_demo.py"
echo ""
echo "2️⃣  Manual API Testing"
echo "   Open: http://localhost:8000/docs"
echo "   Use test cases from PRESENTATION_TESTING_GUIDE.md"
echo ""
echo "3️⃣  Command Line (curl)"
echo "   See PRESENTATION_TESTING_GUIDE.md for examples"
echo ""
echo "=================================="
echo "⏹️  Stop Server:"
echo "   kill $BACKEND_PID"
echo "   OR: pkill -f 'python.*main.py'"
echo "=================================="
echo ""

# Save PID for later
echo $BACKEND_PID > .demo_server.pid
echo "💾 Server PID saved to .demo_server.pid"
echo ""
