# Color routes for the Fashion AI backend
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import psycopg2
from pydantic import BaseModel

# Create router for color endpoints
color_router = APIRouter(prefix="/api/colors", tags=["colors"])

# Database connection (use external Render.com database)
import os
DB_CONFIG = {
    'host': 'dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com',
    'database': 'fashion_jvy9',
    'user': 'fashion_jvy9_user',
    'password': '0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh',
    'port': '5432',
    'sslmode': 'require'  # External database needs SSL
}

# Pydantic models
class ColorRecommendation(BaseModel):
    hex_code: str
    color_name: Optional[str]
    suitable_skin_tone: Optional[str]
    seasonal_palette: Optional[str]
    category: Optional[str]

class MonkColor(BaseModel):
    hex_code: str
    color_name: str
    category: str

def connect_to_db():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

@color_router.get("/skin-tone/{skin_tone}", response_model=List[ColorRecommendation])
async def get_colors_by_skin_tone(
    skin_tone: str,
    limit: Optional[int] = Query(50, description="Number of colors to return"),
    category: Optional[str] = Query(None, description="Filter by category (recommended/avoid)")
):
    """Get colors for a specific skin tone"""
    conn = connect_to_db()
    
    try:
        cursor = conn.cursor()
        
        base_query = """
        SELECT hex_code, color_name, suitable_skin_tone, seasonal_palette, category
        FROM colors 
        WHERE (suitable_skin_tone ILIKE %s OR seasonal_palette ILIKE %s)
        """
        
        params = [f'%{skin_tone}%', f'%{skin_tone}%']
        
        if category:
            base_query += " AND category = %s"
            params.append(category)
        
        base_query += " ORDER BY category, color_name LIMIT %s;"
        params.append(limit)
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        colors = []
        for row in results:
            colors.append(ColorRecommendation(
                hex_code=row[0],
                color_name=row[1],
                suitable_skin_tone=row[2],
                seasonal_palette=row[3],
                category=row[4]
            ))
        
        cursor.close()
        conn.close()
        
        return colors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching colors: {e}")

