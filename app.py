# AI Fashion Backend - Pure FastAPI for HuggingFace
import os
import sys
from pathlib import Path

# Add backend paths to Python path
backend_dir = Path(__file__).parent / "backend"
prods_fastapi_dir = backend_dir / "prods_fastapi"

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(prods_fastapi_dir))

try:
    # Import the working FastAPI app
    from prods_fastapi.main_simple import app
    print("✅ Successfully imported FastAPI backend")
except ImportError as e:
    print(f"⚠️ Main backend import failed: {e}")
    # Create minimal backup FastAPI app
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(title="AI Fashion Backend API", version="1.0.0")
    
    # Add CORS for frontend connection
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://ai-fashion-5lho.onrender.com",
            "https://taddsteam-ai-fashion.hf.space",
            "http://localhost:3000",
            "http://localhost:5173"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def root():
        return {
            "message": "AI Fashion Backend API", 
            "status": "running",
            "docs": "/docs",
            "endpoints": [
                "/health",
                "/analyze-skin-tone",
                "/api/color-recommendations",
                "/data/",
                "/apparel"
            ]
        }
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "message": "AI Fashion Backend is running"}
    
    print("🚑 Created minimal FastAPI app")

# Launch FastAPI directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))  # HF default port
    print(f"🚀 Starting AI Fashion Backend on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
