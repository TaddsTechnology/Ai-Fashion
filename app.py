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
        
        # Import enhanced data endpoints
        import psycopg2
        from psycopg2.extras import DictCursor
        import math
        import logging
        from typing import List, Optional
        from fastapi import Query
        
        # Configure logger
        logger = logging.getLogger(__name__)
        
        # Database connection function
        def get_db_connection():
            """Get database connection to Neon"""
            try:
                return psycopg2.connect(
                    "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require",
                    cursor_factory=DictCursor
                )
            except Exception as e:
                print(f"Database connection failed: {e}")
                return None
        
        @app.get("/data/")
        def get_makeup_data(
            mst: Optional[str] = None,
            ogcolor: Optional[str] = None,
            page: int = 1,
            limit: int = 24,
            product_type: Optional[str] = None
        ):
            """Get real makeup products from Neon database"""
            try:
                conn = get_db_connection()
                if not conn:
                    return _get_fallback_makeup_data(page, limit)
                
                cursor = conn.cursor()
                
                # Build dynamic query
                conditions = ["availability = true"]
                params = []
                
                # Filter by product type
                if product_type:
                    types = [t.strip() for t in product_type.split(',')]
                    type_conditions = " OR ".join(["LOWER(category) LIKE %s"] * len(types))
                    conditions.append(f"({type_conditions})")
                    for ptype in types:
                        params.append(f"%{ptype.lower()}%")
                
                # Filter by color
                if ogcolor:
                    hex_color = f"#{ogcolor}" if not ogcolor.startswith('#') else ogcolor
                    conditions.append("hex_color ILIKE %s")
                    params.append(f"%{hex_color}%")
                
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
                    SELECT id, name, brand, category, color, hex_color, price,
                           description, image_url, product_url, undertone, shade_name
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
                        "image_url": row['image_url'] or f"https://via.placeholder.com/150/FF69B4/FFFFFF?text=Product",
                        "mst": mst or "Universal",
                        "desc": row['description'] or f"Beautiful {row['category'] or 'makeup product'}",
                        "category": row['category'],
                        "color": row['color'],
                        "hex_color": row['hex_color'],
                        "undertone": row['undertone'],
                        "shade_name": row['shade_name'],
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
                    "database_source": "neon_perfect_unified_makeup"
                }
                
            except Exception as e:
                print(f"Error fetching makeup data: {e}")
                return _get_fallback_makeup_data(page, limit)
        
        def _get_fallback_makeup_data(page: int, limit: int):
            """Fallback makeup data"""
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
        
        @app.get("/apparel")
        def get_apparel_data(
            gender: Optional[str] = None,
            color: Optional[str] = None,
            page: int = 1,
            limit: int = 24,
            occasion: Optional[str] = None
        ):
            """Get real outfit products from Neon database"""
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
                    conditions.append("LOWER(color) LIKE %s")
                    params.append(f"%{color.lower()}%")
                
                # Filter by occasion
                if occasion:
                    conditions.append("LOWER(occasion) LIKE %s")
                    params.append(f"%{occasion.lower()}%")
                
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
                    SELECT id, name, brand, category, color, hex_color, price,
                           gender, occasion, season, description, image_url, product_url
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
                        "Image URL": row['image_url'] or f"https://via.placeholder.com/150/FF6B6B/FFFFFF?text=Outfit",
                        "Product Type": row['category'] or "Clothing",
                        "baseColour": row['color'] or "Multi",
                        "brand": row['brand'] or "Unknown Brand",
                        "gender": row['gender'] or "Unisex",
                        "category": row['category'],
                        "hex_color": row['hex_color'],
                        "occasion": row['occasion'],
                        "season": row['season'],
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
                    "database_source": "neon_perfect_unified_outfits"
                }
                
            except Exception as e:
                print(f"Error fetching apparel data: {e}")
                return _get_fallback_apparel_data(page, limit)
        
        def _get_fallback_apparel_data(page: int, limit: int):
            """Fallback apparel data"""
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
        
        @app.get("/api/color-recommendations")
        def get_color_recommendations_backup(skin_tone: Optional[str] = None):
            """Enhanced color recommendations from database"""
            if not skin_tone:
                return {"error": "skin_tone parameter required"}
                
            try:
                conn = get_db_connection()
                if not conn:
                    return {"colors": [], "message": "Database unavailable"}
                
                cursor = conn.cursor()
                
                # Get color palette from database based on skin tone
                palette_query = """
                    SELECT flattering_colors, colors_to_avoid, description
                    FROM color_palettes 
                    WHERE LOWER(skin_tone) LIKE %s
                    LIMIT 1
                """
                cursor.execute(palette_query, [f"%{skin_tone.lower()}%"])
                result = cursor.fetchone()
                
                if result and result['flattering_colors']:
                    colors = result['flattering_colors']
                    return {
                        "colors_that_suit": colors,
                        "colors_to_avoid": result['colors_to_avoid'] or [],
                        "seasonal_type": skin_tone,
                        "description": result['description'],
                        "database_source": "neon_color_palettes"
                    }
                else:
                    # Fallback colors
                    fallback_colors = [
                        {"name": "Navy Blue", "hex": "#000080"},
                        {"name": "Forest Green", "hex": "#228B22"},
                        {"name": "Burgundy", "hex": "#800020"},
                        {"name": "Charcoal Gray", "hex": "#36454F"},
                        {"name": "Cream White", "hex": "#F5F5DC"}
                    ]
                    return {
                        "colors_that_suit": fallback_colors,
                        "seasonal_type": skin_tone,
                        "database_source": "fallback"
                    }
                
                conn.close()
                
            except Exception as e:
                print(f"Error getting color recommendations: {e}")
                return {"colors": [], "error": str(e)}
        
        # Add missing enhanced endpoints for product recommendations
        @app.get("/products-by-skin-analysis")
        def get_products_by_skin_analysis(
            monk_skin_tone: str = Query(..., description="Monk skin tone ID (e.g., Monk05)"),
            undertone: Optional[str] = Query(None, description="Skin undertone: warm, cool, neutral"),
            seasonal_type: Optional[str] = Query(None, description="Seasonal color type"),
            product_category: str = Query("both", description="Product category: makeup, outfit, both"),
            page: int = Query(1, ge=1),
            limit: int = Query(24, ge=1, le=100)
        ):
            """Get personalized product recommendations based on complete skin analysis"""
            try:
                conn = get_db_connection()
                if not conn:
                    return {"error": "Database connection failed", "data": []}
                
                cursor = conn.cursor()
                recommendations = {}
                
                # Get makeup recommendations if requested
                if product_category in ["makeup", "both"]:
                    makeup_conditions = ["availability = true"]
                    makeup_params = []
                    
                    # Filter by undertone compatibility for makeup
                    if undertone:
                        makeup_conditions.append("(undertone IS NULL OR LOWER(undertone) = %s OR undertone = 'neutral')")
                        makeup_params.append(undertone.lower())
                    
                    makeup_query = f"""
                        SELECT id, name, brand, category, color, hex_color, price,
                               description, image_url, undertone, shade_name
                        FROM perfect_unified_makeup 
                        WHERE {' AND '.join(makeup_conditions)}
                        ORDER BY price ASC, brand
                        LIMIT %s
                    """
                    
                    cursor.execute(makeup_query, makeup_params + [limit // 2 if product_category == "both" else limit])
                    makeup_results = cursor.fetchall()
                    
                    makeup_products = []
                    for row in makeup_results:
                        product = {
                            "product_name": row['name'],
                            "brand": row['brand'],
                            "price": f"${float(row['price']):.2f}" if row['price'] else "N/A",
                            "image_url": row['image_url'] or f"https://via.placeholder.com/150/FF69B4/FFFFFF?text=Makeup",
                            "category": row['category'],
                            "color": row['color'],
                            "hex_color": row['hex_color'],
                            "undertone": row['undertone'],
                            "shade_name": row['shade_name'],
                            "desc": row['description'] or f"Perfect {row['category']} for your skin tone",
                            "mst": monk_skin_tone,
                            "id": row['id'],
                            "product_type": "makeup"
                        }
                        makeup_products.append(product)
                    
                    recommendations["makeup"] = makeup_products
                
                # Get outfit recommendations if requested
                if product_category in ["outfit", "both"]:
                    outfit_conditions = ["availability = true"]
                    outfit_params = []
                    
                    outfit_query = f"""
                        SELECT id, name, brand, category, color, price,
                               description, image_url, gender, occasion, season
                        FROM perfect_unified_outfits 
                        WHERE {' AND '.join(outfit_conditions)}
                        ORDER BY price ASC, brand
                        LIMIT %s
                    """
                    
                    cursor.execute(outfit_query, outfit_params + [limit // 2 if product_category == "both" else limit])
                    outfit_results = cursor.fetchall()
                    
                    outfit_products = []
                    for row in outfit_results:
                        product = {
                            "Product Name": row['name'],
                            "brand": row['brand'],
                            "Price": f"${float(row['price']):.2f}" if row['price'] else "N/A",
                            "Image URL": row['image_url'] or f"https://via.placeholder.com/150/FF6B6B/FFFFFF?text=Outfit",
                            "Product Type": row['category'],
                            "baseColour": row['color'],
                            "gender": row['gender'],
                            "occasion": row['occasion'],
                            "season": row['season'],
                            "desc": row['description'] or f"Stylish {row['category']} perfect for your style",
                            "id": row['id'],
                            "product_type": "outfit"
                        }
                        outfit_products.append(product)
                    
                    recommendations["outfit"] = outfit_products
                
                conn.close()
                
                return {
                    "recommendations": recommendations,
                    "skin_analysis": {
                        "monk_skin_tone": monk_skin_tone,
                        "undertone": undertone,
                        "seasonal_type": seasonal_type
                    },
                    "total_products": sum(len(products) for products in recommendations.values()),
                    "database_source": "neon_personalized_recommendations"
                }
                
            except Exception as e:
                logger.error(f"Error getting personalized recommendations: {e}")
                return {"error": str(e), "data": []}
        
        @app.get("/search-products")
        def search_products(
            query: str = Query(..., min_length=2, description="Search query"),
            category: Optional[str] = Query(None, description="Product category: makeup, outfit"),
            page: int = Query(1, ge=1),
            limit: int = Query(24, ge=1, le=100)
        ):
            """Search products across makeup and outfit databases"""
            try:
                conn = get_db_connection()
                if not conn:
                    return {"error": "Database connection failed", "results": []}
                
                cursor = conn.cursor()
                all_results = []
                
                search_term = f"%{query.lower()}%"
                offset = (page - 1) * limit
                
                # Search makeup products
                if not category or category.lower() == "makeup":
                    makeup_query = """
                        SELECT 'makeup' as source_table, id, name, brand, category, 
                               color, price, description, image_url
                        FROM perfect_unified_makeup 
                        WHERE availability = true AND (
                            LOWER(name) LIKE %s OR 
                            LOWER(brand) LIKE %s OR 
                            LOWER(category) LIKE %s OR
                            LOWER(description) LIKE %s
                        )
                        ORDER BY 
                            CASE 
                                WHEN LOWER(name) LIKE %s THEN 1
                                WHEN LOWER(brand) LIKE %s THEN 2
                                ELSE 3
                            END,
                            price ASC
                    """
                    
                    cursor.execute(makeup_query, [search_term] * 6)
                    makeup_results = cursor.fetchall()
                    
                    for row in makeup_results:
                        result = {
                            "product_name": row['name'],
                            "brand": row['brand'],
                            "price": f"${float(row['price']):.2f}" if row['price'] else "N/A",
                            "image_url": row['image_url'],
                            "category": row['category'],
                            "color": row['color'],
                            "desc": row['description'],
                            "product_type": "makeup",
                            "id": row['id']
                        }
                        all_results.append(result)
                
                # Search outfit products
                if not category or category.lower() == "outfit":
                    outfit_query = """
                        SELECT 'outfit' as source_table, id, name, brand, category,
                               color, price, description, image_url, gender
                        FROM perfect_unified_outfits 
                        WHERE availability = true AND (
                            LOWER(name) LIKE %s OR 
                            LOWER(brand) LIKE %s OR 
                            LOWER(category) LIKE %s OR
                            LOWER(description) LIKE %s
                        )
                        ORDER BY 
                            CASE 
                                WHEN LOWER(name) LIKE %s THEN 1
                                WHEN LOWER(brand) LIKE %s THEN 2
                                ELSE 3
                            END,
                            price ASC
                    """
                    
                    cursor.execute(outfit_query, [search_term] * 6)
                    outfit_results = cursor.fetchall()
                    
                    for row in outfit_results:
                        result = {
                            "Product Name": row['name'],
                            "brand": row['brand'],
                            "Price": f"${float(row['price']):.2f}" if row['price'] else "N/A",
                            "Image URL": row['image_url'],
                            "Product Type": row['category'],
                            "baseColour": row['color'],
                            "gender": row['gender'],
                            "desc": row['description'],
                            "product_type": "outfit",
                            "id": row['id']
                        }
                        all_results.append(result)
                
                conn.close()
                
                # Apply pagination to combined results
                total_results = len(all_results)
                paginated_results = all_results[offset:offset + limit]
                
                return {
                    "results": paginated_results,
                    "query": query,
                    "category": category,
                    "total_results": total_results,
                    "page": page,
                    "limit": limit,
                    "total_pages": math.ceil(total_results / limit)
                }
                
            except Exception as e:
                logger.error(f"Error searching products: {e}")
                return {"error": str(e), "results": []}
        
        @app.get("/health/database")
        def database_health_check():
            """Check database health and return counts"""
            try:
                conn = get_db_connection()
                if not conn:
                    return {
                        "status": "unhealthy",
                        "message": "Database connection failed",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                
                cursor = conn.cursor()
                
                # Check makeup products count
                cursor.execute("SELECT COUNT(*) FROM perfect_unified_makeup WHERE availability = true")
                makeup_count = cursor.fetchone()[0]
                
                # Check outfit products count
                cursor.execute("SELECT COUNT(*) FROM perfect_unified_outfits WHERE availability = true")
                outfit_count = cursor.fetchone()[0]
                
                # Check color palettes count
                try:
                    cursor.execute("SELECT COUNT(*) FROM color_palettes")
                    color_count = cursor.fetchone()[0]
                except:
                    color_count = 0
                
                conn.close()
                
                return {
                    "status": "healthy",
                    "database": "neon_postgresql",
                    "tables": {
                        "makeup_products": makeup_count,
                        "outfit_products": outfit_count,
                        "color_palettes": color_count
                    },
                    "total_products": makeup_count + outfit_count,
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:00Z"
                }
        
        # Enhanced color-palettes-db endpoint 
        @app.get("/color-palettes-db")
        def get_color_palettes_from_db(
            skin_tone: Optional[str] = Query(None, description="Skin tone or seasonal type"),
            limit: int = Query(100, ge=1, le=500)
        ):
            """Get color palettes from database based on skin tone"""
            try:
                conn = get_db_connection()
                if not conn:
                    return {"colors_that_suit": [], "colors_to_avoid": [], "message": "Database unavailable"}
                
                cursor = conn.cursor()
                
                # Try to get color palette from database
                if skin_tone:
                    palette_query = """
                        SELECT flattering_colors, colors_to_avoid, description, seasonal_type
                        FROM color_palettes 
                        WHERE LOWER(skin_tone) LIKE %s OR LOWER(seasonal_type) LIKE %s
                        LIMIT 1
                    """
                    cursor.execute(palette_query, [f"%{skin_tone.lower()}%", f"%{skin_tone.lower()}%"])
                    result = cursor.fetchone()
                    
                    if result and result['flattering_colors']:
                        flattering_colors = result['flattering_colors']
                        colors_to_avoid = result['colors_to_avoid'] or []
                        
                        conn.close()
                        return {
                            "colors_that_suit": flattering_colors[:limit],
                            "colors": flattering_colors[:limit],
                            "colors_to_avoid": colors_to_avoid,
                            "seasonal_type": result['seasonal_type'],
                            "monk_skin_tone": skin_tone,
                            "description": result['description'],
                            "message": f"Found {len(flattering_colors)} color recommendations from database",
                            "database_source": True
                        }
                
                # Fallback: return some default colors
                conn.close()
                
                default_colors = [
                    {"name": "Navy Blue", "hex": "#000080"},
                    {"name": "Forest Green", "hex": "#228B22"},
                    {"name": "Burgundy", "hex": "#800020"},
                    {"name": "Charcoal Gray", "hex": "#36454F"},
                    {"name": "Cream White", "hex": "#F5F5DC"},
                    {"name": "Deep Purple", "hex": "#483D8B"},
                    {"name": "Coral Pink", "hex": "#FF7F50"},
                    {"name": "Golden Yellow", "hex": "#FFD700"}
                ]
                
                return {
                    "colors_that_suit": default_colors,
                    "colors": default_colors,
                    "colors_to_avoid": [],
                    "seasonal_type": skin_tone or "Universal",
                    "message": "Showing default color recommendations",
                    "database_source": False
                }
                
            except Exception as e:
                logger.error(f"Error getting color palettes: {e}")
                return {"colors_that_suit": [], "colors_to_avoid": [], "error": str(e)}
        
        print("🚑 Created backup FastAPI app with working analyze-skin-tone endpoint")

# Launch FastAPI directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))  # HF default port
    print(f"🚀 Starting AI Fashion Backend on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
