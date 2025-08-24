#!/bin/bash

# Get port from environment variable or default to 8000
PORT=${PORT:-8000}

echo "Starting NetOps AI Pipeline on port $PORT"

# Start the FastAPI application
uvicorn app:app --host 0.0.0.0 --port $PORT
