# Palette Service (Port 8002)
# season -> 10-20 color hexes

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
from pathlib import Path
from typing import List, Dict, Optional
import json

# Add backend paths
backend_dir = Path(__file__).parent.parent / "backend"
prods_fastapi_dir = backend_dir / "prods_fastapi"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(prods_fastapi_dir))

from database import SessionLocal, ColorPalette
from sqlalchemy import text

app = FastAPI(title="Palette Service", version="1.0.0")

# CORS for microservice communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_mst_palette_from_db(mst_id: int, occasion: Optional[str] = None):
    """Get palette from MST master palette table"""
    try:
        db = SessionLocal()
        with db.begin():
            cursor = db.connection().connection.cursor()
            
            if occasion:
                # Get occasion-specific palette
                cursor.execute("""
                    SELECT base_palette, accent_palette, occasion_palettes, neutrals_light
                    FROM mst_master_palette 
                    WHERE mst_id = %s
                """, [mst_id])
            else:
                # Get general palette
                cursor.execute("""
                    SELECT base_palette, accent_palette, neutrals_light, neutrals_dark
                    FROM mst_master_palette 
                    WHERE mst_id = %s
                """, [mst_id])
            
            result = cursor.fetchone()
            if result:
                base_palette = result[0] if result[0] else []
                accent_palette = result[1] if result[1] else []
                
                colors = []
                
                if occasion and len(result) > 2 and result[2]:
                    # Use occasion-specific colors if available
                    occasion_palettes = result[2]
                    if isinstance(occasion_palettes, dict) and occasion in occasion_palettes:
                        occasion_colors = occasion_palettes[occasion]
                        for hex_color in occasion_colors[:12]:  # Limit to 12
                            colors.append({
                                "hex": hex_color,
                                "name": get_color_name(hex_color),
                                "type": "occasion"
                            })
                
                # Add base colors
                for hex_color in base_palette[:8]:
                    colors.append({
                        "hex": hex_color,
                        "name": get_color_name(hex_color),
                        "type": "base"
                    })
                
                # Add accent colors
                for hex_color in accent_palette[:6]:
                    colors.append({
                        "hex": hex_color,
                        "name": get_color_name(hex_color),
                        "type": "accent"
                    })
                
                # Add neutrals
                if len(result) > 2:
                    neutrals = result[2] if not occasion else result[3]
                    if neutrals:
                        for hex_color in neutrals[:4]:
                            colors.append({
                                "hex": hex_color,
                                "name": get_color_name(hex_color),
                                "type": "neutral"
                            })
                
                return colors[:20]  # Limit to 20 colors
                
        db.close()
        return []
        
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_seasonal_palette_from_db(season: str):
    """Get palette from color_palettes table"""
    try:
        db = SessionLocal()
        palette = db.query(ColorPalette).filter(
            ColorPalette.skin_tone == season
        ).first()
        
        if palette and palette.flattering_colors:
            colors = []
            for color in palette.flattering_colors:
                colors.append({
                    "hex": color.get("hex", ""),
                    "name": color.get("name", "Unknown"),
                    "type": "flattering"
                })
            db.close()
            return colors
            
        db.close()
        return []
        
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_color_name(hex_color: str) -> str:
    """Generate or retrieve color name"""
    color_names = {
        "#F67599": "Rose Pink",
        "#C964CF": "Orchid Purple", 
        "#71C5E8": "Sky Blue",
        "#F57EB6": "Hot Pink",
        "#A05EB5": "Lavender Purple",
        "#6DCDB8": "Mint Green",
        "#FFB81C": "Golden Yellow",
        "#FF8D6D": "Coral Orange",
        "#00A499": "Turquoise",
        "#DA291C": "Crimson Red"
    }
    return color_names.get(hex_color.upper(), f"Color {hex_color}")

# Season to MST mapping
SEASON_TO_MST = {
    "Light Spring": [1, 2],
    "Clear Spring": [3],
    "Warm Spring": [4],
    "Soft Autumn": [5],
    "Warm Autumn": [6],
    "Deep Autumn": [7],
    "Deep Winter": [8],
    "Cool Winter": [9],
    "Clear Winter": [10]
}

@app.get("/")
def root():
    return {"service": "Palette Service", "status": "running", "port": 8002}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "palette"}

