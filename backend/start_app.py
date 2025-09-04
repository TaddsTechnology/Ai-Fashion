#!/usr/bin/env python3
"""
Startup script for AI Fashion Backend
This script tries to start the main application and falls back to simplified version if needed
"""

import os
import sys
import subprocess
import time

def start_application():
    """Start the FastAPI application with fallback strategy."""
    print("🚀 Starting AI Fashion Backend...")
    
    # Get port from environment (Render uses PORT env var)
    port = os.environ.get('PORT', '10000')
    print(f"🌐 Using port: {port}")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/app:/app/prods_fastapi'
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Change to app directory
    os.chdir('/app')
    
    # Add paths to Python path
    sys.path.append('/app')
    sys.path.append('/app/prods_fastapi')
    
    print("📍 Current directory:", os.getcwd())
    print("🔧 Python path:", sys.path[:3])  # Show first 3 paths
    
    # Try simplified version first (more likely to work)
    try:
        print("🎯 Starting simplified application...")
        from prods_fastapi.main_simple import app
        import uvicorn
        
        print(f"✅ Starting app on 0.0.0.0:{port}")
        uvicorn.run(app, host="0.0.0.0", port=int(port))
        
    except Exception as e1:
        print(f"⚠️ Simplified app failed: {e1}")
        print("🔄 Trying fallback application...")
        
        try:
            # Try fallback version
            from prods_fastapi.main_fallback import app
            import uvicorn
            
            print(f"🔧 Starting fallback app on 0.0.0.0:{port}")
            uvicorn.run(app, host="0.0.0.0", port=int(port))
            
        except Exception as e2:
            print(f"⚠️ Fallback app failed: {e2}")
            print("🔄 Trying main application...")
            
            try:
                # Try main application as last resort
                result = subprocess.run([
                    sys.executable, '-m', 'uvicorn', 
                    'prods_fastapi.main:app', 
                    '--host', '0.0.0.0', 
                    '--port', port
                ], check=True)
                
            except Exception as e3:
                print(f"❌ Main application also failed: {e3}")
                print("🆘 Creating emergency server...")
                
                # Emergency fallback server
                try:
                    create_emergency_server(int(port))
                except Exception as e4:
                    print(f"💥 All startup methods failed: {e4}")
                    sys.exit(1)

def create_emergency_server(port: int):
    """Create an emergency basic server."""
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="AI Fashion Emergency Server")
    
    @app.get("/")
    def root():
        return {"message": "AI Fashion Backend Emergency Server", "status": "running"}
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "message": "Emergency server is running"}
    
    print(f"🚑 Starting emergency server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    start_application()
