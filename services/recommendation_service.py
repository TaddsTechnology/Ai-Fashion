# Recommendation Service (Port 8003) - The Smart Core
# Your exact algorithm with scoring

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
import math
import requests
from webcolors import hex_to_rgb

# Add backend paths
backend_dir = Path(__file__).parent.parent / "backend"
prods_fastapi_dir = backend_dir / "prods_fastapi"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(prods_fastapi_dir))

from database import SessionLocal
from sqlalchemy import text

app = FastAPI(title="Recommendation Service", version="1.0.0")

# CORS for microservice communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
PALETTE_SERVICE_URL = "http://localhost:8002"

def ciede2000_distance(color1_hex: str, color2_hex: str) -> float:
    """
    Calculate CIEDE2000 color distance between two hex colors
    Returns: distance value (lower = more similar)
    """
    try:
        # Convert hex to RGB
        r1, g1, b1 = hex_to_rgb(color1_hex)
        r2, g2, b2 = hex_to_rgb(color2_hex)
        
        # Simple RGB distance as approximation (can be enhanced with full CIEDE2000)
        distance = math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)
        return distance / 441.67  # Normalize to 0-1 scale
        
    except Exception:
        return 1.0  # Maximum distance for invalid colors

def get_best_color_match(product_color: str, palette_colors: List[Dict]) -> Tuple[float, str]:
    """
    Find the best matching color from palette for a product
    Returns: (match_score, matched_color_name)
    """
    if not product_color or not palette_colors:
        return 0.0, "No match"
    
    best_score = 0.0
    best_match = "No match"
    
    for color in palette_colors:
        try:
            # Calculate color distance (lower distance = higher score)
            distance = ciede2000_distance(product_color, color["hex"])
            score = max(0.0, 1.0 - distance)  # Convert distance to score
            
            if score > best_score:
                best_score = score
                best_match = color["name"]
                
        except Exception:
            continue
    
    return best_score, best_match

def calculate_occasion_score(product: Dict, occasion: str) -> float:
    """Calculate how well product fits the occasion"""
    occasion_weights = {
        "work": {
            "formal": 0.9, "business": 0.95, "professional": 0.9,
            "casual": 0.3, "party": 0.1, "festive": 0.2
        },
        "casual": {
            "casual": 0.95, "everyday": 0.9, "weekend": 0.9,
            "formal": 0.2, "business": 0.1, "party": 0.7
        },
        "festive_wedding": {
            "festive": 0.95, "party": 0.9, "celebration": 0.9,
            "formal": 0.8, "elegant": 0.85, "casual": 0.3
        },
        "formal_black_tie": {
            "formal": 0.95, "elegant": 0.95, "black_tie": 1.0,
            "business": 0.7, "casual": 0.1, "party": 0.6
        }
    }
    
    product_occasion = product.get("occasion", "").lower()
    if not product_occasion:
        return 0.5  # Neutral score for unknown occasion
    
    weights = occasion_weights.get(occasion, {})
    return weights.get(product_occasion, 0.5)

def calculate_price_score(product_price: float, budget_range: Tuple[float, float]) -> float:
    """Calculate price fitness score"""
    min_budget, max_budget = budget_range
    
    if min_budget <= product_price <= max_budget:
        return 1.0  # Perfect fit
    elif product_price < min_budget:
        # Too cheap, might indicate lower quality
        return 0.7 + 0.3 * (product_price / min_budget)
    else:
        # Too expensive, penalize based on how much over
        overage = (product_price - max_budget) / max_budget
        return max(0.1, 1.0 - overage)

def calculate_contrast_score(product: Dict, contrast_level: str) -> float:
    """Calculate contrast compatibility score"""
    contrast_weights = {
        "light": {"light": 1.0, "soft": 0.8, "medium": 0.5, "bold": 0.2, "dark": 0.1},
        "medium": {"medium": 1.0, "light": 0.7, "soft": 0.8, "bold": 0.7, "dark": 0.6},
        "high": {"bold": 1.0, "dark": 0.9, "dramatic": 1.0, "medium": 0.6, "light": 0.3}
    }
    
    # Infer product contrast from color and category
    product_color = product.get("hex_color", "").lower()
    product_category = product.get("category", "").lower()
    
    # Simple contrast inference (can be enhanced)
    if "light" in product_color or "pastel" in product_color:
        product_contrast = "light"
    elif "dark" in product_color or "black" in product_color:
        product_contrast = "dark"
    elif "bright" in product_color or "bold" in product_category:
        product_contrast = "bold"
    else:
        product_contrast = "medium"
    
    weights = contrast_weights.get(contrast_level, contrast_weights["medium"])
    return weights.get(product_contrast, 0.5)