@color_router.get("/recommendations/{skin_tone}", response_model=List[ColorRecommendation])
async def get_color_recommendations(
    skin_tone: str,
    limit: Optional[int] = Query(10, description="Number of recommendations to return")
):
    """Get top color recommendations for a skin tone"""
    conn = connect_to_db()
    
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT hex_code, color_name, suitable_skin_tone, seasonal_palette, category
        FROM colors 
        WHERE (suitable_skin_tone ILIKE %s OR seasonal_palette ILIKE %s)
        AND category = 'recommended'
        ORDER BY color_name
        LIMIT %s;
        """
        
        cursor.execute(query, (f'%{skin_tone}%', f'%{skin_tone}%', limit))
        results = cursor.fetchall()
        
        recommendations = []
        for row in results:
            recommendations.append(ColorRecommendation(
                hex_code=row[0],
                color_name=row[1],
                suitable_skin_tone=row[2],
                seasonal_palette=row[3],
                category=row[4]
            ))
        
        cursor.close()
        conn.close()
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {e}")

@color_router.get("/monk", response_model=List[MonkColor])
async def get_monk_colors():
    """Get monk-inspired colors"""
    conn = connect_to_db()
    
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT hex_code, color_name, category
        FROM colors 
        WHERE suitable_skin_tone IS NULL AND seasonal_palette IS NULL
        AND color_name IN ('Monk Brown', 'Sienna', 'Peru Brown', 'Burlywood', 'Tan', 'Khaki Brown', 
                          'Dark Orange', 'Orange', 'Goldenrod', 'Dark Goldenrod', 'Maroon', 
                          'Dark Red', 'Saddle Brown', 'Dark Brown', 'Sepia', 'Coyote Brown', 
                          'Slate Gray', 'Light Slate Gray', 'Dim Gray', 'Gray')
        ORDER BY color_name;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        colors = []
        for row in results:
            colors.append(MonkColor(
                hex_code=row[0],
                color_name=row[1],
                category=row[2]
            ))
        
        cursor.close()
        conn.close()
        
        return colors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching monk colors: {e}")

@color_router.get("/hex/{hex_code}", response_model=ColorRecommendation)
async def get_color_by_hex(hex_code: str):
    """Get color information by hex code"""
    if not hex_code.startswith('#'):
        hex_code = '#' + hex_code
    
    conn = connect_to_db()
    
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT hex_code, color_name, suitable_skin_tone, seasonal_palette, category
        FROM colors 
        WHERE hex_code = %s;
        """
        
        cursor.execute(query, (hex_code,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Color not found")
        
        color_info = ColorRecommendation(
            hex_code=result[0],
            color_name=result[1],
            suitable_skin_tone=result[2],
            seasonal_palette=result[3],
            category=result[4]
        )
        
        cursor.close()
        conn.close()
        
        return color_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching color: {e}")

@color_router.get("/all", response_model=List[ColorRecommendation])
async def get_all_colors(
    limit: Optional[int] = Query(500, description="Number of colors to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skin_tone: Optional[str] = Query(None, description="Filter by skin tone")
):
    """Get all colors with optional filters - using correct database tables"""
    try:
        from database import SessionLocal, ColorPalette, SkinToneMapping
        from sqlalchemy import text
        import json
        
        db = SessionLocal()
        try:
            colors = []
            
            # First try to get colors from color_palettes table
            if skin_tone:
                # Map skin tone to seasonal type if needed
                seasonal_type = skin_tone
                if "monk" in skin_tone.lower():
                    monk_number = ''.join(filter(str.isdigit, skin_tone))
                    if monk_number:
                        monk_tone_formatted = f"Monk{monk_number.zfill(2)}"
                        mapping = db.query(SkinToneMapping).filter(
                            SkinToneMapping.monk_tone == monk_tone_formatted
                        ).first()
                        if mapping:
                            seasonal_type = mapping.seasonal_type
                
                # Get colors from color_palettes table
                palette = db.query(ColorPalette).filter(
                    ColorPalette.skin_tone == seasonal_type
                ).first()
                
                if palette and palette.flattering_colors:
                    for color in palette.flattering_colors:
                        if isinstance(color, dict) and 'hex' in color and 'name' in color:
                            colors.append(ColorRecommendation(
                                hex_code=color['hex'],
                                color_name=color['name'],
                                suitable_skin_tone=seasonal_type,
                                seasonal_palette=seasonal_type,
                                category="recommended"
                            ))
            
            # If we don't have enough colors, try comprehensive_colors table
            if len(colors) < limit:
                remaining_limit = limit - len(colors)
                
                try:
                    if skin_tone:
                        # Handle JSON array properly for monk_tones with fallback
                        comp_query = text("""
                            SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                            FROM comprehensive_colors 
                            WHERE hex_code IS NOT NULL 
                            AND color_name IS NOT NULL
                            AND (
                                (monk_tones IS NOT NULL AND monk_tones::text ILIKE :monk_search)
                                OR (seasonal_types IS NOT NULL AND seasonal_types::text ILIKE :seasonal_search)
                                OR color_name ILIKE :name_search
                            )
                            ORDER BY color_name
                            LIMIT :limit_val
                        """)
                        # Format skin_tone for different search types
                        text_search = f'%{skin_tone}%'
                        comp_result = db.execute(comp_query, {
                            'monk_search': text_search,
                            'seasonal_search': text_search, 
                            'name_search': text_search, 
                            'limit_val': remaining_limit
                        })
                    else:
                        comp_query = text("""
                            SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                            FROM comprehensive_colors 
                            WHERE hex_code IS NOT NULL 
                            AND color_name IS NOT NULL
                            ORDER BY color_name
                            LIMIT :limit_val
                        """)
                        comp_result = db.execute(comp_query, {'limit_val': remaining_limit})
                    
                    comp_colors = comp_result.fetchall()
                    for row in comp_colors:
                        # Avoid duplicates
                        if not any(c.hex_code.lower() == row[0].lower() for c in colors):
                            colors.append(ColorRecommendation(
                                hex_code=row[0],
                                color_name=row[1],
                                suitable_skin_tone=skin_tone or "Universal",
                                seasonal_palette=row[2] if row[2] else "Universal",
                                category="recommended"
                            ))
                            
                except Exception as comp_error:
                    # Log the error but continue with fallback
                    print(f"Comprehensive colors query failed: {comp_error}")
                    # Try a simpler query without JSON operations
                    try:
                        simple_query = text("""
                            SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                            FROM comprehensive_colors 
                            WHERE hex_code IS NOT NULL 
                            AND color_name IS NOT NULL
                            ORDER BY color_name
                            LIMIT :limit_val
                        """)
                        simple_result = db.execute(simple_query, {'limit_val': remaining_limit})
                        simple_colors = simple_result.fetchall()
                        for row in simple_colors:
                            if not any(c.hex_code.lower() == row[0].lower() for c in colors):
                                colors.append(ColorRecommendation(
                                    hex_code=row[0],
                                    color_name=row[1],
                                    suitable_skin_tone="Universal",
                                    seasonal_palette=row[2] if row[2] else "Universal",
                                    category="recommended"
                                ))
                    except Exception as simple_error:
                        print(f"Simple colors query also failed: {simple_error}")
            
            # If still not enough colors, get some basic colors from all palettes
            if len(colors) < 10:
                all_palettes = db.query(ColorPalette).limit(5).all()
                for palette in all_palettes:
                    if palette.flattering_colors:
                        for color in palette.flattering_colors[:2]:  # Just 2 colors per palette
                            if isinstance(color, dict) and 'hex' in color and 'name' in color:
                                # Avoid duplicates
                                if not any(c.hex_code.lower() == color['hex'].lower() for c in colors):
                                    colors.append(ColorRecommendation(
                                        hex_code=color['hex'],
                                        color_name=color['name'],
                                        suitable_skin_tone=palette.skin_tone,
                                        seasonal_palette=palette.skin_tone,
                                        category="recommended"
                                    ))
                                    if len(colors) >= limit:
                                        break
                    if len(colors) >= limit:
                        break
            
            return colors[:limit]
            
        finally:
            db.close()
            
    except Exception as e:
        # Fallback: Try to get colors from processed data
        try:
            import os
            import json
            processed_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'processed_data', 'seasonal_palettes.json')
            
            if os.path.exists(processed_data_path):
                with open(processed_data_path, 'r') as f:
                    seasonal_data = json.load(f)
                
                fallback_colors = []
                for season, palette in seasonal_data.items():
                    if isinstance(palette, dict) and 'recommended' in palette:
                        for color in palette['recommended']:
                            if isinstance(color, dict) and 'color' in color and 'name' in color:
                                fallback_colors.append(ColorRecommendation(
                                    hex_code=color['color'],
                                    color_name=color['name'],
                                    suitable_skin_tone=season,
                                    seasonal_palette=season,
                                    category="recommended"
                                ))
                
                if fallback_colors:
                    return fallback_colors[:limit]
                    
        except Exception as fallback_e:
            pass
            
        raise HTTPException(status_code=500, detail=f"Error fetching colors: {e}")

# Add a separate router for color palettes
from fastapi import APIRouter
palette_router = APIRouter(prefix="/api", tags=["palettes"])

class ColorPaletteResponse(BaseModel):
    colors_that_suit: List[dict]
    colors_to_avoid: List[dict] = []
    seasonal_type: str
    monk_skin_tone: str
    message: str
    database_source: bool = True

@palette_router.get("/color-palettes-db")
async def get_color_palettes_db(
    skin_tone: Optional[str] = Query(None, description="Monk skin tone (e.g., Monk05) or seasonal type"),
    limit: Optional[int] = Query(500, description="Number of colors to return")
):
    """Get color palettes from database based on skin tone mapping - using correct database tables"""
    if not skin_tone:
        raise HTTPException(status_code=400, detail="skin_tone parameter is required")
    
    try:
        from database import SessionLocal, ColorPalette, SkinToneMapping
        
        db = SessionLocal()
        try:
            # Step 1: Determine seasonal type from Monk tone
            seasonal_type = skin_tone
            seasonal_type_map = {
                'Monk01': 'Light Spring',
                'Monk02': 'Light Spring', 
                'Monk03': 'Clear Spring',
                'Monk04': 'Warm Spring',
                'Monk05': 'Soft Autumn',
                'Monk06': 'Warm Autumn',
                'Monk07': 'Deep Autumn',
                'Monk08': 'Deep Winter',
                'Monk09': 'Cool Winter',
                'Monk10': 'Clear Winter'
            }
            
            if skin_tone in seasonal_type_map:
                seasonal_type = seasonal_type_map[skin_tone]
            elif "monk" in skin_tone.lower():
                # Extract number and format
                monk_number = ''.join(filter(str.isdigit, skin_tone))
                if monk_number:
                    monk_tone_formatted = f"Monk{monk_number.zfill(2)}"
                    mapping = db.query(SkinToneMapping).filter(
                        SkinToneMapping.monk_tone == monk_tone_formatted
                    ).first()
                    if mapping:
                        seasonal_type = mapping.seasonal_type
            
            # Step 2: Get colors from color_palettes table
            palette = db.query(ColorPalette).filter(
                ColorPalette.skin_tone == seasonal_type
            ).first()
            
            colors_that_suit = []
            colors_to_avoid = []
            
            if palette:
                # Extract flattering colors
                if palette.flattering_colors:
                    for color in palette.flattering_colors:
                        if isinstance(color, dict) and 'hex' in color and 'name' in color:
                            colors_that_suit.append({
                                "name": color['name'],
                                "hex": color['hex']
                            })
                            if len(colors_that_suit) >= limit:
                                break
                
                # Extract colors to avoid
                if palette.colors_to_avoid:
                    for color in palette.colors_to_avoid:
                        if isinstance(color, dict) and 'hex' in color and 'name' in color:
                            colors_to_avoid.append({
                                "name": color['name'],
                                "hex": color['hex']
                            })
                            if len(colors_to_avoid) >= 20:
                                break
            
            # If we don't have enough colors, try to get some basic colors from other palettes
            if len(colors_that_suit) < 10:
                all_palettes = db.query(ColorPalette).limit(3).all()
                for other_palette in all_palettes:
                    if other_palette.skin_tone != seasonal_type and other_palette.flattering_colors:
                        for color in other_palette.flattering_colors[:2]:  # Just 2 colors per palette
                            if isinstance(color, dict) and 'hex' in color and 'name' in color:
                                # Avoid duplicates
                                if not any(c['hex'].lower() == color['hex'].lower() for c in colors_that_suit):
                                    colors_that_suit.append({
                                        "name": color['name'],
                                        "hex": color['hex']
                                    })
                                    if len(colors_that_suit) >= limit:
                                        break
                    if len(colors_that_suit) >= limit:
                        break
            
            return {
                "colors_that_suit": colors_that_suit,
                "colors": colors_that_suit,  # Alias for compatibility
                "colors_to_avoid": colors_to_avoid,
                "seasonal_type": seasonal_type,
                "monk_skin_tone": skin_tone,
                "description": f"Based on your {seasonal_type} seasonal type and {skin_tone} skin tone, here are colors from our database that complement your complexion.",
                "message": f"Showing {len(colors_that_suit)} recommended colors and {len(colors_to_avoid)} colors to avoid from our comprehensive database.",
                "database_source": True
            }
            
        finally:
            db.close()
        
    except Exception as e:
        # Fallback: return some basic colors
        basic_colors = [
            {"name": "Navy Blue", "hex": "#002D72"},
            {"name": "Forest Green", "hex": "#205C40"},
            {"name": "Burgundy", "hex": "#890C58"},
            {"name": "Charcoal", "hex": "#36454F"},
            {"name": "Deep Teal", "hex": "#00594C"},
            {"name": "Plum", "hex": "#86647A"}
        ]
        
        return {
            "colors_that_suit": basic_colors,
            "colors": basic_colors,
            "colors_to_avoid": [],
            "seasonal_type": skin_tone or "Universal",
            "monk_skin_tone": skin_tone,
            "description": f"Basic color palette for {skin_tone or 'unknown skin tone'} - database error occurred",
            "message": f"Showing {len(basic_colors)} basic colors due to database error: {str(e)}",
            "database_source": False
        }

