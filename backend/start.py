#!/usr/bin/env python3
"""
Simple startup script for AI Fashion Backend on Render
This script ensures the server binds to the correct port and host
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    
    # Get configuration from environment
    port = int(os.environ.get("PORT", 10000))
    host = "0.0.0.0"
    environment = os.environ.get("ENVIRONMENT", "production")
    
    logger.info(f"=== AI Fashion Backend Startup ===")
    logger.info(f"Environment: {environment}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(current_dir / "prods_fastapi"))
    
    logger.info(f"Python path: {sys.path[:3]}...")
    
    # Import requirements
    try:
        import uvicorn
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        logger.info("✅ Core dependencies imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import core dependencies: {e}")
        sys.exit(1)
    
    # Try to import the main app
    app = None
    
    try:
        # First try the main production app
        logger.info("Attempting to import main production app...")
        from prods_fastapi.main import app
        logger.info("✅ Successfully imported main production app")
    except Exception as e:
        logger.warning(f"⚠️ Failed to import main app: {e}")
        
        # Create a minimal working app
        logger.info("Creating minimal fallback app...")
        app = create_minimal_app()
        logger.info("✅ Created minimal fallback app")
    
    # Start the server
    try:
        logger.info(f"🚀 Starting server on {host}:{port}")
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            # Additional configuration for Render
            server_header=False,
            date_header=False
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

def create_minimal_app():
    """Create a minimal FastAPI application"""
    
    app = FastAPI(
        title="AI Fashion Backend",
        version="1.0.0",
        description="AI Fashion recommendation system"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def root():
        return {
            "message": "AI Fashion Backend is running",
            "status": "healthy",
            "version": "1.0.0",
            "environment": os.environ.get("ENVIRONMENT", "production")
        }
    
    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "message": "Service is running",
            "port": int(os.environ.get("PORT", 10000)),
            "host": "0.0.0.0"
        }
    
    @app.get("/api/test")
    def api_test():
        return {
            "message": "API is working",
            "timestamp": str(__import__('datetime').datetime.now()),
            "environment": os.environ.get("ENVIRONMENT", "production")
        }
    
    # Handle CORS preflight requests
    @app.options("/{path:path}")
    async def handle_options(path: str):
        return {"message": "OK"}
    
    logger.info("✅ Minimal app created with basic endpoints")
    return app

if __name__ == "__main__":
    main()
