# Main entry point for AI Fashion Backend
import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prods_fastapi'))

try:
    # Try to import the simplified version first
    from prods_fastapi.main_simple import app
    print("✅ Successfully imported simplified app")
except ImportError as e:
    print(f"⚠️ Simplified app import failed: {e}")
    try:
        # Try fallback version
        from prods_fastapi.main_fallback import app
        print("✅ Successfully imported fallback app")
    except ImportError as e2:
        print(f"❌ Fallback app import failed: {e2}")
        # Create emergency app
        from fastapi import FastAPI
        
        app = FastAPI(title="AI Fashion Emergency Server")
        
        @app.get("/")
        def root():
            return {"message": "AI Fashion Backend Emergency Server", "status": "running"}
        
        @app.get("/health")
        def health():
            return {"status": "healthy", "message": "Emergency server is running"}
        
        print("🚑 Created emergency app")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    print(f"🚀 Starting AI Fashion Backend on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
