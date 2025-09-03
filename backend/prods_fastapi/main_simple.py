# Simplified FastAPI application for Render deployment
from fastapi import FastAPI, Query, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import math
import os
from typing import List, Optional, Dict
import numpy as np
import cv2
from webcolors import hex_to_rgb, rgb_to_hex
import io
from PIL import Image
import logging
import random
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Fashion Backend",
    version="1.0.0",
    description="AI Fashion recommendation system with skin tone analysis"
)

# Configure CORS - specific origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://app.taddstechnology.com",
        "https://ai-fashion-backend-d9nj.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "accept",
        "accept-language",
        "content-language", 
        "content-type",
        "authorization",
        "x-requested-with"
    ],
    max_age=3600  # Cache preflight for 1 hour
)

# Monk skin tone scale - now loaded from database
def get_monk_skin_tones():
    """Get Monk skin tones from database."""
    try:
        # Database connection 
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://fashion_jvy9_user:0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh@dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com/fashion_jvy9"
        )
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            cursor = db.connection().connection.cursor()
            cursor.execute("SELECT monk_tone, hex_code FROM skin_tone_mappings ORDER BY monk_tone")
            mappings = cursor.fetchall()
            
            monk_tones = {}
            for row in mappings:
                # Convert Monk01 -> Monk 1 format
                display_name = row[0].replace('Monk0', 'Monk ').replace('Monk10', 'Monk 10')
                monk_tones[display_name] = row[1]
                
            if monk_tones:
                return monk_tones
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to load Monk skin tones from database: {e}")
    
    # Emergency fallback - minimal set
    return {
        'Monk 1': '#f6ede4',
        'Monk 5': '#d7bd96', 
        'Monk 10': '#292420'
    }

# Initialize monk tones on startup
MONK_SKIN_TONES = get_monk_skin_tones()

# Basic color mapping
color_mapping = {
    "Red": "Red",
    "Blue": "Blue", 
    "Green": "Green",
    "Black": "Black",
    "White": "White",
    "Pink": "Pink",
    "Yellow": "Yellow",
    "Purple": "Purple",
    "Orange": "Orange",
    "Brown": "Brown"
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

@app.get("/apparel")
def get_apparel(
    gender: str = Query(None),
    color: List[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100)
):
    """Get apparel products."""
    # Generate sample apparel
    brands = ["H&M", "Zara", "Nike", "Adidas", "Uniqlo", "Gap"]
    types = ["T-Shirt", "Jeans", "Dress", "Jacket", "Sweater", "Pants"]
    colors = ["Black", "White", "Blue", "Red", "Green", "Gray"]
    
    sample_data = []
    for i in range(50):
        brand = random.choice(brands)
        product_type = random.choice(types)
        base_color = random.choice(colors)
        price = f"${random.randint(20, 80)}.{random.randint(10, 99)}"
        
        sample_data.append({
            "Product Name": f"{brand} {product_type}",
            "Price": price,
            "Image URL": f"https://via.placeholder.com/150/{random.randint(100000, 999999)}/FFFFFF?text={product_type.replace(' ', '+')}",
            "Product Type": product_type,
            "baseColour": base_color,
            "brand": brand,
            "gender": gender or random.choice(["Men", "Women", "Unisex"])
        })
    
    # Apply pagination
    total_items = len(sample_data)
    total_pages = math.ceil(total_items / limit)
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_items)
    
    paginated_data = sample_data[start_idx:end_idx]
    
    return {
        "data": paginated_data,
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages
    }