@app.get("/get_palette")
def get_palette(
    season: str = Query(..., description="Seasonal color type"),
    contrast: str = Query("medium", description="Contrast level"),
    occasion: Optional[str] = Query(None, description="Occasion filter")
):
    """
    Get color palette based on season and contrast level
    Returns: {"season": "Warm Spring", "colors": [{"hex": "#FCE300", "name": "Bright Yellow", "type": "base"}]}
    """
    try:
        # Get MST IDs for this season
        mst_ids = SEASON_TO_MST.get(season, [5])  # Default to Soft Autumn
        
        all_colors = []
        
        # Try MST master palette first
        for mst_id in mst_ids:
            colors = get_mst_palette_from_db(mst_id, occasion)
            all_colors.extend(colors)
            if len(all_colors) >= 15:  # We have enough colors
                break
        
        # If not enough colors, try seasonal palette
        if len(all_colors) < 10:
            seasonal_colors = get_seasonal_palette_from_db(season)
            all_colors.extend(seasonal_colors)
        
        # If still not enough, use fallback
        if len(all_colors) < 5:
            all_colors = get_fallback_palette(season)
        
        # Remove duplicates and limit
        seen_colors = set()
        unique_colors = []
        for color in all_colors:
            if color["hex"].upper() not in seen_colors:
                seen_colors.add(color["hex"].upper())
                unique_colors.append(color)
                if len(unique_colors) >= 20:
                    break
        
        return {
            "season": season,
            "contrast": contrast,
            "occasion": occasion,
            "colors": unique_colors,
            "total_colors": len(unique_colors),
            "source": "database"
        }
        
    except Exception as e:
        return {
            "season": season,
            "colors": get_fallback_palette(season),
            "error": str(e),
            "source": "fallback"
        }

def get_fallback_palette(season: str) -> List[Dict]:
    """Fallback color palettes when database is unavailable"""
    palettes = {
        "Light Spring": [
            {"hex": "#FFB6C1", "name": "Light Pink", "type": "base"},
            {"hex": "#98FB98", "name": "Mint Green", "type": "base"},
            {"hex": "#FFCBA4", "name": "Peach", "type": "base"},
            {"hex": "#E6E6FA", "name": "Lavender", "type": "base"},
            {"hex": "#F0F8FF", "name": "Alice Blue", "type": "neutral"}
        ],
        "Clear Spring": [
            {"hex": "#00FFFF", "name": "Turquoise", "type": "base"},
            {"hex": "#FFFF00", "name": "Bright Yellow", "type": "base"},
            {"hex": "#FF69B4", "name": "Hot Pink", "type": "base"},
            {"hex": "#32CD32", "name": "Lime Green", "type": "accent"},
            {"hex": "#FF6347", "name": "Tomato Red", "type": "accent"}
        ],
        "Warm Spring": [
            {"hex": "#FFA500", "name": "Orange", "type": "base"},
            {"hex": "#FFD700", "name": "Gold", "type": "base"},
            {"hex": "#FF7F50", "name": "Coral", "type": "base"},
            {"hex": "#ADFF2F", "name": "Green Yellow", "type": "accent"},
            {"hex": "#F5DEB3", "name": "Wheat", "type": "neutral"}
        ],
        "Soft Autumn": [
            {"hex": "#8B7D6B", "name": "Taupe", "type": "base"},
            {"hex": "#A0522D", "name": "Sienna", "type": "base"},
            {"hex": "#6B8E23", "name": "Olive Green", "type": "base"},
            {"hex": "#CD853F", "name": "Peru", "type": "accent"},
            {"hex": "#F4A460", "name": "Sandy Brown", "type": "neutral"}
        ],
        "Warm Autumn": [
            {"hex": "#B22222", "name": "Fire Brick", "type": "base"},
            {"hex": "#D2691E", "name": "Chocolate", "type": "base"},
            {"hex": "#DAA520", "name": "Golden Rod", "type": "base"},
            {"hex": "#8B4513", "name": "Saddle Brown", "type": "accent"},
            {"hex": "#A0522D", "name": "Sienna", "type": "neutral"}
        ]
    }
    
    return palettes.get(season, palettes["Soft Autumn"])

@app.get("/get_contrast_colors")
def get_contrast_colors(
    season: str = Query(..., description="Seasonal type"),
    contrast_level: str = Query("medium", description="light, medium, high")
):
    """Get colors filtered by contrast level"""
    palette = get_palette(season, contrast_level)
    
    if contrast_level == "light":
        # Filter for lighter, softer colors
        filtered_colors = [c for c in palette["colors"] if c["type"] in ["neutral", "base"]]
    elif contrast_level == "high":
        # Filter for bold, dramatic colors
        filtered_colors = [c for c in palette["colors"] if c["type"] in ["accent", "base"]]
    else:
        # Medium contrast - all colors
        filtered_colors = palette["colors"]
    
    return {
        "season": season,
        "contrast_level": contrast_level,
        "colors": filtered_colors[:15]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
