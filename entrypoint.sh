#!/bin/bash

set -e

echo "Updating the database with Alembic..."
alembic upgrade head

echo "Starting the FastAPI application..."
uvicorn src.app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --loop uvloop \
  --http httptools \
  --timeout-keep-alive 5 \
  --limit-concurrency 1000 \
  --backlog 2048 \
  --no-access-log