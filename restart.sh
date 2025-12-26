#!/bin/bash

echo "🔄 Restarting server..."

# Kill any existing Flask servers
pkill -f "python.*app.py"

sleep 1

echo "🚀 Starting fresh server..."
python3 app.py


