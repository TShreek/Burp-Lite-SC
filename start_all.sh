#!/bin/bash

echo "🔄 Starting backend server..."
python3 backend/server.py > logs/backend.log 2>&1 &

echo "🕵️‍♂️ Starting proxy server..."
python3 proxy.py > logs/proxy.log 2>&1 &

echo "📊 Starting UI dashboard server..."
python3 ui/server.py > logs/ui.log 2>&1 &

echo "✅ All components started in background. Check logs/ for output."
