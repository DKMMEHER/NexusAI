#!/bin/bash

# Start all python services in the background
# We rely on existing environment variables or defaults used in code

echo "Starting Image Generation (8000)..."
python -m uvicorn ImageGeneration.backend:app --port 8000 &
sleep 2

echo "Starting Video Generation (8002)..."
python -m uvicorn VideoGeneration.backend:app --port 8002 &
sleep 2

echo "Starting Documents Summarization (8003)..."
python -m uvicorn DocumentsSummarization.backend:app --port 8003 &
sleep 2

echo "Starting YouTube Transcript (8004)..."
python -m uvicorn YoutubeTranscript.backend:app --port 8004 &
sleep 2

echo "Starting Chat (8005)..."
python -m uvicorn Chat.backend:app --port 8005 &
sleep 2

echo "Starting Director (8006)..."
python -m uvicorn Director.backend:app --port 8006 &
sleep 2

# Start Nginx (In Foreground to keep container alive)
echo "Starting Nginx..."
nginx -g "daemon off;"
