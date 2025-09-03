#!/bin/bash

# Set Python path to include the app directory
export PYTHONPATH="/app:/app/prods_fastapi:$PYTHONPATH"

# Set unbuffered output
export PYTHONUNBUFFERED=1

# Change to the app directory
cd /app

# Create necessary directories if they don't exist
mkdir -p processed_data
mkdir -p prods_fastapi/data

# Print diagnostic information
echo "Python path: $PYTHONPATH"
echo "Current directory: $(pwd)"
echo "Available Python modules:"
python -c "import sys; print('\n'.join(sys.path))"

# Start the FastAPI application directly with uvicorn and proper port binding
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
