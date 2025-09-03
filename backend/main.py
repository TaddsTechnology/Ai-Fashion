# Main entry point for AI Fashion Backend
import os
import sys
import logging

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prods_fastapi'))

def create_emergency_app():
    """Create a minimal FastAPI app for emergency deployment"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    emergency_app = FastAPI(
        title="AI Fashion Emergency Server",
        version="1.0.0",
        description="Emergency fallback server"
    )
    
    # Add CORS middleware
    emergency_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Temporarily allow all origins for emergency mode
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    
    @emergency_app.get("/")
    def root():
        return {
            "message": "AI Fashion Backend Emergency Server", 
            "status": "running",
            "port": int(os.getenv("PORT", 10000))
        }
    
    @emergency_app.get("/health")
    def health():
        return {
            "status": "healthy", 
            "message": "Emergency server is running",
            "port": int(os.getenv("PORT", 10000)),
            "host": "0.0.0.0"
        }
    
    @emergency_app.get("/api/test")
    def api_test():
        return {
            "message": "Emergency API endpoint working",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    
    return emergency_app

# Try to import apps in order of preference
app = None

try:
    # Try to import the main production app
    logger.info("Attempting to import main production app...")
    from prods_fastapi.main import app
    logger.info("✅ Successfully imported main production app")
except Exception as e:
    logger.warning(f"⚠️ Main app import failed: {e}")
    try:
        # Try to import simplified version
        logger.info("Attempting to import simplified app...")
        from prods_fastapi.main_simple import app
        logger.info("✅ Successfully imported simplified app")
    except Exception as e2:
        logger.warning(f"⚠️ Simplified app import failed: {e2}")
        try:
            # Try fallback version
            logger.info("Attempting to import fallback app...")
            from prods_fastapi.main_fallback import app
            logger.info("✅ Successfully imported fallback app")
        except Exception as e3:
            logger.error(f"❌ All app imports failed. Creating emergency app. Errors: Main={e}, Simple={e2}, Fallback={e3}")
            app = create_emergency_app()
            logger.info("🚑 Created emergency app")

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment with validation
    try:
        port = int(os.getenv("PORT", 10000))
        if port <= 0 or port > 65535:
            logger.warning(f"Invalid port {port}, using default 10000")
            port = 10000
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing PORT environment variable: {e}, using default 10000")
        port = 10000
    
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting AI Fashion Backend on {host}:{port}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Debug mode: {os.getenv('DEBUG', 'false').lower() == 'true'}")
    
    try:
        # Start the server with explicit configuration for Render
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            log_level="info",
            access_log=True,
            loop="asyncio"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
