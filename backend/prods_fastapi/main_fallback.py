# Fallback FastAPI application for Render deployment with simple imports
from fastapi import FastAPI, Query, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import asyncio
import base64
import uuid
from contextlib import asynccontextmanager

# Import simplified modules instead of complex ones
try:
    from prods_fastapi.simple_cache import cache_manager, cached, skin_tone_cache, warm_cache_skin_tones, warm_cache_color_palettes
    from prods_fastapi.simple_async_database import async_db_service, get_async_db, async_create_tables, async_init_color_palette_data, warm_async_caches
    from prods_fastapi.simple_background_tasks import (
        process_image_analysis_task, 
        generate_color_recommendations_task,
        generate_product_recommendations_task,
        warm_cache_task,
        cleanup_expired_cache_task,
        get_task_result,
        is_task_complete
    )
    from prods_fastapi.simple_monitoring import (
        performance_monitor, 
        health_check_manager,
        RequestMonitoringMiddleware,
        get_health_endpoint,
        get_metrics_endpoint,
        get_system_stats_endpoint,
        periodic_health_check,
        cleanup_old_metrics
    )
except ImportError as e:
    print(f"Import warning: {e}")
    # Create mock objects if imports fail
    class MockCacheManager:
        def get(self, key): return None
        def set(self, key, value, ttl=None): pass
    
    cache_manager = MockCacheManager()
    cached = lambda ttl=3600: lambda f: f
    skin_tone_cache = {}
    
    def warm_cache_skin_tones(): pass
    def warm_cache_color_palettes(): pass
    
    class MockAsyncDbService:
        async def close(self): pass
    
    async_db_service = MockAsyncDbService()
    
    async def get_async_db(): return None
    async def async_create_tables(): pass
    async def async_init_color_palette_data(): pass
    async def warm_async_caches(): pass
    
    def process_image_analysis_task(*args, **kwargs): pass
    def generate_color_recommendations_task(*args, **kwargs): pass
    def generate_product_recommendations_task(*args, **kwargs): pass
    
    class MockTask:
        def send(self, *args, **kwargs): pass
    
    warm_cache_task = MockTask()
    cleanup_expired_cache_task = MockTask()
    
    def get_task_result(task_id): return {"status": "completed"}
    def is_task_complete(task_id): return True
    
    performance_monitor = lambda *args, **kwargs: lambda f: f
    health_check_manager = None
    
    class RequestMonitoringMiddleware:
        async def __call__(self, request, call_next):
            return await call_next(request)
    
    async def get_health_endpoint(): return {"status": "healthy"}
    async def get_metrics_endpoint(): return {"requests": 0}
    async def get_system_stats_endpoint(): return {"uptime": "unknown"}
    async def periodic_health_check(): pass
    async def cleanup_old_metrics(): pass

import pandas as pd
import json
import math
import os
from typing import List, Optional, Dict
try:
    from prods_fastapi.color_utils import get_color_mapping, get_seasonal_palettes, get_monk_hex_codes
except ImportError:
    def get_color_mapping(): return {}
    def get_seasonal_palettes(): return {}
    def get_monk_hex_codes(): return {}

from pathlib import Path
import re
import numpy as np
import cv2
from webcolors import hex_to_rgb, rgb_to_hex
import io
from PIL import Image
import logging
import random
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple configuration
class Settings:
    app_name = "AI Fashion Backend"
    app_version = "1.0.0"
    cors_origins = ["*"]
    cors_allow_credentials = True
    cors_allow_methods = ["*"]
    cors_allow_headers = ["*"]
    max_workers = 4

settings = Settings()

# Feature flags - disable complex features
FEATURE_FLAGS = {
    "enable_caching": False,
    "enable_async_db": False,
    "enable_background_processing": False,
    "enable_health_checks": False,
    "enable_compression": True,
    "enable_metrics": False,
}

def get_environment_config():
    return {
        "debug": False,
        "environment": "production",
        "port": int(os.getenv("PORT", "8000")),
    }

env_config = get_environment_config()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    try:
        logger.info("Starting AI Fashion Backend (Fallback Mode)...")
        
        # Simple initialization
        if FEATURE_FLAGS["enable_caching"]:
            warm_cache_skin_tones()
            warm_cache_color_palettes()
            logger.info("Caches warmed")
        
        logger.info("Application started successfully in fallback mode")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        logger.info("Shutting down AI Fashion Backend...")
        await async_db_service.close()
        logger.info("Application shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=env_config["debug"],
    lifespan=lifespan
)

# Add performance middleware
if FEATURE_FLAGS["enable_compression"]:
    app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Monk skin tone scale
MONK_SKIN_TONES = {
    'Monk 1': '#f6ede4',
    'Monk 2': '#f3e7db', 
    'Monk 3': '#f7ead0',
    'Monk 4': '#eadaba',
    'Monk 5': '#d7bd96',
    'Monk 6': '#a07e56',
    'Monk 7': '#825c43',
    'Monk 8': '#604134',
    'Monk 9': '#3a312a',
    'Monk 10': '#292420'
}

