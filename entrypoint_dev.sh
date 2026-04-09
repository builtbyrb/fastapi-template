#!/bin/bash

set -e

echo "Updating the database with Alembic..."
alembic upgrade head

echo "Starting the FastAPI application..."
fastapi dev src/app.py --host 0.0.0.0 --port 8000