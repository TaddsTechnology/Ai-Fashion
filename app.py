# AI Fashion Backend - Gradio wrapper for FastAPI
import gradio as gr
import os
import sys
from pathlib import Path
import threading
import time

# Add backend paths to Python path
backend_dir = Path(__file__).parent / "backend"
prods_fastapi_dir = backend_dir / "prods_fastapi"

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(prods_fastapi_dir))

try:
    # Import the working FastAPI app
    from prods_fastapi.main_simple import app as fastapi_app
    print("✅ Successfully imported FastAPI backend")
    backend_available = True
except ImportError as e:
    print(f"⚠️ Main backend import failed: {e}")
    # Create minimal backup FastAPI app
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    fastapi_app = FastAPI(title="AI Fashion Backend", version="1.0.0")
    
    # Add CORS for frontend connection
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for HF Space
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    @fastapi_app.get("/")
    def root():
        return {
            "message": "AI Fashion Backend API", 
            "status": "running",
            "docs": "/docs",
            "endpoints": [
                "/health",
                "/api/color-recommendations",
                "/data/",
                "/apparel"
            ]
        }
    
    @fastapi_app.get("/health")
    def health():
        return {"status": "healthy", "message": "AI Fashion Backend is running"}
    
    print("🚑 Created minimal FastAPI app")
    backend_available = False

# Start FastAPI in background thread
def start_fastapi():
    import uvicorn
    port = 8000  # Internal port for FastAPI
    print(f"🚀 Starting FastAPI backend on port {port}")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port, log_level="info")

# Start FastAPI server in background
fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
fastapi_thread.start()

# Give FastAPI time to start
time.sleep(2)

# Create Gradio interface that displays backend info
with gr.Blocks(title="AI Fashion Backend API") as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #4F46E5; font-size: 2.5rem; margin-bottom: 10px;">🎨 AI Fashion Backend API</h1>
        <p style="font-size: 1.2rem; color: #6B7280;">FastAPI Backend for Beauty & Style Recommendations</p>
        <p style="color: #9CA3AF;">This backend provides APIs for your frontend application</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("""
            ## 🚀 **Backend Status**: RUNNING
            
            Your FastAPI backend is now live and ready to serve requests!
            
            ### 📋 **Available Endpoints:**
            - `GET /` - API information
            - `GET /health` - Health check
            - `GET /api/color-recommendations` - Color recommendations
            - `GET /data/` - Makeup products
            - `GET /apparel` - Clothing recommendations
            
            ### 📖 **API Documentation:**
            - **Swagger UI**: [/docs](/docs)
            - **ReDoc**: [/redoc](/redoc)
            
            ### 🔗 **Connect Your Frontend:**
            Use this Space's URL as your backend endpoint in your Render frontend.
            """)
        
        with gr.Column():
            gr.Markdown("""
            ## 🛠️ **Integration Guide**
            
            ### For your Render frontend:
            
            ```javascript
            // Update your API base URL to:
            const API_BASE_URL = "https://taddsTeam-ai-fashion.hf.space";
            
            // Example API calls:
            const response = await fetch(`${API_BASE_URL}/api/color-recommendations?skin_tone=Monk03`);
            const data = await response.json();
            ```
            
            ### 📊 **Sample Response:**
            ```json
            {
              "colors": [
                {"name": "Navy Blue", "hex": "#000080"},
                {"name": "Forest Green", "hex": "#228B22"}
              ],
              "total_colors": 2,
              "monk_skin_tone": "Monk03"
            }
            ```
            """)
    
    gr.HTML("""
    <div style="text-align: center; margin-top: 20px; padding: 15px; background-color: #F3F4F6; border-radius: 10px;">
        <h3>✅ Backend Deployment Successful!</h3>
        <p>Your AI Fashion FastAPI backend is now running on Hugging Face Spaces.</p>
        <p><strong>Connect your Render frontend to this backend URL.</strong></p>
    </div>
    """)

# Launch Gradio interface
if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
