#!/bin/bash
echo "Stopping any existing Ngrok sessions..."
pkill -f ngrok || true

echo "Configuring Ngrok authtoken..."
ngrok config add-authtoken 2zJhR03rrVQY1IZMPbLfa2ijZ50_4h39aTFnL9JbnhWZ5YpLd

echo "Starting Ngrok tunnel for port 5001..."
echo "NOTE: If you see a 403 or warning page, add the header 'ngrok-skip-browser-warning: true' to your request."
ngrok http 5001
