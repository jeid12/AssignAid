#!/bin/bash

# Activate virtual environment (if necessary)
# source .venv/bin/activate

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000