@app.get("/")
def home():
    return {"message": "Welcome to the AI Fashion API!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "AI Fashion Backend is running"}

@app.get("/color-suggestions")
def get_color_suggestions(skin_tone: str = Query(None)):
    """Get color suggestions for a specific skin tone."""
    suggestions = [
        {"skin_tone": "Fair", "suitable_colors": "Navy Blue, Emerald Green, Ruby Red, Cool Pink"},
        {"skin_tone": "Medium", "suitable_colors": "Warm Brown, Orange, Coral, Olive Green"},
        {"skin_tone": "Dark", "suitable_colors": "Bright Yellow, Royal Blue, Magenta, White"},
        {"skin_tone": "Deep", "suitable_colors": "Vibrant Colors, Jewel Tones, Bright Contrasts"}
    ]
    
    if skin_tone:
        filtered = [s for s in suggestions if skin_tone.lower() in s["skin_tone"].lower()]
        return {"data": filtered, "total_items": len(filtered)}
    
    return {"data": suggestions, "total_items": len(suggestions)}

@app.get("/data/")
def get_makeup_data(
    mst: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100)
):
    """Get makeup products with pagination."""
    # Generate sample makeup products
    brands = ["Fenty Beauty", "MAC", "NARS", "Maybelline", "L'Oreal", "Dior"]
    products = ["Foundation", "Concealer", "Lipstick", "Mascara", "Blush", "Highlighter"]
    
    sample_data = []
    for i in range(100):  # Generate 100 sample products
        brand = random.choice(brands)
        product_type = random.choice(products)
        price = f"${random.randint(15, 50)}.{random.randint(10, 99)}"
        
        sample_data.append({
            "product_name": f"{brand} {product_type}",
            "brand": brand,
            "price": price,
            "image_url": f"https://via.placeholder.com/150/FF{random.randint(1000, 9999)}/FFFFFF?text={brand.replace(' ', '+')}",
            "mst": mst or f"Monk{random.randint(1, 10):02d}",
            "desc": f"Beautiful {product_type.lower()} from {brand}"
        })
    
    # Apply pagination
    total_items = len(sample_data)
    total_pages = math.ceil(total_items / limit)
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_items)
    
    paginated_data = sample_data[start_idx:end_idx]
    
    return {
        "data": paginated_data,
        "total_items": total_items,
        "total_pages": total_pages,
        "page": page,
        "limit": limit
    }

def analyze_skin_tone_simple(image_array: np.ndarray) -> Dict:
    """Simplified skin tone analysis."""
    try:
        # Get average color of the image center
        h, w = image_array.shape[:2]
        center_region = image_array[h//4:3*h//4, w//4:3*w//4]
        
        # Calculate average RGB
        avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
        
        # Find closest Monk skin tone
        min_distance = float('inf')
        closest_monk = "Monk 5"  # Default
        
        for monk_name, hex_color in MONK_SKIN_TONES.items():
            monk_rgb = np.array(hex_to_rgb(hex_color))
            distance = np.sqrt(np.sum((avg_color - monk_rgb) ** 2))
            
            if distance < min_distance:
                min_distance = distance
                closest_monk = monk_name
        
        # Format response
        monk_number = closest_monk.split()[1]
        monk_id = f"Monk{monk_number.zfill(2)}"
        derived_hex = rgb_to_hex((int(avg_color[0]), int(avg_color[1]), int(avg_color[2])))
        
        return {
            'monk_skin_tone': monk_id,
            'monk_tone_display': closest_monk,
            'monk_hex': MONK_SKIN_TONES[closest_monk],
            'derived_hex_code': derived_hex,
            'dominant_rgb': avg_color.astype(int).tolist(),
            'confidence': 0.8,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error in skin tone analysis: {e}")
        return {
            'monk_skin_tone': 'Monk05',
            'monk_tone_display': 'Monk 5',
            'monk_hex': MONK_SKIN_TONES['Monk 5'],
            'derived_hex_code': '#d7bd96',
            'dominant_rgb': [215, 189, 150],
            'confidence': 0.5,
            'success': False,
            'error': str(e)
        }

@app.post("/analyze-skin-tone")
async def analyze_skin_tone(file: UploadFile = File(...)):
    """Analyze skin tone from uploaded image."""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_array = np.array(image)
        
        # Analyze skin tone
        result = analyze_skin_tone_simple(image_array)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_skin_tone endpoint: {e}")
        return {
            'monk_skin_tone': 'Monk05',
            'monk_tone_display': 'Monk 5',
            'monk_hex': '#d7bd96',
            'derived_hex_code': '#d7bd96',
            'dominant_rgb': [215, 189, 150],
            'confidence': 0.5,
            'success': False,
            'error': str(e)
        }

# Health and monitoring endpoints
@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check"""
    return await get_health_endpoint()

@app.get("/metrics")
async def get_system_metrics():
    """Get system metrics"""
    return await get_metrics_endpoint()

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    return await get_system_stats_endpoint()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