def fetch_outfits_from_db(occasion: str, gender: str, budget: Tuple[float, float], 
                         categories: List[str], limit: int = 50) -> List[Dict]:
    """Fetch outfit candidates from database"""
    try:
        db = SessionLocal()
        with db.begin():
            cursor = db.connection().connection.cursor()
            
            # Build query conditions
            conditions = []
            params = []
            
            if occasion and occasion != "any":
                conditions.append("LOWER(occasion) LIKE %s")
                params.append(f"%{occasion.lower()}%")
            
            if gender and gender.lower() != "unisex":
                conditions.append("(LOWER(gender) = %s OR LOWER(gender) = 'unisex')")
                params.append(gender.lower())
            
            if budget[1] > 0:  # If budget is specified
                conditions.append("price BETWEEN %s AND %s")
                params.extend([budget[0], budget[1]])
            
            if categories:
                category_conditions = " OR ".join(["LOWER(category) LIKE %s"] * len(categories))
                conditions.append(f"({category_conditions})")
                for cat in categories:
                    params.append(f"%{cat.lower()}%")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT id, name, brand, category, subcategory, color, hex_color, 
                       price, currency, gender, occasion, season, material, 
                       description, image_url, product_url
                FROM perfect_unified_outfits 
                WHERE {where_clause} 
                AND availability = true
                ORDER BY price ASC
                LIMIT %s
            """
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            outfits = []
            for row in results:
                outfits.append({
                    "id": row[0],
                    "name": row[1],
                    "brand": row[2],
                    "category": row[3],
                    "subcategory": row[4],
                    "color": row[5],
                    "hex_color": row[6],
                    "price": float(row[7]) if row[7] else 0.0,
                    "currency": row[8],
                    "gender": row[9],
                    "occasion": row[10],
                    "season": row[11],
                    "material": row[12],
                    "description": row[13],
                    "image_url": row[14],
                    "product_url": row[15]
                })
            
        db.close()
        return outfits
        
    except Exception as e:
        print(f"Database error fetching outfits: {e}")
        return []

def fetch_makeup_from_db(undertone: str, price_range: Tuple[float, float], 
                        categories: List[str], limit: int = 30) -> List[Dict]:
    """Fetch makeup candidates from database"""
    try:
        db = SessionLocal()
        with db.begin():
            cursor = db.connection().connection.cursor()
            
            conditions = []
            params = []
            
            if undertone:
                conditions.append("(LOWER(undertone) = %s OR undertone IS NULL)")
                params.append(undertone.lower())
            
            if price_range[1] > 0:
                conditions.append("price BETWEEN %s AND %s")
                params.extend([price_range[0], price_range[1]])
            
            if categories:
                category_conditions = " OR ".join(["LOWER(category) LIKE %s"] * len(categories))
                conditions.append(f"({category_conditions})")
                for cat in categories:
                    params.append(f"%{cat.lower()}%")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT id, name, brand, category, subcategory, color, hex_color, 
                       price, currency, undertone, finish, coverage, skin_type,
                       shade_name, shade_number, description, image_url, product_url
                FROM perfect_unified_makeup 
                WHERE {where_clause} 
                AND availability = true
                ORDER BY price ASC
                LIMIT %s
            """
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            makeup = []
            for row in results:
                makeup.append({
                    "id": row[0],
                    "name": row[1],
                    "brand": row[2],
                    "category": row[3],
                    "subcategory": row[4],
                    "color": row[5],
                    "hex_color": row[6],
                    "price": float(row[7]) if row[7] else 0.0,
                    "currency": row[8],
                    "undertone": row[9],
                    "finish": row[10],
                    "coverage": row[11],
                    "skin_type": row[12],
                    "shade_name": row[13],
                    "shade_number": row[14],
                    "description": row[15],
                    "image_url": row[16],
                    "product_url": row[17]
                })
            
        db.close()
        return makeup
        
    except Exception as e:
        print(f"Database error fetching makeup: {e}")
        return []

def get_palette_from_service(season: str, contrast: str, occasion: str = None):
    """Get color palette from Palette Service"""
    try:
        params = {"season": season, "contrast": contrast}
        if occasion:
            params["occasion"] = occasion
            
        response = requests.get(f"{PALETTE_SERVICE_URL}/get_palette", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error getting palette: {e}")
        return None

@app.get("/")
def root():
    return {"service": "Recommendation Service", "status": "running", "port": 8003}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "recommendation"}

