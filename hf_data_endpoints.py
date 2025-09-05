"""
Enhanced Data Endpoints for HuggingFace Deployment
These endpoints integrate with the Neon database to provide real makeup and outfit data
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import DictCursor
import logging
import math
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neon database connection
DATABASE_URL = "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def get_db_connection():
    """Get database connection"""
    try:
        return psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

# Add these endpoints to your existing app.py or main.py

# Enhanced /data/ endpoint for makeup products
def get_makeup_data(
    mst: Optional[str] = None,
    ogcolor: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    product_type: Optional[str] = None
):
    """Get real makeup products from Neon database with advanced filtering."""
    
    try:
        conn = get_db_connection()
        if not conn:
            return _get_fallback_makeup_data(page, limit)
        
        cursor = conn.cursor()
        
        # Build dynamic query based on filters
        conditions = ["availability = true"]
        params = []
        
        # Filter by MST (Monk Skin Tone)
        if mst:
            # Convert mst format (e.g., "Monk03" to match database)
            if "monk" in mst.lower():
                monk_num = ''.join(filter(str.isdigit, mst))
                if monk_num:
                    formatted_mst = f"Monk{monk_num.zfill(2)}"
                    # For makeup, we'll filter by undertone compatibility
                    conditions.append("(undertone IS NULL OR undertone IN ('neutral', 'warm', 'cool'))")
        
        # Filter by original color
        if ogcolor:
            hex_color = f"#{ogcolor}" if not ogcolor.startswith('#') else ogcolor
            conditions.append("hex_color ILIKE %s")
            params.append(f"%{hex_color}%")
        
        # Filter by product type
        if product_type:
            types = [t.strip() for t in product_type.split(',')]
            type_conditions = " OR ".join(["LOWER(category) LIKE %s"] * len(types))
            conditions.append(f"({type_conditions})")
            for ptype in types:
                params.append(f"%{ptype.lower()}%")
        
        # Count total items
        count_query = f"""
            SELECT COUNT(*) 
            FROM perfect_unified_makeup 
            WHERE {' AND '.join(conditions)}
        """
        cursor.execute(count_query, params)
        total_items = cursor.fetchone()[0]
        
        # Get paginated data
        offset = (page - 1) * limit
        data_query = f"""
            SELECT id, name, brand, category, subcategory, color, hex_color, 
                   price, currency, undertone, finish, coverage, skin_type,
                   shade_name, shade_number, description, image_url, product_url
            FROM perfect_unified_makeup 
            WHERE {' AND '.join(conditions)}
            ORDER BY price ASC, brand, name
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(data_query, params + [limit, offset])
        results = cursor.fetchall()
        
        # Format data for frontend
        makeup_data = []
        for row in results:
            product = {
                "product_name": row['name'] or "Unknown Product",
                "brand": row['brand'] or "Unknown Brand",
                "price": f"${float(row['price']):.2f}" if row['price'] else "N/A",
                "image_url": row['image_url'] or f"https://via.placeholder.com/150/FF69B4/FFFFFF?text={row['brand'] or 'Product'}",
                "mst": mst or "Universal",
                "desc": row['description'] or f"Beautiful {row['category'] or 'makeup product'} from {row['brand'] or 'premium brand'}",
                "category": row['category'],
                "subcategory": row['subcategory'],
                "color": row['color'],
                "hex_color": row['hex_color'],
                "undertone": row['undertone'],
                "finish": row['finish'],
                "coverage": row['coverage'],
                "skin_type": row['skin_type'],
                "shade_name": row['shade_name'],
                "shade_number": row['shade_number'],
                "product_url": row['product_url'],
                "id": row['id']
            }
            makeup_data.append(product)
        
        conn.close()
        
        total_pages = math.ceil(total_items / limit)
        
        return {
            "data": makeup_data,
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "limit": limit,
            "filters_applied": {
                "mst": mst,
                "ogcolor": ogcolor,
                "product_type": product_type
            },
            "database_source": "neon_perfect_unified_makeup"
        }
        
    except Exception as e:
        logger.error(f"Error fetching makeup data: {e}")
        return _get_fallback_makeup_data(page, limit)

