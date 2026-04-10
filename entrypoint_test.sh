#!/bin/bash

set -e

echo "Updating the database with Alembic..."
alembic upgrade head

echo "Starting test..."
pytest --cov=src --cov-report html:cov_html -v