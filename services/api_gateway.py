# API Gateway (Port 8000)
# Routes requests to appropriate microservices

from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import httpx
import os
from typing import Optional

app = FastAPI(
    title="AI Fashion API Gateway", 
    version="1.0.0",
    description="Gateway routing requests to AI Fashion microservices"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://app.taddstechnology.com",
        "https://ai-fashion-5lho.onrender.com",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Service URLs
DETECTION_SERVICE_URL = os.getenv("DETECTION_SERVICE_URL", "http://localhost:8001")
PALETTE_SERVICE_URL = os.getenv("PALETTE_SERVICE_URL", "http://localhost:8002")
RECOMMENDATION_SERVICE_URL = os.getenv("RECOMMENDATION_SERVICE_URL", "http://localhost:8003")

@app.get("/")
def root():
    return {
        "service": "AI Fashion API Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "detection": f"{DETECTION_SERVICE_URL}",
            "palette": f"{PALETTE_SERVICE_URL}",
            "recommendation": f"{RECOMMENDATION_SERVICE_URL}"
        }
    }

@app.get("/health")
async def health():
    """Gateway health check - also checks microservices"""
    services_status = {}
    overall_healthy = True
    
    services = {
        "detection": DETECTION_SERVICE_URL,
        "palette": PALETTE_SERVICE_URL,
        "recommendation": RECOMMENDATION_SERVICE_URL
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in services.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                services_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_url
                }
            except Exception as e:
                services_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "url": service_url
                }
                overall_healthy = False
    
    return {
        "gateway_status": "healthy",
        "overall_status": "healthy" if overall_healthy else "degraded",
        "services": services_status
    }

# === DETECTION SERVICE ROUTES ===

@app.post("/analyze-skin-tone")
async def analyze_skin_tone(file: UploadFile = File(...)):
    """Route to Detection Service for skin tone analysis"""
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(
                f"{DETECTION_SERVICE_URL}/analyze_photo",
                files=files,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Detection service error: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Detection service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

# === PALETTE SERVICE ROUTES ===

@app.get("/api/color-palettes")
async def get_color_palettes(
    season: str,
    contrast: str = "medium",
    occasion: Optional[str] = None
):
    """Route to Palette Service for color palettes"""
    try:
        async with httpx.AsyncClient() as client:
            params = {"season": season, "contrast": contrast}
            if occasion:
                params["occasion"] = occasion
                
            response = await client.get(
                f"{PALETTE_SERVICE_URL}/get_palette",
                params=params,
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Palette service error: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Palette service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

@app.get("/api/contrast-colors")
async def get_contrast_colors(season: str, contrast_level: str = "medium"):
    """Route to Palette Service for contrast-specific colors"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PALETTE_SERVICE_URL}/get_contrast_colors",
                params={"season": season, "contrast_level": contrast_level},
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Palette service error: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Palette service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

# === RECOMMENDATION SERVICE ROUTES ===

@app.post("/api/recommendations")
async def get_recommendations(
    season: str,
    undertone: str,
    contrast: str,
    occasion: str = "casual",
    gender: str = "Unisex",
    budget_min: float = 0,
    budget_max: float = 1000,
    outfit_categories: str = "tops,bottoms,dresses",
    makeup_categories: str = "foundation,lipstick,eyeshadow"
):
    """Route to Recommendation Service for product recommendations"""
    try:
        async with httpx.AsyncClient() as client:
            params = {
                "season": season,
                "undertone": undertone,
                "contrast": contrast,
                "occasion": occasion,
                "gender": gender,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "outfit_categories": outfit_categories,
                "makeup_categories": makeup_categories
            }
            
            response = await client.post(
                f"{RECOMMENDATION_SERVICE_URL}/get_recommendations",
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Recommendation service error: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Recommendation service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

@app.get("/api/color-alternatives")
async def get_color_alternatives(
    original_color: str,
    season: str,
    limit: int = 5
):
    """Route to Recommendation Service for color alternatives"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RECOMMENDATION_SERVICE_URL}/color_alternatives",
                params={
                    "original_color": original_color,
                    "season": season,
                    "limit": limit
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Recommendation service error: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Recommendation service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

# === LEGACY ROUTES (for backward compatibility) ===

@app.get("/api/color-recommendations")
async def legacy_color_recommendations(skin_tone: str):
    """Legacy route - redirects to new palette service"""
    try:
        # Map legacy skin_tone to season
        season_mapping = {
            "Monk01": "Light Spring", "Monk02": "Light Spring", "Monk03": "Clear Spring",
            "Monk04": "Warm Spring", "Monk05": "Soft Autumn", "Monk06": "Warm Autumn",
            "Monk07": "Deep Autumn", "Monk08": "Deep Winter", "Monk09": "Cool Winter",
            "Monk10": "Clear Winter"
        }
        
        season = season_mapping.get(skin_tone, "Soft Autumn")
        
        # Get palette from service
        palette_response = await get_color_palettes(season, "medium")
        
        # Format for legacy compatibility
        colors = palette_response.get("colors", [])
        return {
            "colors_that_suit": [{"name": c["name"], "hex": c["hex"]} for c in colors[:10]],
            "seasonal_type": season,
            "monk_skin_tone": skin_tone
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Legacy route error: {str(e)}")

@app.get("/data/")
async def legacy_data():
    """Legacy data endpoint - returns empty for now"""
    return {"data": [], "message": "Use /api/recommendations for product data"}

@app.get("/apparel")
async def legacy_apparel():
    """Legacy apparel endpoint - returns empty for now"""
    return {"data": [], "message": "Use /api/recommendations for apparel data"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