# Enhanced /apparel endpoint for outfit products
def get_apparel_data(
    gender: Optional[str] = None,
    color: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    occasion: Optional[str] = None,
    season: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Get real outfit products from Neon database with advanced filtering."""
    
    try:
        conn = get_db_connection()
        if not conn:
            return _get_fallback_apparel_data(page, limit)
        
        cursor = conn.cursor()
        
        # Build dynamic query
        conditions = ["availability = true"]
        params = []
        
        # Filter by gender
        if gender and gender.lower() != "unisex":
            conditions.append("(LOWER(gender) = %s OR LOWER(gender) = 'unisex')")
            params.append(gender.lower())
        
        # Filter by colors
        if color:
            color_conditions = []
            for c in color:
                color_conditions.append("LOWER(color) LIKE %s")
                params.append(f"%{c.lower()}%")
            if color_conditions:
                conditions.append(f"({' OR '.join(color_conditions)})")
        
        # Filter by occasion
        if occasion:
            conditions.append("LOWER(occasion) LIKE %s")
            params.append(f"%{occasion.lower()}%")
        
        # Filter by season
        if season:
            conditions.append("LOWER(season) LIKE %s")
            params.append(f"%{season.lower()}%")
        
        # Filter by price range
        if min_price is not None:
            conditions.append("price >= %s")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("price <= %s")
            params.append(max_price)
        
        # Count total items
        count_query = f"""
            SELECT COUNT(*) 
            FROM perfect_unified_outfits 
            WHERE {' AND '.join(conditions)}
        """
        cursor.execute(count_query, params)
        total_items = cursor.fetchone()[0]
        
        # Get paginated data
        offset = (page - 1) * limit
        data_query = f"""
            SELECT id, name, brand, category, subcategory, color, hex_color, 
                   price, currency, gender, occasion, season, material, 
                   size_range, description, image_url, product_url
            FROM perfect_unified_outfits 
            WHERE {' AND '.join(conditions)}
            ORDER BY price ASC, brand, name
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(data_query, params + [limit, offset])
        results = cursor.fetchall()
        
        # Format data for frontend
        apparel_data = []
        for row in results:
            product = {
                "Product Name": row['name'] or "Unknown Product",
                "Price": f"${float(row['price']):.2f}" if row['price'] else "N/A",
                "Image URL": row['image_url'] or f"https://via.placeholder.com/150/FF6B6B/FFFFFF?text={row['brand'] or 'Outfit'}",
                "Product Type": row['category'] or "Clothing",
                "baseColour": row['color'] or "Multi",
                "brand": row['brand'] or "Unknown Brand",
                "gender": row['gender'] or "Unisex",
                "category": row['category'],
                "subcategory": row['subcategory'],
                "hex_color": row['hex_color'],
                "occasion": row['occasion'],
                "season": row['season'],
                "material": row['material'],
                "size_range": row['size_range'],
                "description": row['description'],
                "product_url": row['product_url'],
                "id": row['id']
            }
            apparel_data.append(product)
        
        conn.close()
        
        total_pages = math.ceil(total_items / limit)
        
        return {
            "data": apparel_data,
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
            "filters_applied": {
                "gender": gender,
                "color": color,
                "occasion": occasion,
                "season": season,
                "price_range": [min_price, max_price]
            },
            "database_source": "neon_perfect_unified_outfits"
        }
        
    except Exception as e:
        logger.error(f"Error fetching apparel data: {e}")
        return _get_fallback_apparel_data(page, limit)

# New endpoint: Get products by skin tone analysis
def get_products_by_skin_analysis(
    monk_tone: str,
    undertone: str = "neutral",
    seasonal_type: Optional[str] = None,
    product_category: str = "all",  # "makeup", "outfits", or "all"
    limit: int = Query(20, ge=1, le=50)
):
    """Get personalized product recommendations based on skin tone analysis."""
    
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        cursor = conn.cursor()
        
        recommendations = {
            "monk_tone": monk_tone,
            "undertone": undertone,
            "seasonal_type": seasonal_type,
            "makeup_products": [],
            "outfit_products": []
        }
        
        # Get makeup recommendations
        if product_category in ["makeup", "all"]:
            makeup_query = """
                SELECT id, name, brand, category, color, hex_color, price, 
                       undertone, shade_name, description, image_url, product_url
                FROM perfect_unified_makeup 
                WHERE (undertone = %s OR undertone IS NULL OR undertone = 'neutral')
                AND availability = true
                ORDER BY 
                    CASE WHEN undertone = %s THEN 1 ELSE 2 END,
                    price ASC
                LIMIT %s
            """
            cursor.execute(makeup_query, [undertone, undertone, limit // 2])
            makeup_results = cursor.fetchall()
            
            for row in makeup_results:
                recommendations["makeup_products"].append({
                    "id": row['id'],
                    "name": row['name'],
                    "brand": row['brand'],
                    "category": row['category'],
                    "color": row['color'],
                    "hex_color": row['hex_color'],
                    "price": float(row['price']) if row['price'] else 0,
                    "undertone": row['undertone'],
                    "shade_name": row['shade_name'],
                    "description": row['description'],
                    "image_url": row['image_url'],
                    "product_url": row['product_url'],
                    "match_reason": f"Compatible with {undertone} undertone"
                })
        
        # Get outfit recommendations
        if product_category in ["outfits", "all"]:
            outfit_query = """
                SELECT id, name, brand, category, color, hex_color, price,
                       gender, occasion, season, description, image_url, product_url
                FROM perfect_unified_outfits 
                WHERE availability = true
                ORDER BY price ASC
                LIMIT %s
            """
            cursor.execute(outfit_query, [limit // 2])
            outfit_results = cursor.fetchall()
            
            for row in outfit_results:
                recommendations["outfit_products"].append({
                    "id": row['id'],
                    "name": row['name'],
                    "brand": row['brand'],
                    "category": row['category'],
                    "color": row['color'],
                    "hex_color": row['hex_color'],
                    "price": float(row['price']) if row['price'] else 0,
                    "gender": row['gender'],
                    "occasion": row['occasion'],
                    "season": row['season'],
                    "description": row['description'],
                    "image_url": row['image_url'],
                    "product_url": row['product_url'],
                    "match_reason": f"Suitable for {monk_tone} skin tone"
                })
        
        conn.close()
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting skin tone recommendations: {e}")
        return {"error": str(e)}

# Enhanced search endpoint
def search_products(
    query: str,
    category: str = "all",  # "makeup", "outfits", "all"
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100)
):
    """Search products across makeup and outfits."""
    
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        cursor = conn.cursor()
        
        search_results = {
            "query": query,
            "category": category,
            "makeup_products": [],
            "outfit_products": [],
            "total_results": 0
        }
        
        search_terms = f"%{query.lower()}%"
        
        # Search makeup products
        if category in ["makeup", "all"]:
            makeup_search_query = """
                SELECT id, name, brand, category, color, hex_color, price,
                       description, image_url, product_url
                FROM perfect_unified_makeup 
                WHERE (
                    LOWER(name) LIKE %s OR 
                    LOWER(brand) LIKE %s OR 
                    LOWER(category) LIKE %s OR 
                    LOWER(color) LIKE %s OR
                    LOWER(description) LIKE %s
                )
                AND availability = true
                ORDER BY 
                    CASE WHEN LOWER(name) LIKE %s THEN 1 ELSE 2 END,
                    price ASC
                LIMIT %s
            """
            cursor.execute(makeup_search_query, [search_terms] * 6 + [limit // 2])
            makeup_results = cursor.fetchall()
            
            for row in makeup_results:
                search_results["makeup_products"].append({
                    "id": row['id'],
                    "name": row['name'],
                    "brand": row['brand'],
                    "category": row['category'],
                    "color": row['color'],
                    "hex_color": row['hex_color'],
                    "price": float(row['price']) if row['price'] else 0,
                    "description": row['description'],
                    "image_url": row['image_url'],
                    "product_url": row['product_url'],
                    "product_type": "makeup"
                })
        
        # Search outfit products
        if category in ["outfits", "all"]:
            outfit_search_query = """
                SELECT id, name, brand, category, color, hex_color, price,
                       gender, occasion, description, image_url, product_url
                FROM perfect_unified_outfits 
                WHERE (
                    LOWER(name) LIKE %s OR 
                    LOWER(brand) LIKE %s OR 
                    LOWER(category) LIKE %s OR 
                    LOWER(color) LIKE %s OR
                    LOWER(description) LIKE %s
                )
                AND availability = true
                ORDER BY 
                    CASE WHEN LOWER(name) LIKE %s THEN 1 ELSE 2 END,
                    price ASC
                LIMIT %s
            """
            cursor.execute(outfit_search_query, [search_terms] * 6 + [limit // 2])
            outfit_results = cursor.fetchall()
            
            for row in outfit_results:
                search_results["outfit_products"].append({
                    "id": row['id'],
                    "name": row['name'],
                    "brand": row['brand'],
                    "category": row['category'],
                    "color": row['color'],
                    "hex_color": row['hex_color'],
                    "price": float(row['price']) if row['price'] else 0,
                    "gender": row['gender'],
                    "occasion": row['occasion'],
                    "description": row['description'],
                    "image_url": row['image_url'],
                    "product_url": row['product_url'],
                    "product_type": "outfit"
                })
        
        search_results["total_results"] = len(search_results["makeup_products"]) + len(search_results["outfit_products"])
        
        conn.close()
        return search_results
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return {"error": str(e)}

# Fallback functions
def _get_fallback_makeup_data(page: int, limit: int):
    """Fallback makeup data when database is unavailable"""
    brands = ["Fenty Beauty", "MAC", "NARS", "Maybelline", "L'Oreal", "Dior"]
    products = ["Foundation", "Concealer", "Lipstick", "Mascara", "Blush", "Highlighter"]
    
    sample_data = []
    for i in range(50):
        brand = brands[i % len(brands)]
        product_type = products[i % len(products)]
        price = f"${15 + (i % 35)}.99"
        
        sample_data.append({
            "product_name": f"{brand} {product_type}",
            "brand": brand,
            "price": price,
            "image_url": f"https://via.placeholder.com/150/FF69B4/FFFFFF?text={brand.replace(' ', '+')}",
            "mst": f"Monk{((i % 10) + 1):02d}",
            "desc": f"Beautiful {product_type.lower()} from {brand}",
            "database_source": "fallback"
        })
    
    total_items = len(sample_data)
    total_pages = math.ceil(total_items / limit)
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_items)
    
    return {
        "data": sample_data[start_idx:end_idx],
        "total_items": total_items,
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "database_source": "fallback"
    }

def _get_fallback_apparel_data(page: int, limit: int):
    """Fallback apparel data when database is unavailable"""
    brands = ["H&M", "Zara", "Nike", "Adidas", "Uniqlo", "Gap"]
    types = ["T-Shirt", "Jeans", "Dress", "Jacket", "Sweater", "Pants"]
    colors = ["Black", "White", "Blue", "Red", "Green", "Gray"]
    
    sample_data = []
    for i in range(50):
        brand = brands[i % len(brands)]
        product_type = types[i % len(types)]
        color = colors[i % len(colors)]
        price = f"${20 + (i % 60)}.99"
        
        sample_data.append({
            "Product Name": f"{brand} {product_type}",
            "Price": price,
            "Image URL": f"https://via.placeholder.com/150/FF6B6B/FFFFFF?text={product_type.replace(' ', '+')}",
            "Product Type": product_type,
            "baseColour": color,
            "brand": brand,
            "gender": "Unisex",
            "database_source": "fallback"
        })
    
    total_items = len(sample_data)
    total_pages = math.ceil(total_items / limit)
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_items)
    
    return {
        "data": sample_data[start_idx:end_idx],
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "database_source": "fallback"
    }

# Database health check
def check_database_health():
    """Check if database connection is working"""
    try:
        conn = get_db_connection()
        if not conn:
            return {"status": "unhealthy", "message": "Cannot connect to database"}
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM perfect_unified_makeup")
        makeup_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM perfect_unified_outfits")
        outfit_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "makeup_products": makeup_count,
            "outfit_products": outfit_count,
            "database": "neon_postgresql"
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Export all functions to be added to your main app
__all__ = [
    'get_makeup_data',
    'get_apparel_data', 
    'get_products_by_skin_analysis',
    'search_products',
    'check_database_health'
]
