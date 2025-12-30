#!/bin/bash
# Start script for Director service on Cloud Run
# This runs Nginx (frontend) and Director backend only

set -e

echo "Starting Director backend on port 8006..."
python -m uvicorn Director.backend:app --host 127.0.0.1 --port 8006 &

# Wait for backend to start
sleep 3

echo "Starting Nginx on port 8080..."
# Nginx will serve frontend and proxy /director/* to localhost:8006
nginx -g "daemon off;"
