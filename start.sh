#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

echo "========================================="
echo "   D&D NFC Campaign Tool - Startup       "
echo "========================================="

# Ask for password immediately so the browser doesn't steal focus later!
echo "[*] Please enter your password to grant USB access to the Flipper:"
sudo -v


# Clean up old Node.js files if they still exist
rm -rf server/package.json server/index.js server/node_modules server/package-lock.json 2>/dev/null

# 1. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "[*] Creating new Python virtual environment..."
    python3 -m venv venv
fi

echo "[*] Activating virtual environment..."
source venv/bin/activate

# 2. Install all dependencies for both Server and Bridge
echo "[*] Checking and installing dependencies..."
pip install --upgrade -q pip
pip install -q fastapi uvicorn[standard] pydantic websockets pyserial requests

# 3. Start the Server in the background
echo "[*] Starting FastAPI Server..."
cd server
python3 server.py &
SERVER_PID=$!

# Give the server a second to start
sleep 2 

# Automatically open the GM Dashboard in the default web browser
echo "[*] Opening GM Dashboard in your web browser..."
xdg-open http://localhost:3000 2>/dev/null &

# 4. Start the Flipper Bridge in the foreground
echo "[*] Starting Flipper NFC Bridge (requires sudo for USB permissions)..."
cd ../bridge
sudo ../venv/bin/python flipper_reader.py

# 5. Cleanup when you exit (Ctrl+C)
echo "[*] Shutting down Server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null
echo "Goodbye!"
