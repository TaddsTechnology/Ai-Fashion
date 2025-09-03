# Use Python 3.11 full image for better OpenCV compatibility
FROM python:3.11

# Set environment variables to avoid OpenGL issues
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    MPLCONFIGDIR=/tmp/matplotlib \
    FONTCONFIG_PATH=/tmp/fontconfig \
    FONTCONFIG_FILE=/tmp/fontconfig/fonts.conf \
    XDG_CACHE_HOME=/tmp \
    QT_QPA_PLATFORM=offscreen \
    DISPLAY=:99 \
    OPENCV_LOG_LEVEL=ERROR

# Set work directory
WORKDIR /app

# Install minimal system dependencies including OpenCV requirements
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create directories for data and logs
RUN mkdir -p /app/logs /app/data /tmp/fontconfig

# Set proper permissions
RUN chmod -R 755 /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check - use PORT env var with fallback to 10000 (Render's default)
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Expose port - Render uses PORT env var, default to 10000
EXPOSE ${PORT:-10000}

# Command to run the application - use PORT environment variable with Render's default
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1"]
