# AI Fashion FastAPI Backend for Hugging Face
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
    
    app = FastAPI(title="AI Fashion Backend", version="1.0.0")
    
    # Add CORS for frontend connection
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your Render frontend URL
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def root():
        return {
            "message": "AI Fashion Backend API", 
            "status": "running",
            "docs": "/docs"
        }
    
    @app.get("/health")
    def health():
        return {"status": "healthy"}
    
    print("🚑 Created minimal FastAPI app")

# For Hugging Face deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))  # HF default port
    uvicorn.run(app, host="0.0.0.0", port=port)
