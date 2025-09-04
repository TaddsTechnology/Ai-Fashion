#!/usr/bin/env python3
"""
Simple test server to validate color API endpoints without heavy dependencies
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

# Import the database models and routers
from database import SessionLocal, ColorPalette, SkinToneMapping, ComprehensiveColors
from sqlalchemy import text
from color_routes import color_router, palette_router

# Create a simple FastAPI app
app = FastAPI(title="Color API Test Server", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include the color routers
app.include_router(color_router)
app.include_router(palette_router)

@app.get("/")
def home():
    return {"message": "Color API Test Server", "status": "healthy"}

@app.get("/test-palettes")
def test_palettes():
    """Test endpoint to verify color palettes are working"""
    db = SessionLocal()
    try:
        # Test for Monk05 (Soft Autumn)
        seasonal_type = "Soft Autumn"
        palette = db.query(ColorPalette).filter(
            ColorPalette.skin_tone == seasonal_type
        ).first()
        
        if palette:
            return {
                "status": "success",
                "seasonal_type": seasonal_type,
                "colors_count": len(palette.flattering_colors) if palette.flattering_colors else 0,
                "sample_colors": palette.flattering_colors[:5] if palette.flattering_colors else []
            }
        else:
            return {"status": "error", "message": "No palette found"}
    finally:
        db.close()

@app.get("/test-comprehensive")
def test_comprehensive():
    """Test endpoint to verify comprehensive colors are working"""
    db = SessionLocal()
    try:
        comp_query = text("""
            SELECT DISTINCT hex_code, color_name, color_family, brightness_level
            FROM comprehensive_colors 
            WHERE monk_tones IS NOT NULL 
            AND monk_tones::text LIKE '%Monk05%'
            AND hex_code IS NOT NULL
            AND color_name IS NOT NULL
            ORDER BY color_name
            LIMIT 10
        """)
        comp_result = db.execute(comp_query)
        comp_colors = comp_result.fetchall()
        
        colors = [
            {
                "hex_code": row[0],
                "color_name": row[1],
                "color_family": row[2],
                "brightness_level": row[3]
            }
            for row in comp_colors
        ]
        
        return {
            "status": "success",
            "colors_count": len(colors),
            "colors": colors
        }
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
