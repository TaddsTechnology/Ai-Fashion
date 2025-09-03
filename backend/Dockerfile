# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    python3-opencv \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with timeout and retry settings
RUN pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt

# Copy the entire backend directory
COPY . .

# Create necessary directories
RUN mkdir -p processed_data prods_fastapi/data

# Expose port (will be overridden by PORT env var)
EXPOSE 10000

# Copy entrypoint script and set permissions
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && \
    # Convert Windows line endings to Unix
    sed -i 's/\r$//' /app/entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app:/app/prods_fastapi
ENV PYTHONUNBUFFERED=1

# Health check endpoint (use PORT environment variable with fallback to 10000)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
