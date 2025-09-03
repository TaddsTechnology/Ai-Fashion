# Add these routes to your existing FastAPI backend
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import psycopg2
from pydantic import BaseModel

# Create router for color endpoints
color_router = APIRouter(prefix="/api/colors", tags=["colors"])

# Database connection (use your existing DB config)
DB_CONFIG = {
    'host': 'dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com',
    'database': 'fashion_jvy9',
    'user': 'fashion_jvy9_user',
    'password': '0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh',
    'port': '5432',
    'sslmode': 'require'
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

# Add this to your main FastAPI app:
# app.include_router(color_router)