@app.get("/api/color-recommendations")
def get_color_recommendations(
    skin_tone: str = Query(None),
    hex_color: str = Query(None),
    limit: int = Query(50, ge=10, le=100, description="Maximum number of colors to return")
):
    """Enhanced color recommendations combining multiple database tables."""
    try:
        # Database connection
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://fashion_jvy9_user:0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh@dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com/fashion_jvy9"
        )
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            all_colors = []
            seasonal_type = "Universal"
            sources_used = []
            
            if skin_tone:
                cursor = db.connection().connection.cursor()
                
                # Step 1: Get seasonal type mapping
                cursor.execute("""
                    SELECT seasonal_type 
                    FROM skin_tone_mappings 
                    WHERE monk_tone = %s
                """, [skin_tone])
                
                mapping = cursor.fetchone()
                if mapping:
                    seasonal_type = mapping[0]
                    logger.info(f"Found seasonal type: {seasonal_type} for {skin_tone}")
                
                # Step 2: Get colors from color_palettes (seasonal-specific)
                if seasonal_type != "Universal":
                    cursor.execute("""
                        SELECT flattering_colors 
                        FROM color_palettes 
                        WHERE skin_tone = %s
                    """, [seasonal_type])
                    
                    palette = cursor.fetchone()
                    if palette and palette[0]:
                        flattering_colors = palette[0] if isinstance(palette[0], list) else json.loads(palette[0])
                        for color in flattering_colors:
                            all_colors.append({
                                "name": color.get("name", "Unknown Color"),
                                "hex": color.get("hex", "#000000"),
                                "source": "seasonal_palette",
                                "seasonal_type": seasonal_type
                            })
                        sources_used.append(f"color_palettes ({len(flattering_colors)} colors)")
                        logger.info(f"Added {len(flattering_colors)} colors from color_palettes")
                
                # Step 3: Get colors from comprehensive_colors (Monk tone matching)
                cursor.execute("""
                    SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                    FROM comprehensive_colors 
                    WHERE monk_tones::text LIKE %s
                    AND hex_code IS NOT NULL
                    AND color_name IS NOT NULL
                    ORDER BY color_name
                    LIMIT 40
                """, [f'%{skin_tone}%'])
                
                comp_results = cursor.fetchall()
                for row in comp_results:
                    # Avoid duplicates by checking hex codes
                    if not any(color["hex"].lower() == row[0].lower() for color in all_colors):
                        all_colors.append({
                            "name": row[1],
                            "hex": row[0],
                            "source": "comprehensive_colors",
                            "color_family": row[2] or "unknown",
                            "brightness_level": row[3] or "medium",
                            "monk_compatible": skin_tone
                        })
                
                if comp_results:
                    unique_comp_colors = len([row for row in comp_results if not any(color["hex"].lower() == row[0].lower() for color in all_colors[:len(all_colors)-len(comp_results)])])
                    sources_used.append(f"comprehensive_colors ({len(comp_results)} total, {unique_comp_colors} unique)")
                    logger.info(f"Added {len(comp_results)} colors from comprehensive_colors")
                
                # Step 4: Get additional colors from main colors table (seasonal matching)
                if seasonal_type != "Universal":
                    cursor.execute("""
                        SELECT DISTINCT hex_code, color_name, seasonal_palette, category, suitable_skin_tone
                        FROM colors 
                        WHERE (seasonal_palette = %s OR suitable_skin_tone LIKE %s)
                        AND category = 'recommended'
                        AND hex_code IS NOT NULL
                        AND color_name IS NOT NULL
                        ORDER BY color_name
                        LIMIT 30
                    """, [seasonal_type, f'%{skin_tone}%'])
                    
                    colors_results = cursor.fetchall()
                    for row in colors_results:
                        # Avoid duplicates
                        if not any(color["hex"].lower() == row[0].lower() for color in all_colors):
                            all_colors.append({
                                "name": row[1],
                                "hex": row[0],
                                "source": "colors_table",
                                "seasonal_palette": row[2] or seasonal_type,
                                "category": row[3],
                                "suitable_skin_tone": row[4] or "universal"
                            })
                    
                    if colors_results:
                        unique_colors_count = len([row for row in colors_results if not any(color["hex"].lower() == row[0].lower() for color in all_colors[:len(all_colors)-len(colors_results)])])
                        sources_used.append(f"colors table ({len(colors_results)} total, {unique_colors_count} unique)")
                        logger.info(f"Added {len(colors_results)} colors from colors table")
                
                # Step 5: Get general color suggestions as additional options
                # Note: color_suggestions table may not exist or have different schema
                try:
                    cursor.execute("""
                        SELECT DISTINCT suitable_colors_text as color_name, skin_tone as suggested_for
                        FROM color_suggestions 
                        WHERE suitable_colors_text IS NOT NULL
                        ORDER BY skin_tone
                        LIMIT 20
                    """)
                    
                    suggestions_results = cursor.fetchall()
                    for row in suggestions_results:
                        # Parse comma-separated color names
                        color_names = [name.strip() for name in row[0].split(',')]
                        for color_name in color_names:
                            # Generate a sample hex color for display (this would be better with actual hex codes)
                            sample_hex = "#" + format(abs(hash(color_name)) % 16777216, '06x')
                            
                            if not any(color["name"].lower() == color_name.lower() for color in all_colors):
                                all_colors.append({
                                    "name": color_name.title(),
                                    "hex": sample_hex,
                                    "source": "color_suggestions",
                                    "suggested_for": row[1] or "general"
                                })
                    
                    if suggestions_results:
                        total_suggestion_colors = sum(len(row[0].split(',')) for row in suggestions_results)
                        sources_used.append(f"color_suggestions ({total_suggestion_colors} colors from {len(suggestions_results)} records)")
                        logger.info(f"Added colors from color_suggestions table")
                        
                except Exception as e:
                    logger.info(f"Skipping color_suggestions table (may not exist): {e}")
            
            # Default/Universal colors if no skin tone provided or limited results
            if len(all_colors) < 10:
                default_query = text("""
                    SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                    FROM comprehensive_colors 
                    WHERE color_family IN ('blue', 'green', 'red', 'purple', 'neutral', 'brown', 'pink')
                    AND brightness_level IN ('medium', 'dark', 'light')
                    AND hex_code IS NOT NULL
                    AND color_name IS NOT NULL
                    ORDER BY color_name
                    LIMIT 25
                """)
                
                default_result = db.execute(default_query)
                default_colors = default_result.fetchall()
                
                for row in default_colors:
                    # Avoid duplicates
                    if not any(color["hex"].lower() == row[0].lower() for color in all_colors):
                        all_colors.append({
                            "name": row[1],
                            "hex": row[0],
                            "source": "universal_colors",
                            "color_family": row[2] or "unknown",
                            "brightness_level": row[3] or "medium"
                        })
                
                if default_colors:
                    sources_used.append(f"universal_colors ({len(default_colors)} colors)")
                    logger.info(f"Added {len(default_colors)} universal colors")
            
            # Ultimate fallback if database queries fail completely
            if not all_colors:
                all_colors = [
                    {"name": "Navy Blue", "hex": "#000080", "source": "fallback"},
                    {"name": "Forest Green", "hex": "#228B22", "source": "fallback"},
                    {"name": "Burgundy", "hex": "#800020", "source": "fallback"},
                    {"name": "Charcoal Gray", "hex": "#36454F", "source": "fallback"},
                    {"name": "Cream White", "hex": "#F5F5DC", "source": "fallback"},
                    {"name": "Soft Pink", "hex": "#FFB6C1", "source": "fallback"},
                    {"name": "Royal Purple", "hex": "#663399", "source": "fallback"},
                    {"name": "Emerald Green", "hex": "#50C878", "source": "fallback"},
                    {"name": "Deep Orange", "hex": "#FF6600", "source": "fallback"},
                    {"name": "Chocolate Brown", "hex": "#8B4513", "source": "fallback"}
                ]
                sources_used.append("hardcoded_fallback (10 colors)")
            
            # Apply the limit while preserving diversity
            if len(all_colors) > limit:
                # Prioritize colors from seasonal palettes and comprehensive colors
                priority_colors = [c for c in all_colors if c["source"] in ["seasonal_palette", "comprehensive_colors"]]
                other_colors = [c for c in all_colors if c["source"] not in ["seasonal_palette", "comprehensive_colors"]]
                
                # Take priority colors first, then fill with others
                final_colors = priority_colors[:limit]
                remaining_slots = limit - len(final_colors)
                if remaining_slots > 0:
                    final_colors.extend(other_colors[:remaining_slots])
            else:
                final_colors = all_colors
            
            logger.info(f"Returning {len(final_colors)} colors from {len(sources_used)} sources")
            
            return {
                "colors": final_colors,
                "total_colors": len(final_colors),
                "seasonal_type": seasonal_type,
                "monk_skin_tone": skin_tone,
                "sources_used": sources_used,
                "description": f"Enhanced color recommendations for {skin_tone or 'universal skin tone'} from multiple database sources",
                "query_limit": limit,
                "database_tables_queried": ["skin_tone_mappings", "color_palettes", "comprehensive_colors", "colors", "color_suggestions"]
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error in enhanced color recommendations: {e}")
        # Comprehensive fallback colors
        fallback_colors = [
            {"name": "Navy Blue", "hex": "#000080", "source": "fallback"},
            {"name": "Forest Green", "hex": "#228B22", "source": "fallback"},
            {"name": "Burgundy", "hex": "#800020", "source": "fallback"},
            {"name": "Charcoal Gray", "hex": "#36454F", "source": "fallback"},
            {"name": "Cream White", "hex": "#F5F5DC", "source": "fallback"},
            {"name": "Soft Pink", "hex": "#FFB6C1", "source": "fallback"},
            {"name": "Royal Purple", "hex": "#663399", "source": "fallback"},
            {"name": "Emerald Green", "hex": "#50C878", "source": "fallback"},
            {"name": "Deep Orange", "hex": "#FF6600", "source": "fallback"},
            {"name": "Chocolate Brown", "hex": "#8B4513", "source": "fallback"},
            {"name": "Crimson Red", "hex": "#DC143C", "source": "fallback"},
            {"name": "Golden Yellow", "hex": "#FFD700", "source": "fallback"},
            {"name": "Teal Blue", "hex": "#008080", "source": "fallback"},
            {"name": "Coral Pink", "hex": "#FF7F50", "source": "fallback"},
            {"name": "Olive Green", "hex": "#808000", "source": "fallback"}
        ]
        
        return {
            "colors": fallback_colors[:limit] if len(fallback_colors) > limit else fallback_colors,
            "total_colors": min(len(fallback_colors), limit),
            "seasonal_type": "Universal",
            "monk_skin_tone": skin_tone,
            "sources_used": ["hardcoded_fallback_error"],
            "description": f"Fallback color recommendations due to database error: {str(e)}",
            "error": str(e)
        }

def apply_lighting_correction(image_array: np.ndarray) -> np.ndarray:
    """Apply CLAHE and lighting correction for better skin tone detection."""
    try:
        # Convert to LAB color space for better lighting correction
        lab_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_image)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_channel_corrected = clahe.apply(l_channel)
        
        # Merge channels back
        corrected_lab = cv2.merge([l_channel_corrected, a_channel, b_channel])
        
        # Convert back to RGB
        corrected_rgb = cv2.cvtColor(corrected_lab, cv2.COLOR_LAB2RGB)
        
        # Apply gentle gamma correction for very light skin tones
        gamma = 1.2  # Slightly brighten to better detect light skin
        corrected_rgb = np.power(corrected_rgb / 255.0, gamma) * 255.0
        corrected_rgb = np.clip(corrected_rgb, 0, 255).astype(np.uint8)
        
        return corrected_rgb
        
    except Exception as e:
        logger.warning(f"Lighting correction failed: {e}, using original image")
        return image_array

