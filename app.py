# AI Fashion Backend - Pure FastAPI for HuggingFace
import os
import sys
from pathlib import Path

# Add backend paths to Python path
backend_dir = Path(__file__).parent / "backend"
prods_fastapi_dir = backend_dir / "prods_fastapi"

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(prods_fastapi_dir))

# Set environment variables for proper operation
os.environ.setdefault("ENV", "production")
os.environ.setdefault("DATABASE_URL", "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

# Import the comprehensive FastAPI app with full functionality
try:
    from prods_fastapi.main import app
    print("✅ Successfully imported comprehensive FastAPI backend from prods_fastapi.main")
except ImportError as e:
    print(f"⚠️ Main import failed: {e}, trying fallback to main_simple")
    try:
        from prods_fastapi.main_simple import app
        print("✅ Successfully imported fallback FastAPI backend from prods_fastapi.main_simple")
    except ImportError as e2:
        print(f"⚠️ All imports failed: {e2}, creating minimal backup")
        # Create working backup FastAPI app with analyze-skin-tone
        from fastapi import FastAPI, File, UploadFile, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from PIL import Image
        import numpy as np
        import io
        from webcolors import hex_to_rgb, rgb_to_hex
        
        app = FastAPI(title="AI Fashion Backend API", version="1.0.0")
        
        # Add CORS for frontend connection
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://ai-fashion-5lho.onrender.com",
                "https://taddsteam-ai-fashion.hf.space",
                "http://localhost:3000",
                "http://localhost:5173",
                "*"  # Allow all origins for Hugging Face
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
        
        # Minimal Monk skin tones for backup
        MONK_TONES = {
            'Monk 1': '#f6ede4','Monk 2': '#f3e7db','Monk 3': '#f7ead0','Monk 4': '#eadaba','Monk 5': '#d7bd96',
            'Monk 6': '#a07e56','Monk 7': '#825c43','Monk 8': '#604134','Monk 9': '#3a312a','Monk 10': '#292420'
        }
        
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
        
        @app.post("/analyze-skin-tone")
        async def analyze_skin_tone_backup(file: UploadFile = File(...)):
            """Working analyze-skin-tone endpoint for Hugging Face deployment"""
            try:
                if not file.content_type.startswith("image/"):
                    raise HTTPException(status_code=400, detail="File must be an image")
                
                # Read and process image
                image_data = await file.read()
                image = Image.open(io.BytesIO(image_data)).convert("RGB")
                image_array = np.array(image)
                
                # Get center region for analysis
                h, w = image_array.shape[:2]
                center = image_array[h//4:3*h//4, w//4:3*w//4]
                avg_color = np.mean(center.reshape(-1, 3), axis=0)
                
                # Find closest Monk tone
                closest = "Monk 5"
                min_distance = float('inf')
                
                for name, hex_color in MONK_TONES.items():
                    r, g, b = hex_to_rgb(hex_color)
                    distance = np.sqrt(((avg_color[0]-r)**2) + ((avg_color[1]-g)**2) + ((avg_color[2]-b)**2))
                    if distance < min_distance:
                        min_distance = distance
                        closest = name
                
                # Format response
                monk_num = closest.split()[1]
                monk_id = f"Monk{int(monk_num):02d}"
                
                try:
                    derived_hex = rgb_to_hex((int(avg_color[0]), int(avg_color[1]), int(avg_color[2])))
                except:
                    derived_hex = MONK_TONES[closest]
                
                return {
                    "monk_skin_tone": monk_id,
                    "monk_tone_display": closest,
                    "monk_hex": MONK_TONES[closest],
                    "derived_hex_code": derived_hex,
                    "dominant_rgb": [int(avg_color[0]), int(avg_color[1]), int(avg_color[2])],
                    "confidence": 0.8,
                    "success": True
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")
        
        @app.get("/data/")
        def get_data_backup():
            return {"data": [], "message": "Backup endpoint - full backend not loaded"}
        
        @app.get("/apparel")
        def get_apparel_backup():
            return {"data": [], "message": "Backup endpoint - full backend not loaded"}
        
        @app.get("/api/color-recommendations")
        def get_color_recommendations_backup():
            return {"colors": [], "message": "Backup endpoint - full backend not loaded"}
        
        print("🚑 Created backup FastAPI app with working analyze-skin-tone endpoint")

# Launch FastAPI directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))  # HF default port
    print(f"🚀 Starting AI Fashion Backend on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