@app.post("/get_recommendations")
def get_recommendations(
    season: str = Query(..., description="Seasonal color type"),
    undertone: str = Query(..., description="Skin undertone"),
    contrast: str = Query(..., description="Contrast level"),
    occasion: str = Query("casual", description="Occasion"),
    gender: str = Query("Unisex", description="Gender preference"),
    budget_min: float = Query(0, description="Minimum budget"),
    budget_max: float = Query(1000, description="Maximum budget"),
    outfit_categories: str = Query("tops,bottoms,dresses", description="Comma-separated outfit categories"),
    makeup_categories: str = Query("foundation,lipstick,eyeshadow", description="Comma-separated makeup categories")
):
    """
    Get personalized recommendations using your exact algorithm with scoring
    """
    try:
        # Get color palette
        palette_data = get_palette_from_service(season, contrast, occasion)
        if not palette_data:
            raise HTTPException(status_code=500, detail="Could not retrieve color palette")
        
        palette = palette_data.get("colors", [])
        
        # Parse categories
        outfit_cats = [cat.strip() for cat in outfit_categories.split(",")]
        makeup_cats = [cat.strip() for cat in makeup_categories.split(",")]
        
        # Fetch candidates
        budget_range = (budget_min, budget_max)
        outfits = fetch_outfits_from_db(occasion, gender, budget_range, outfit_cats)
        makeup = fetch_makeup_from_db(undertone, budget_range, makeup_cats)
        
        # Score outfits using your algorithm
        scored_outfits = []
        for outfit in outfits:
            # Color matching score (55% weight)
            color_score, matched_color = get_best_color_match(outfit.get("hex_color", ""), palette)
            
            # Occasion score (15% weight)
            occasion_score = calculate_occasion_score(outfit, occasion)
            
            # Price score (15% weight)
            price = outfit.get("price", 0)
            price_score = calculate_price_score(price, budget_range)
            
            # Contrast score (15% weight)
            contrast_score = calculate_contrast_score(outfit, contrast)
            
            # Total score with your exact weights
            total_score = (0.55 * color_score + 0.15 * occasion_score + 
                          0.15 * price_score + 0.15 * contrast_score)
            
            scored_outfits.append({
                **outfit,
                "color_score": color_score,
                "occasion_score": occasion_score,
                "price_score": price_score,
                "contrast_score": contrast_score,
                "total_score": total_score,
                "matched_color": matched_color,
                "explanation": f"Color match: {matched_color} ({color_score:.2f}), "
                              f"Occasion fit: {occasion_score:.2f}, "
                              f"Price value: {price_score:.2f}, "
                              f"Contrast: {contrast_score:.2f}"
            })
        
        # Score makeup products
        scored_makeup = []
        for product in makeup:
            color_score, matched_color = get_best_color_match(product.get("hex_color", ""), palette)
            price_score = calculate_price_score(product.get("price", 0), budget_range)
            
            # For makeup, undertone compatibility is important
            undertone_score = 1.0 if (product.get("undertone", "").lower() == undertone.lower() 
                                    or not product.get("undertone")) else 0.6
            
            total_score = (0.50 * color_score + 0.25 * undertone_score + 0.25 * price_score)
            
            scored_makeup.append({
                **product,
                "color_score": color_score,
                "undertone_score": undertone_score,
                "price_score": price_score,
                "total_score": total_score,
                "matched_color": matched_color,
                "explanation": f"Color match: {matched_color} ({color_score:.2f}), "
                              f"Undertone fit: {undertone_score:.2f}, "
                              f"Price value: {price_score:.2f}"
            })
        
        # Sort by total score (highest first)
        scored_outfits.sort(key=lambda x: x["total_score"], reverse=True)
        scored_makeup.sort(key=lambda x: x["total_score"], reverse=True)
        
        return {
            "season": season,
            "undertone": undertone,
            "contrast": contrast,
            "occasion": occasion,
            "palette": palette,
            "recommended_outfits": scored_outfits[:15],  # Top 15 outfits
            "recommended_makeup": scored_makeup[:10],    # Top 10 makeup products
            "algorithm": {
                "outfit_weights": {"color": 0.55, "occasion": 0.15, "price": 0.15, "contrast": 0.15},
                "makeup_weights": {"color": 0.50, "undertone": 0.25, "price": 0.25}
            },
            "total_candidates": {
                "outfits": len(outfits),
                "makeup": len(makeup)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.get("/color_alternatives")
def get_color_alternatives(
    original_color: str = Query(..., description="Original color hex"),
    season: str = Query(..., description="Seasonal type"),
    limit: int = Query(5, description="Number of alternatives")
):
    """Get alternative colors from the same palette"""
    try:
        palette_data = get_palette_from_service(season, "medium")
        if not palette_data:
            return {"alternatives": []}
        
        palette = palette_data.get("colors", [])
        
        # Find colors similar to original but different
        alternatives = []
        for color in palette:
            if color["hex"].upper() != original_color.upper():
                distance = ciede2000_distance(original_color, color["hex"])
                alternatives.append({
                    **color,
                    "similarity": 1.0 - distance
                })
        
        # Sort by similarity and return top alternatives
        alternatives.sort(key=lambda x: x["similarity"], reverse=True)
        
        return {
            "original_color": original_color,
            "alternatives": alternatives[:limit]
        }
        
    except Exception as e:
        return {"error": str(e), "alternatives": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