def extract_multi_region_colors(image_array: np.ndarray) -> List[np.ndarray]:
    """Extract skin colors from multiple face regions for better accuracy."""
    h, w = image_array.shape[:2]
    
    # Define multiple face regions (optimized for light skin detection)
    regions = [
        # Forehead (most reliable for light skin)
        image_array[h//8:h//3, w//3:2*w//3],
        # Upper cheeks
        image_array[h//3:h//2, w//4:3*w//4],
        # Nose bridge
        image_array[h//3:2*h//3, 2*w//5:3*w//5],
        # Lower cheeks
        image_array[h//2:2*h//3, w//4:3*w//4],
        # Chin area
        image_array[2*h//3:5*h//6, 2*w//5:3*w//5]
    ]
    
    region_colors = []
    
    for region in regions:
        if region.size > 100:  # Ensure region has enough pixels
            # For light skin, focus on brighter pixels
            region_gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
            
            # Use adaptive thresholding for light skin detection
            light_threshold = np.percentile(region_gray, 75)  # Top 25% brightest pixels
            light_mask = region_gray > light_threshold
            
            if np.sum(light_mask) > 50:  # Enough light pixels
                light_pixels = region[light_mask]
                region_color = np.mean(light_pixels, axis=0)
                region_colors.append(region_color)
    
    return region_colors

def calculate_confidence_score(image_array: np.ndarray, final_color: np.ndarray, closest_distance: float) -> float:
    """Calculate confidence score based on multiple factors."""
    try:
        # Base confidence from color distance (closer = higher confidence)
        distance_confidence = max(0, 1 - (closest_distance / 200))  # Normalize to 0-1
        
        # Check image quality (sharpness)
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_confidence = min(1.0, sharpness / 500)  # Good sharpness > 500
        
        # Check brightness consistency (for light skin detection)
        brightness_std = np.std(final_color)
        consistency_confidence = max(0, 1 - (brightness_std / 50))  # Lower std = more consistent
        
        # Overall brightness check (light skin should be bright)
        avg_brightness = np.mean(final_color)
        if avg_brightness > 200:  # Very light skin
            brightness_bonus = 0.2
        elif avg_brightness > 180:  # Light skin
            brightness_bonus = 0.1
        else:
            brightness_bonus = 0
        
        # Weighted combination
        final_confidence = (
            distance_confidence * 0.4 +
            sharpness_confidence * 0.3 +
            consistency_confidence * 0.3 +
            brightness_bonus
        )
        
        return min(1.0, final_confidence)  # Cap at 1.0
        
    except Exception as e:
        logger.warning(f"Confidence calculation failed: {e}")
        return 0.5  # Default confidence

def find_closest_monk_tone_enhanced(rgb_color: np.ndarray) -> tuple:
    """Enhanced Monk tone matching with better detection for all skin tones."""
    min_distance = float('inf')
    closest_monk = "Monk 5"  # Default to medium tone
    
    # Calculate average brightness
    avg_brightness = np.mean(rgb_color)
    
    # Enhanced distance calculation for all skin tones
    for monk_name, hex_color in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(hex_color))
        
        # Standard Euclidean distance
        euclidean_distance = np.sqrt(np.sum((rgb_color - monk_rgb) ** 2))
        
        # Brightness-weighted distance (favor similar brightness levels)
        brightness_diff = abs(avg_brightness - np.mean(monk_rgb))
        
        # Adaptive weighting based on brightness ranges
        if avg_brightness > 220:  # Very light skin
            combined_distance = euclidean_distance * 0.3 + brightness_diff * 1.5
        elif avg_brightness > 180:  # Light skin
            combined_distance = euclidean_distance * 0.6 + brightness_diff * 1.0
        elif avg_brightness > 120:  # Medium skin
            combined_distance = euclidean_distance * 0.8 + brightness_diff * 0.8
        elif avg_brightness > 80:   # Dark skin
            combined_distance = euclidean_distance * 0.9 + brightness_diff * 0.5
        else:  # Very dark skin (black)
            combined_distance = euclidean_distance * 1.0 + brightness_diff * 0.3
        
        if combined_distance < min_distance:
            min_distance = combined_distance
            closest_monk = monk_name
    
    return closest_monk, min_distance

def analyze_skin_tone_enhanced(image_array: np.ndarray) -> Dict:
    """Enhanced skin tone analysis with LAB color space, CLAHE, multi-region analysis, and confidence scoring."""
    try:
        logger.info("Starting enhanced skin tone analysis...")
        
        # Step 1: Apply lighting correction
        corrected_image = apply_lighting_correction(image_array)
        
        # Step 2: Extract colors from multiple regions
        region_colors = extract_multi_region_colors(corrected_image)
        
        if not region_colors:
            # Fallback to center region if no regions found
            h, w = corrected_image.shape[:2]
            center_region = corrected_image[h//4:3*h//4, w//4:3*w//4]
            avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
        else:
            # Step 3: Calculate weighted average of region colors
            region_colors_array = np.array(region_colors)
            
            # Weight regions by brightness for light skin detection
            brightness_weights = np.mean(region_colors_array, axis=1)
            
            # Normalize weights
            if np.sum(brightness_weights) > 0:
                brightness_weights = brightness_weights / np.sum(brightness_weights)
                avg_color = np.average(region_colors_array, axis=0, weights=brightness_weights)
            else:
                avg_color = np.mean(region_colors_array, axis=0)
        
        # Step 4: Convert to LAB color space for final analysis
        lab_color = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_RGB2LAB)[0][0]
        
        # Step 5: Find closest Monk tone with enhanced algorithm
        closest_monk, min_distance = find_closest_monk_tone_enhanced(avg_color)
        
        # Step 6: Calculate confidence score
        confidence = calculate_confidence_score(image_array, avg_color, min_distance)
        
        # Format response
        monk_number = closest_monk.split()[1]
        monk_id = f"Monk{monk_number.zfill(2)}"
        derived_hex = rgb_to_hex((int(avg_color[0]), int(avg_color[1]), int(avg_color[2])))
        
        logger.info(f"Enhanced analysis result: {monk_id}, confidence: {confidence:.2f}")
        
        return {
            'monk_skin_tone': monk_id,
            'monk_tone_display': closest_monk,
            'monk_hex': MONK_SKIN_TONES[closest_monk],
            'derived_hex_code': derived_hex,
            'dominant_rgb': avg_color.astype(int).tolist(),
            'confidence': round(confidence, 2),
            'success': True,
            'analysis_method': 'enhanced_lab_clahe_multi_region',
            'regions_analyzed': len(region_colors) if region_colors else 1
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced skin tone analysis: {e}")
        # Try to get fallback from database
        try:
            DATABASE_URL = os.getenv(
                "DATABASE_URL", 
                "postgresql://fashion_jvy9_user:0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh@dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com/fashion_jvy9"
            )
            engine = create_engine(DATABASE_URL)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            try:
                cursor = db.connection().connection.cursor()
                cursor.execute("SELECT monk_tone, hex_code FROM skin_tone_mappings WHERE monk_tone IN ('Monk02', 'Monk03') ORDER BY monk_tone LIMIT 1")
                fallback_data = cursor.fetchone()
                if fallback_data:
                    fallback_rgb = list(hex_to_rgb(fallback_data[1]))
                    return {
                        'monk_skin_tone': fallback_data[0],
                        'monk_tone_display': fallback_data[0].replace('Monk0', 'Monk '),
                        'monk_hex': fallback_data[1],
                        'derived_hex_code': fallback_data[1],
                        'dominant_rgb': fallback_rgb,
                        'confidence': 0.3,
                        'success': False,
                        'error': f'Enhanced analysis error, database fallback: {str(e)}'
                    }
            finally:
                db.close()
        except Exception:
            pass
            
        # Ultimate fallback
        return {
            'monk_skin_tone': 'Monk02',  # Default to lighter tone for errors
            'monk_tone_display': 'Monk 2',
            'monk_hex': '#f3e7db',
            'derived_hex_code': '#f3e7db',
            'dominant_rgb': [243, 231, 219],
            'confidence': 0.3,
            'success': False,
            'error': f'Ultimate fallback: {str(e)}'
        }

# Keep the simple version as fallback
def analyze_skin_tone_simple(image_array: np.ndarray) -> Dict:
    """Simplified skin tone analysis (fallback method)."""
    try:
        # Get average color of the image center
        h, w = image_array.shape[:2]
        center_region = image_array[h//4:3*h//4, w//4:3*w//4]
        
        # Calculate average RGB
        avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
        
        # Find closest Monk skin tone
        min_distance = float('inf')
        closest_monk = "Monk 2"  # Default to lighter tone
        
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
            'confidence': 0.6,
            'success': True,
            'analysis_method': 'simple_rgb'
        }
        
    except Exception as e:
        logger.error(f"Error in simple skin tone analysis: {e}")
        return {
            'monk_skin_tone': 'Monk02',
            'monk_tone_display': 'Monk 2',
            'monk_hex': MONK_SKIN_TONES['Monk 2'],
            'derived_hex_code': '#f3e7db',
            'dominant_rgb': [243, 231, 219],
            'confidence': 0.3,
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
        
        # Try enhanced analysis first, fallback to simple if it fails
        try:
            result = analyze_skin_tone_enhanced(image_array)
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"Enhanced analysis failed: {e}, falling back to simple analysis")
        
        # Fallback to simple analysis
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

# Additional endpoints for compatibility
@app.get("/products")
def get_products(product_type: str = Query(None), random: bool = Query(False)):
    """Get H&M style products."""
    return []

@app.get("/makeup-types")
def get_makeup_types():
    """Get available makeup types."""
    return {
        "types": ["Foundation", "Concealer", "Lipstick", "Mascara", "Blush", "Highlighter", "Eyeshadow"]
    }

@app.get("/api/colors/all")
def get_all_colors(
    limit: int = Query(500, ge=10, le=1000, description="Maximum number of colors to return"),
    skin_tone: Optional[str] = Query(None, description="Filter by skin tone"),
    category: Optional[str] = Query(None, description="Filter by category (recommended/avoid)")
):
    """Get all colors with optional filters from database."""
    logger.info(f"Get all colors request: limit={limit}, skin_tone={skin_tone}, category={category}")
    
    try:
        # Database connection
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://fashion_jvy9_user:0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh@dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com/fashion_jvy9"
        )
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            cursor = db.connection().connection.cursor()
            
            # Build query based on filters
            base_query = """
                SELECT DISTINCT hex_code, color_name, 
                       COALESCE(color_family, 'unknown') as color_family,
                       COALESCE(brightness_level, 'medium') as brightness_level,
                       monk_tones
                FROM comprehensive_colors 
                WHERE hex_code IS NOT NULL AND color_name IS NOT NULL
            """
            
            params = []
            
            # Add skin tone filter
            if skin_tone:
                base_query += " AND monk_tones::text LIKE %s"
                params.append(f'%{skin_tone}%')
            
            # Add ordering and limit
            base_query += " ORDER BY color_name LIMIT %s"
            params.append(limit)
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            # Format results
            colors = []
            for row in results:
                colors.append({
                    "hex_code": row[0],
                    "color_name": row[1],
                    "color_family": row[2],
                    "brightness_level": row[3],
                    "monk_tones": row[4],
                    "category": category or "recommended",
                    "source": "comprehensive_colors"
                })
            
            logger.info(f"Returning {len(colors)} colors from comprehensive_colors table")
            
            return {
                "colors": colors,
                "total_colors": len(colors),
                "filters_applied": {
                    "skin_tone": skin_tone,
                    "category": category,
                    "limit": limit
                },
                "data_source": "comprehensive_colors",
                "message": f"Retrieved {len(colors)} colors from database"
            }
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in get_all_colors: {e}")
        # Fallback colors
        fallback_colors = [
            {"hex_code": "#000080", "color_name": "Navy Blue", "color_family": "blue", "brightness_level": "dark", "category": "recommended", "source": "fallback"},
            {"hex_code": "#228B22", "color_name": "Forest Green", "color_family": "green", "brightness_level": "medium", "category": "recommended", "source": "fallback"},
            {"hex_code": "#800020", "color_name": "Burgundy", "color_family": "red", "brightness_level": "dark", "category": "recommended", "source": "fallback"},
            {"hex_code": "#36454F", "color_name": "Charcoal Gray", "color_family": "neutral", "brightness_level": "dark", "category": "recommended", "source": "fallback"},
            {"hex_code": "#F5F5DC", "color_name": "Cream White", "color_family": "neutral", "brightness_level": "light", "category": "recommended", "source": "fallback"},
        ]
        
        return {
            "colors": fallback_colors[:limit],
            "total_colors": min(len(fallback_colors), limit),
            "filters_applied": {"skin_tone": skin_tone, "category": category, "limit": limit},
            "data_source": "fallback",
            "message": f"Fallback colors due to database error: {str(e)}",
            "error": str(e)
        }

@app.get("/api/color-palettes-db")
def get_color_palettes_db(
    skin_tone: Optional[str] = Query(None, description="Monk skin tone (e.g., Monk05) or seasonal type"),
    limit: int = Query(500, ge=10, le=1000, description="Number of colors to return")
):
    """Get color palettes from database based on skin tone mapping."""
    logger.info(f"Color palette request: skin_tone={skin_tone}, limit={limit}")
    
    if not skin_tone:
        raise HTTPException(status_code=400, detail="skin_tone parameter is required")
    
    try:
        # Database connection
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://fashion_jvy9_user:0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh@dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com/fashion_jvy9"
        )
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            cursor = db.connection().connection.cursor()
            
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
            
            # Check if it's a Monk tone and map it to seasonal type
            if skin_tone in seasonal_type_map:
                seasonal_type = seasonal_type_map[skin_tone]
            
            # Try to get from skin_tone_mappings table first
            if "Monk" in skin_tone:
                cursor.execute("""
                    SELECT seasonal_type 
                    FROM skin_tone_mappings 
                    WHERE monk_tone = %s
                """, [skin_tone])
                
                mapping_result = cursor.fetchone()
                if mapping_result:
                    seasonal_type = mapping_result[0]
                    logger.info(f"Found seasonal type from mapping: {seasonal_type} for {skin_tone}")
            
            # Step 2: Get colors from comprehensive_colors table (Monk tone specific)
            all_colors = []
            if "Monk" in skin_tone:
                cursor.execute("""
                    SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                    FROM comprehensive_colors 
                    WHERE monk_tones::text LIKE %s
                    AND hex_code IS NOT NULL
                    AND color_name IS NOT NULL
                    ORDER BY color_name
                    LIMIT %s
                """, [f'%{skin_tone}%', limit])
                
                monk_results = cursor.fetchall()
                for row in monk_results:
                    all_colors.append({
                        "name": row[1],
                        "hex": row[0],
                        "color_family": row[2] or "unknown",
                        "brightness_level": row[3] or "medium",
                        "source": "comprehensive_colors"
                    })
                
                logger.info(f"Added {len(monk_results)} colors from comprehensive_colors for {skin_tone}")
            
            # Step 3: Get colors from color_palettes table (seasonal type specific)
            if seasonal_type != skin_tone and seasonal_type != "Universal":
                try:
                    cursor.execute("""
                        SELECT flattering_colors, colors_to_avoid
                        FROM color_palettes 
                        WHERE skin_tone = %s
                    """, [seasonal_type])
                    
                    palette_result = cursor.fetchone()
                    if palette_result and palette_result[0]:
                        flattering_colors = palette_result[0] if isinstance(palette_result[0], list) else json.loads(palette_result[0])
                        for color in flattering_colors:
                            # Avoid duplicates
                            if not any(existing["hex"].lower() == color.get("hex", "").lower() for existing in all_colors):
                                all_colors.append({
                                    "name": color.get("name", "Unknown Color"),
                                    "hex": color.get("hex", "#000000"),
                                    "source": "seasonal_palette",
                                    "seasonal_type": seasonal_type
                                })
                        
                        logger.info(f"Added {len(flattering_colors)} colors from color_palettes for {seasonal_type}")
                except Exception as e:
                    logger.info(f"Could not fetch from color_palettes table: {e}")
            
            # Step 4: Get additional colors from main colors table
            try:
                cursor.execute("""
                    SELECT DISTINCT hex_code, color_name, seasonal_palette, category
                    FROM colors 
                    WHERE (seasonal_palette = %s OR suitable_skin_tone LIKE %s)
                    AND category = 'recommended'
                    AND hex_code IS NOT NULL
                    AND color_name IS NOT NULL
                    ORDER BY color_name
                    LIMIT 50
                """, [seasonal_type, f'%{skin_tone}%'])
                
                colors_results = cursor.fetchall()
                for row in colors_results:
                    # Avoid duplicates
                    if not any(existing["hex"].lower() == row[0].lower() for existing in all_colors):
                        all_colors.append({
                            "name": row[1],
                            "hex": row[0],
                            "source": "colors_table",
                            "seasonal_palette": row[2] or seasonal_type,
                            "category": row[3]
                        })
                
                if colors_results:
                    logger.info(f"Added {len(colors_results)} colors from colors table")
            except Exception as e:
                logger.info(f"Could not fetch from colors table: {e}")
            
            # If we don't have enough colors, get some universal ones
            if len(all_colors) < 10:
                cursor.execute("""
                    SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                    FROM comprehensive_colors 
                    WHERE color_family IN ('blue', 'green', 'red', 'purple', 'neutral', 'brown', 'pink')
                    AND hex_code IS NOT NULL
                    AND color_name IS NOT NULL
                    ORDER BY color_name
                    LIMIT 20
                """)
                
                universal_results = cursor.fetchall()
                for row in universal_results:
                    # Avoid duplicates
                    if not any(existing["hex"].lower() == row[0].lower() for existing in all_colors):
                        all_colors.append({
                            "name": row[1],
                            "hex": row[0],
                            "source": "universal_colors",
                            "color_family": row[2] or "unknown",
                            "brightness_level": row[3] or "medium"
                        })
                
                if universal_results:
                    logger.info(f"Added {len(universal_results)} universal colors")
            
            # Format response to match frontend expectations
            final_colors = all_colors[:limit] if len(all_colors) > limit else all_colors
            
            response = {
                "colors_that_suit": [{"name": color["name"], "hex": color["hex"]} for color in final_colors],
                "colors": final_colors,  # Full color objects with metadata
                "colors_to_avoid": [],  # We can enhance this later
                "seasonal_type": seasonal_type,
                "monk_skin_tone": skin_tone,
                "total_colors": len(final_colors),
                "description": f"Based on your {seasonal_type} seasonal type and {skin_tone} skin tone, here are colors from our database that complement your complexion.",
                "message": f"Showing {len(final_colors)} recommended colors from multiple database sources.",
                "database_source": True,
                "sources_used": list(set([color.get("source", "unknown") for color in final_colors]))
            }
            
            logger.info(f"Returning {len(final_colors)} colors for {skin_tone} (seasonal: {seasonal_type})")
            return response
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in get_color_palettes_db: {e}")
        # Fallback response
        fallback_colors = [
            {"name": "Navy Blue", "hex": "#000080"},
            {"name": "Forest Green", "hex": "#228B22"},
            {"name": "Burgundy", "hex": "#800020"},
            {"name": "Charcoal Gray", "hex": "#36454F"},
            {"name": "Cream White", "hex": "#F5F5DC"},
            {"name": "Soft Pink", "hex": "#FFB6C1"},
            {"name": "Royal Purple", "hex": "#663399"},
            {"name": "Emerald Green", "hex": "#50C878"},
            {"name": "Deep Orange", "hex": "#FF6600"},
            {"name": "Chocolate Brown", "hex": "#8B4513"}
        ]
        
        return {
            "colors_that_suit": fallback_colors,
            "colors": [{"name": c["name"], "hex": c["hex"], "source": "fallback"} for c in fallback_colors],
            "colors_to_avoid": [],
            "seasonal_type": skin_tone or "Unknown",
            "monk_skin_tone": skin_tone,
            "total_colors": len(fallback_colors),
            "description": f"Fallback color palette for {skin_tone or 'unknown skin tone'} - database error occurred",
            "message": f"Showing {len(fallback_colors)} fallback colors due to database error.",
            "database_source": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
