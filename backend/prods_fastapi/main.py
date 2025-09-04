from fastapi import FastAPI, Query, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import numpy as np
import cv2
import math
from typing import List, Optional, Dict
from PIL import Image
import io
from webcolors import hex_to_rgb, rgb_to_hex
import logging
import mediapipe as mp
import asyncio
# import dlib  # Removed to avoid compilation issues
# face_recognition also removed to avoid dlib compilation issues
# Using MediaPipe and OpenCV for face detection instead
from enhanced_skin_tone_analyzer import EnhancedSkinToneAnalyzer

# Import services
from services.cloudinary_service import cloudinary_service
from services.sentry_service import EnhancedSentryService
from config import settings

# Import performance optimizations
from performance import (
    init_performance_systems,
    cleanup_performance_systems,
    get_performance_stats,
    get_db_pool,
    get_cache_manager,
    get_image_optimizer
)

# Import comprehensive error handling
from error_handling import (
    setup_error_handling,
    get_error_stats,
    enhanced_health_check,
    circuit_breaker_context,
    ErrorCategory
)
from health_checks import register_all_health_checks

# Import enhanced monitoring system
from monitoring_enhanced import (
    setup_monitoring,
    setup_monitoring_middleware,
    cleanup_monitoring,
    setup_database_health_check,
    setup_cache_health_check,
    setup_custom_health_check,
    get_health_status,
    get_metrics,
    get_traces,
    get_trace_details,
    get_alerts,
    get_system_stats
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from datetime import datetime

# Initialize enhanced skin tone analyzer
enhanced_analyzer = EnhancedSkinToneAnalyzer()

# Initialize database on startup
try:
    from database import create_tables, init_color_palette_data
    create_tables()
    init_color_palette_data()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.warning(f"Database initialization failed: {e}")

# Import color router
from color_routes import color_router, palette_router

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="AI Fashion Backend",
    version="1.0.3",  # Ultra-aggressive fair skin detection
    description="AI Fashion recommendation system with enhanced skin tone analysis"
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add Sentry middleware for error tracking
if settings.sentry_dsn:
    app.add_middleware(SentryAsgiMiddleware)

# Setup comprehensive error handling system
setup_error_handling(app)

# Add performance middleware before startup
from performance import add_performance_middleware_early
try:
    add_performance_middleware_early(app)
except Exception as e:
    logger.warning(f"Failed to add performance middleware: {e}")

# Add monitoring middleware before startup
try:
    setup_monitoring_middleware(app)
except Exception as e:
    logger.warning(f"Failed to add monitoring middleware: {e}")

# Setup enhanced monitoring system will be done in startup event

# Configure CORS with restricted headers and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://app.taddstechnology.com",
        "https://ai-fashion-backend-d9nj.onrender.com",
        "http://localhost:8000",  # For local development
        "https://localhost:8000",  # For HTTPS local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "accept",
        "accept-language",
        "content-language",
        "content-type",
        "authorization",
        "x-requested-with",
        "cache-control",
        "pragma",
        "origin",
        "user-agent",
        "dnt",
        "sec-fetch-mode",
        "sec-fetch-site",
        "sec-fetch-dest"
    ],
    max_age=3600  # Cache preflight for 1 hour
)

# Add explicit OPTIONS handler for CORS preflight requests
@app.options("/{path:path}")
async def handle_options(path: str):
    """Handle CORS preflight requests for all paths"""
    return {"message": "OK"}

# Include the color routers
app.include_router(color_router)
app.include_router(palette_router)

# Monk skin tone scale - now loaded from database
def get_monk_skin_tones():
    """Get Monk skin tones from database."""
    try:
        from database import SessionLocal, SkinToneMapping
        db = SessionLocal()
        try:
            mappings = db.query(SkinToneMapping).all()
            monk_tones = {}
            for mapping in mappings:
                # Convert Monk01 -> Monk 1 format
                display_name = mapping.monk_tone.replace('Monk0', 'Monk ').replace('Monk', 'Monk ')
                if display_name.endswith('10'):
                    display_name = 'Monk 10'
                monk_tones[display_name] = mapping.hex_code
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

# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize performance systems on startup"""
    logger.info("🚀 Starting AI Fashion Backend...")
    try:
        # Initialize performance systems
        await init_performance_systems(app)
        
        # Setup enhanced monitoring system
        await setup_monitoring(app)
        
        # Register health check dependencies
        register_all_health_checks(app.state.health_manager)
        
        # Setup additional health checks for monitoring
        setup_database_health_check(lambda: {"status": "healthy", "message": "Database is responding"})
        setup_cache_health_check(lambda: {"status": "healthy", "message": "Cache is responding"})
        
        logger.info("✅ All systems initialized successfully")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("🔄 Shutting down AI Fashion Backend...")
    try:
        await cleanup_performance_systems(app)
        await cleanup_monitoring(app)
        logger.info("✅ Cleanup completed")
    except Exception as e:
        logger.error(f"❌ Shutdown cleanup failed: {e}")


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
        image_array[h//8:h//3, w//3:2*w//3],  # Forehead
        image_array[h//3:h//2, w//4:3*w//4],  # Upper cheeks
        image_array[h//3:2*h//3, 2*w//5:3*w//5],  # Nose bridge
        image_array[h//2:2*h//3, w//4:3*w//4],  # Lower cheeks
        image_array[2*h//3:5*h//6, 2*w//5:3*w//5]  # Chin area
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
        distance_confidence = max(0, 1 - (closest_distance / 200))  # Normalize to 0-1
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_confidence = min(1.0, sharpness / 500)  # Good sharpness
        brightness_std = np.std(final_color)
        consistency_confidence = max(0, 1 - (brightness_std / 50))
        avg_brightness = np.mean(final_color)
        brightness_bonus = 0.2 if avg_brightness > 200 else 0.1 if avg_brightness > 180 else 0

        final_confidence = (
            distance_confidence * 0.4 +
            sharpness_confidence * 0.3 +
            consistency_confidence * 0.3 +
            brightness_bonus
        )

        return min(1.0, final_confidence)

    except Exception as e:
        logger.warning(f"Confidence calculation failed: {e}")
        return 0.5


def find_closest_monk_tone_enhanced(rgb_color: np.ndarray) -> tuple:
    """Enhanced Monk tone matching with better light skin detection."""
    min_distance = float('inf')
    closest_monk = "Monk 2"

    avg_brightness = np.mean(rgb_color)

    for monk_name, hex_color in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(hex_color))
        euclidean_distance = np.sqrt(np.sum((rgb_color - monk_rgb) ** 2))
        brightness_diff = abs(avg_brightness - np.mean(monk_rgb))

        if avg_brightness > 220:
            combined_distance = euclidean_distance * 0.3 + brightness_diff * 1.5
        elif avg_brightness > 180:
            combined_distance = euclidean_distance * 0.6 + brightness_diff * 1.0
        else:
            combined_distance = euclidean_distance

        if combined_distance < min_distance:
            min_distance = combined_distance
            closest_monk = monk_name

    return closest_monk, min_distance


# Old dlib-based function removed - now using enhanced_analyzer


@app.get("/")
def home():
    return {"message": "Welcome to the AI Fashion API!", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Comprehensive health check with all dependencies"""
    try:
        return await enhanced_health_check(app)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/performance")
def get_performance_metrics():
    """Get comprehensive performance metrics"""
    try:
        return get_performance_stats(app)
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        return {"error": str(e)}

@app.get("/performance/database")
def get_database_performance():
    """Get database connection pool performance metrics"""
    try:
        if hasattr(app.state, 'db_pool'):
            return app.state.db_pool.get_pool_stats()
        else:
            return {"error": "Database pool not initialized"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/performance/cache")
def get_cache_performance():
    """Get cache performance metrics"""
    try:
        if hasattr(app.state, 'cache_manager'):
            return app.state.cache_manager.get_cache_stats()
        else:
            return {"error": "Cache manager not initialized"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/performance/images")
def get_image_optimization_performance():
    """Get image optimization performance metrics"""
    try:
        if hasattr(app.state, 'image_optimizer'):
            return app.state.image_optimizer.get_optimization_stats()
        else:
            return {"error": "Image optimizer not initialized"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/error-stats")
def get_comprehensive_error_stats():
    """Get comprehensive error handling statistics"""
    try:
        return get_error_stats(app)
    except Exception as e:
        logger.error(f"Failed to get error stats: {e}")
        return {"error": str(e)}

@app.get("/health/quick")
async def quick_health():
    """Quick health check for critical systems only"""
    try:
        from health_checks import quick_health_summary
        return await quick_health_summary()
    except Exception as e:
        logger.error(f"Quick health check failed: {e}")
        return {"status": "unknown", "error": str(e)}

# Enhanced monitoring endpoints
@app.get("/monitoring/metrics")
def get_monitoring_metrics():
    """Get comprehensive metrics from enhanced monitoring system"""
    try:
        return get_metrics()
    except Exception as e:
        logger.error(f"Failed to get monitoring metrics: {e}")
        return {"error": str(e)}

@app.get("/monitoring/traces")
def get_monitoring_traces(limit: int = 20):
    """Get recent request traces"""
    try:
        return get_traces(limit)
    except Exception as e:
        logger.error(f"Failed to get traces: {e}")
        return {"error": str(e)}

@app.get("/monitoring/traces/{trace_id}")
def get_monitoring_trace_details(trace_id: str):
    """Get detailed information about a specific trace"""
    try:
        trace_details = get_trace_details(trace_id)
        if not trace_details:
            raise HTTPException(status_code=404, detail="Trace not found")
        return trace_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trace details: {e}")
        return {"error": str(e)}

@app.get("/monitoring/alerts")
def get_monitoring_alerts():
    """Get alerts and alert history"""
    try:
        return get_alerts()
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        return {"error": str(e)}

@app.get("/monitoring/system")
def get_monitoring_system_stats():
    """Get system performance statistics"""
    try:
        return get_system_stats()
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        return {"error": str(e)}

@app.get("/monitoring/health")
async def get_monitoring_health():
    """Get comprehensive health status from monitoring system"""
    try:
        return await get_health_status()
    except Exception as e:
        logger.error(f"Failed to get health status: {e}")
        return {"status": "unknown", "error": str(e)}


@app.get("/makeup-types")
def get_makeup_types():
    """Get available makeup types."""
    return {
        "types": ["Foundation", "Concealer", "Lipstick", "Mascara", "Blush", "Highlighter", "Eyeshadow"]
    }


@app.get("/products")
def get_products(product_type: str = Query(None), random: bool = Query(False)):
    """Get H&M style products."""
    return []


@app.get("/color-recommendations")
def get_color_recommendations(skin_tone: str = Query(None)):
    """Get color recommendations for skin tone based on database."""
    try:
        from database import SessionLocal, SkinToneMapping, ColorPalette
        
        if not skin_tone:
            # Return error when no skin tone provided
            raise HTTPException(status_code=400, detail="skin_tone parameter is required")
        
        db = SessionLocal()
        try:
            # First, try to find the seasonal type from monk tone mapping
            seasonal_type = None
            
            # Check if skin_tone is a monk tone (like "Monk 5" or "Monk05")
            if "monk" in skin_tone.lower():
                # Normalize monk tone format
                monk_number = ''.join(filter(str.isdigit, skin_tone))
                if monk_number:
                    monk_tone_formatted = f"Monk{monk_number.zfill(2)}"
                    
                    # Look up seasonal type for this monk tone
                    mapping = db.query(SkinToneMapping).filter(
                        SkinToneMapping.monk_tone == monk_tone_formatted
                    ).first()
                    
                    if mapping:
                        seasonal_type = mapping.seasonal_type
            else:
                # If not a monk tone, assume it's already a seasonal type
                seasonal_type = skin_tone
            
            if not seasonal_type:
                logger.warning(f"Could not find seasonal type for skin tone: {skin_tone}")
                raise HTTPException(status_code=404, detail=f"No seasonal type mapping found for skin tone: {skin_tone}")
            
            # Get color palette for this seasonal type
            palette = db.query(ColorPalette).filter(
                ColorPalette.skin_tone == seasonal_type
            ).first()
            
            if not palette:
                logger.warning(f"No color palette found for seasonal type: {seasonal_type}")
                raise HTTPException(status_code=404, detail=f"No color palette found for seasonal type: {seasonal_type}")
            
            # Format the flattering colors for response
            recommendations = []
            if palette.flattering_colors:
                for color in palette.flattering_colors:
                    recommendations.append({
                        "hex_code": color.get("hex", ""),
                        "color_name": color.get("name", ""),
                        "category": "recommended"
                    })
            
            logger.info(f"Found {len(recommendations)} color recommendations for skin tone: {skin_tone} (seasonal type: {seasonal_type})")
            return recommendations
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting color recommendations: {e}")
        # Raise HTTP exception instead of returning hardcoded colors
        raise HTTPException(status_code=500, detail="Database error: unable to fetch color recommendations")


@app.get("/api/color-recommendations")
@limiter.limit("30/minute")
async def get_api_color_recommendations(
    request: Request,
    skin_tone: str = Query(None),
    hex_color: str = Query(None),
    limit: int = Query(50, ge=10, le=100, description="Maximum number of colors to return"),
    occasion: str = Query(None, description="Occasion filter: work, casual, festive_wedding, formal_black_tie")
):
    """Enhanced MST-based color recommendations using comprehensive palette data."""
    logger.info(f"MST Color recommendations request: skin_tone={skin_tone}, occasion={occasion}")
    
    try:
        # Use the enhanced MST Color Recommendation Service
        from services.mst_color_recommendation_service import MSTColorRecommendationService
        
        mst_service = MSTColorRecommendationService()
        
        # Handle different request types based on parameters
        if occasion:
            # Get occasion-specific recommendations
            recommendations = await mst_service.get_occasion_specific_colors(
                skin_tone=skin_tone or "Monk05",  # Default fallback
                occasion=occasion,
                limit=limit
            )
            
            if "error" in recommendations:
                logger.warning(f"MST occasion service error: {recommendations['error']}")
                # Fallback to comprehensive recommendations
                comprehensive = await mst_service.get_comprehensive_color_recommendations(
                    skin_tone=skin_tone or "Monk05",
                    limit=limit
                )
                return _format_comprehensive_to_simple(comprehensive, skin_tone)
            else:
                return _format_occasion_response(recommendations, skin_tone)
        
        else:
            # Get comprehensive recommendations
            comprehensive = await mst_service.get_comprehensive_color_recommendations(
                skin_tone=skin_tone or "Monk05",
                limit=limit
            )
            
            return _format_comprehensive_to_simple(comprehensive, skin_tone)
        
    except Exception as e:
        logger.error(f"MST service error in color recommendations: {e}")
        # Fallback to basic database query if MST service fails
        return await _get_fallback_color_recommendations(skin_tone, limit)


# Helper functions for formatting MST service responses
def _format_comprehensive_to_simple(comprehensive: Dict, skin_tone: str) -> Dict:
    """Convert comprehensive MST response to simple format for frontend compatibility"""
    colors_that_suit = []
    
    # Combine primary and accent colors
    for color in comprehensive.get("primary_colors", []):
        colors_that_suit.append({
            "name": color.get("name", "Unknown"),
            "hex": color.get("hex", "#000000")
        })
    
    for color in comprehensive.get("accent_colors", []):
        colors_that_suit.append({
            "name": color.get("name", "Unknown"), 
            "hex": color.get("hex", "#000000")
        })
    
    # Add some neutrals
    for color in comprehensive.get("neutral_lights", [])[:3]:
        colors_that_suit.append({
            "name": color.get("name", "Unknown"),
            "hex": color.get("hex", "#000000")
        })
    
    return {
        "colors_that_suit": colors_that_suit,
        "colors_to_avoid": [
            {
                "name": color.get("name", "Unknown"),
                "hex": color.get("hex", "#000000")
            }
            for color in comprehensive.get("colors_to_avoid", [])[:5]
        ],
        "seasonal_type": comprehensive.get("seasonal_types", ["Unknown"])[0] if comprehensive.get("seasonal_types") else "Unknown",
        "monk_skin_tone": skin_tone,
        "message": f"MST-based recommendations for {skin_tone} using comprehensive palette data",
        "styling_guidance": comprehensive.get("styling_guidance", {}),
        "recommended_metals": comprehensive.get("recommended_metals", []),
        "denim_recommendations": comprehensive.get("denim_recommendations", [])
    }

def _format_occasion_response(occasion_data: Dict, skin_tone: str) -> Dict:
    """Format occasion-specific response for frontend"""
    colors_that_suit = [
        {
            "name": color.get("name", "Unknown"),
            "hex": color.get("hex", "#000000")
        }
        for color in occasion_data.get("colors", [])
    ]
    
    return {
        "colors_that_suit": colors_that_suit,
        "occasion": occasion_data.get("occasion", "unknown"),
        "monk_skin_tone": skin_tone,
        "styling_tips": occasion_data.get("styling_tips", []),
        "complementary_neutrals": occasion_data.get("complementary_neutrals", []),
        "recommended_metals": occasion_data.get("recommended_metals", []),
        "message": f"Occasion-specific recommendations for {skin_tone}"
    }

async def _get_fallback_color_recommendations(skin_tone: str, limit: int) -> Dict:
    """Fallback color recommendations using basic database queries"""
    try:
        from database import SessionLocal, ColorPalette, SkinToneMapping
        
        db = SessionLocal()
        try:
            # Try to get basic colors from color_palettes
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
            
            palette = db.query(ColorPalette).filter(
                ColorPalette.skin_tone == seasonal_type
            ).first()
            
            if palette and palette.flattering_colors:
                colors_that_suit = [
                    {
                        "name": color.get("name", "Unknown"),
                        "hex": color.get("hex", "#000000")
                    }
                    for color in palette.flattering_colors[:limit]
                ]
                
                return {
                    "colors_that_suit": colors_that_suit,
                    "seasonal_type": seasonal_type,
                    "monk_skin_tone": skin_tone,
                    "message": f"Fallback recommendations for {skin_tone}"
                }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Fallback query failed: {e}")
    
    # Ultimate fallback - basic universal colors
    return {
        "colors_that_suit": [
            {"name": "Navy Blue", "hex": "#002D72"},
            {"name": "Forest Green", "hex": "#205C40"},
            {"name": "Burgundy", "hex": "#890C58"},
            {"name": "Charcoal", "hex": "#36454F"}
        ],
        "seasonal_type": "Universal",
        "monk_skin_tone": skin_tone or "Unknown",
        "message": "Universal fallback colors due to service unavailability"
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
        from database import SessionLocal, SkinToneMapping, ColorPalette
        from sqlalchemy import create_engine, text
        import json
        
        # Get database URL from environment or use default
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
        )
        
        engine = create_engine(DATABASE_URL)
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
            
            # Always add seasonal type specific colors as they are most relevant
            seasonal_colors = get_seasonal_type_colors(seasonal_type)
            for color in seasonal_colors:
                # Avoid duplicates
                if not any(existing["hex"].lower() == color["hex"].lower() for existing in all_colors):
                    all_colors.append(color)
            
            if seasonal_colors:
                logger.info(f"Added {len(seasonal_colors)} seasonal type specific colors for {seasonal_type}")
            
            # If we still don't have enough colors, get some universal ones from database
            if len(all_colors) < 10:
                try:
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
                except Exception as db_error:
                    logger.warning(f"Database query failed: {db_error}")
            
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


@app.get("/analyze-skin-tone")
def analyze_skin_tone_info():
    """Information about the skin tone analysis endpoint."""
    return {
        "message": "Use POST method with image file to analyze skin tone",
        "method": "POST",
        "content_type": "multipart/form-data",
        "parameter": "file (image file)",
        "example": "curl -X POST -F 'file=@image.jpg' /analyze-skin-tone"
    }

@app.post("/analyze-skin-tone")
@limiter.limit("10/minute")
async def analyze_skin_tone(request: Request, file: UploadFile = File(...)):
    """Analyze skin tone from uploaded image with optimization."""
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_data = await file.read()
        
        # Optimize image for faster processing
        try:
            if hasattr(app.state, 'image_optimizer'):
                image_array, optimization_stats = app.state.image_optimizer.optimize_for_analysis(image_data)
                # Apply additional preprocessing for skin tone analysis
                image_array = app.state.image_optimizer.preprocess_for_skin_analysis(image_array)
                logger.info(f"Image optimized: {optimization_stats.optimization_applied}, processing time: {optimization_stats.processing_time_ms}ms")
            else:
                # Fallback to basic processing
                image = Image.open(io.BytesIO(image_data))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image_array = np.array(image)
        except Exception as e:
            logger.warning(f"Image optimization failed: {e}, using fallback")
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_array = np.array(image)
        
        # Store image in Cloudinary for ML dataset and user history with circuit breaker
        upload_result = None
        try:
            async with circuit_breaker_context(
                "cloudinary", 
                failure_threshold=3, 
                timeout_seconds=30,
                recovery_timeout=60
            ):
                import uuid
                unique_id = str(uuid.uuid4())[:8]
                public_id = f"skin_analysis/{unique_id}_{file.filename.replace(' ', '_') if file.filename else 'upload'}"
                upload_result = cloudinary_service.upload_image(image_data, public_id)
                logger.info(f"Image stored in Cloudinary: {upload_result.get('public_id') if upload_result else 'Failed'}")
        except Exception as e:
            logger.warning(f"Failed to store image in Cloudinary: {e}")

        try:
            result = enhanced_analyzer.analyze_skin_tone(image_array, MONK_SKIN_TONES)
            if result['success']:
                # Add Cloudinary URL to response if upload was successful
                if upload_result and upload_result.get('success'):
                    result['cloudinary_url'] = upload_result.get('url')
                    result['image_public_id'] = upload_result.get('public_id')
                return result
        except Exception as e:
            logger.warning(f"Enhanced analysis failed: {e}, falling back to simple analysis")
            
        # Fallback - get a random monk tone from database
        try:
            from database import SessionLocal, SkinToneMapping
            import random
            db = SessionLocal()
            try:
                mappings = db.query(SkinToneMapping).all()
                if mappings:
                    # Pick a middle-range monk tone for fallback
                    fallback_mapping = next((m for m in mappings if 'Monk0' in m.monk_tone and m.monk_tone in ['Monk02', 'Monk03', 'Monk04']), mappings[0])
                    fallback_rgb = list(hex_to_rgb(fallback_mapping.hex_code))
                    return {
                        'monk_skin_tone': fallback_mapping.monk_tone,
                        'monk_tone_display': fallback_mapping.monk_tone.replace('Monk0', 'Monk '),
                        'monk_hex': fallback_mapping.hex_code,
                        'derived_hex_code': fallback_mapping.hex_code,
                        'dominant_rgb': fallback_rgb,
                        'confidence': 0.3,
                        'success': False,
                        'error': 'Fallback to database default'
                    }
            finally:
                db.close()
        except Exception as fallback_e:
            logger.warning(f"Database fallback failed: {fallback_e}")
        
        # Ultimate fallback if database is unavailable
        return {
            'monk_skin_tone': 'Monk02',
            'monk_tone_display': 'Monk 2', 
            'monk_hex': '#f3e7db',
            'derived_hex_code': '#f3e7db',
            'dominant_rgb': [243, 231, 219],
            'confidence': 0.3,
            'success': False,
            'error': 'Ultimate fallback - database unavailable'
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_skin_tone endpoint: {e}")
        # Try to get fallback from database even in error case
        try:
            from database import SessionLocal, SkinToneMapping
            db = SessionLocal()
            try:
                mappings = db.query(SkinToneMapping).all()
                if mappings:
                    # Pick middle tone as error fallback
                    error_fallback = next((m for m in mappings if m.monk_tone == 'Monk05'), mappings[len(mappings)//2])
                    error_rgb = list(hex_to_rgb(error_fallback.hex_code))
                    return {
                        'monk_skin_tone': error_fallback.monk_tone,
                        'monk_tone_display': error_fallback.monk_tone.replace('Monk0', 'Monk '),
                        'monk_hex': error_fallback.hex_code,
                        'derived_hex_code': error_fallback.hex_code,
                        'dominant_rgb': error_rgb,
                        'confidence': 0.5,
                        'success': False,
                        'error': f"Error fallback from database: {str(e)}"
                    }
            finally:
                db.close()
        except Exception:
            pass  # Use ultimate fallback below
            
        # Ultimate fallback if all database attempts fail
        return {
            'monk_skin_tone': 'Monk05',
            'monk_tone_display': 'Monk 5',
            'monk_hex': '#d7bd96',
            'derived_hex_code': '#d7bd96',
            'dominant_rgb': [215, 189, 150],
            'confidence': 0.5,
            'success': False,
            'error': f"Ultimate error fallback: {str(e)}"
        }


def get_seasonal_type_colors(seasonal_type: str) -> List[Dict]:
    """Get colors specifically tailored to each seasonal type."""
    seasonal_palettes = {
        "Warm Autumn": [
            {"name": "Rust", "hex": "#B7410E", "source": "seasonal_warm_autumn"},
            {"name": "Burnt Orange", "hex": "#CC5500", "source": "seasonal_warm_autumn"},
            {"name": "Golden Yellow", "hex": "#FFD700", "source": "seasonal_warm_autumn"},
            {"name": "Olive Green", "hex": "#808000", "source": "seasonal_warm_autumn"},
            {"name": "Deep Terracotta", "hex": "#E2725B", "source": "seasonal_warm_autumn"},
            {"name": "Warm Brown", "hex": "#8B4513", "source": "seasonal_warm_autumn"},
            {"name": "Mustard Yellow", "hex": "#FFDB58", "source": "seasonal_warm_autumn"},
            {"name": "Pumpkin Orange", "hex": "#FF7518", "source": "seasonal_warm_autumn"},
            {"name": "Camel Brown", "hex": "#C19A6B", "source": "seasonal_warm_autumn"},
            {"name": "Deep Gold", "hex": "#B8860B", "source": "seasonal_warm_autumn"},
            {"name": "Brick Red", "hex": "#CB4154", "source": "seasonal_warm_autumn"},
            {"name": "Forest Green", "hex": "#228B22", "source": "seasonal_warm_autumn"}
        ],
        "Soft Autumn": [
            {"name": "Muted Coral", "hex": "#F88379", "source": "seasonal_soft_autumn"},
            {"name": "Sage Green", "hex": "#9CAF88", "source": "seasonal_soft_autumn"},
            {"name": "Dusty Rose", "hex": "#DCAE96", "source": "seasonal_soft_autumn"},
            {"name": "Taupe", "hex": "#483C32", "source": "seasonal_soft_autumn"},
            {"name": "Soft Teal", "hex": "#5F8A8B", "source": "seasonal_soft_autumn"},
            {"name": "Muted Gold", "hex": "#D4AF37", "source": "seasonal_soft_autumn"},
            {"name": "Pewter Gray", "hex": "#899499", "source": "seasonal_soft_autumn"},
            {"name": "Soft Burgundy", "hex": "#800020", "source": "seasonal_soft_autumn"},
            {"name": "Mushroom Beige", "hex": "#C7B299", "source": "seasonal_soft_autumn"},
            {"name": "Muted Olive", "hex": "#6B8E23", "source": "seasonal_soft_autumn"}
        ],
        "Deep Autumn": [
            {"name": "Deep Burgundy", "hex": "#722F37", "source": "seasonal_deep_autumn"},
            {"name": "Rich Chocolate", "hex": "#7B3F00", "source": "seasonal_deep_autumn"},
            {"name": "Hunter Green", "hex": "#355E3B", "source": "seasonal_deep_autumn"},
            {"name": "Burnt Sienna", "hex": "#E97451", "source": "seasonal_deep_autumn"},
            {"name": "Deep Rust", "hex": "#B7410E", "source": "seasonal_deep_autumn"},
            {"name": "Rich Gold", "hex": "#B8860B", "source": "seasonal_deep_autumn"},
            {"name": "Deep Forest", "hex": "#013220", "source": "seasonal_deep_autumn"},
            {"name": "Mahogany", "hex": "#C04000", "source": "seasonal_deep_autumn"},
            {"name": "Dark Olive", "hex": "#556B2F", "source": "seasonal_deep_autumn"},
            {"name": "Espresso Brown", "hex": "#362D1C", "source": "seasonal_deep_autumn"}
        ],
        "Clear Spring": [
            {"name": "Bright Coral", "hex": "#FF7F50", "source": "seasonal_clear_spring"},
            {"name": "Turquoise", "hex": "#40E0D0", "source": "seasonal_clear_spring"},
            {"name": "Emerald Green", "hex": "#50C878", "source": "seasonal_clear_spring"},
            {"name": "Bright Yellow", "hex": "#FFFF00", "source": "seasonal_clear_spring"},
            {"name": "Hot Pink", "hex": "#FF69B4", "source": "seasonal_clear_spring"},
            {"name": "Royal Blue", "hex": "#4169E1", "source": "seasonal_clear_spring"},
            {"name": "Lime Green", "hex": "#32CD32", "source": "seasonal_clear_spring"},
            {"name": "Bright Orange", "hex": "#FF8C00", "source": "seasonal_clear_spring"},
            {"name": "Magenta", "hex": "#FF00FF", "source": "seasonal_clear_spring"},
            {"name": "Electric Blue", "hex": "#00BFFF", "source": "seasonal_clear_spring"}
        ],
        "Warm Spring": [
            {"name": "Peach", "hex": "#FFCBA4", "source": "seasonal_warm_spring"},
            {"name": "Golden Green", "hex": "#B8C25D", "source": "seasonal_warm_spring"},
            {"name": "Warm Coral", "hex": "#FF6B6B", "source": "seasonal_warm_spring"},
            {"name": "Butter Yellow", "hex": "#FFFD74", "source": "seasonal_warm_spring"},
            {"name": "Light Orange", "hex": "#FFB347", "source": "seasonal_warm_spring"},
            {"name": "Aqua", "hex": "#00FFFF", "source": "seasonal_warm_spring"},
            {"name": "Warm Pink", "hex": "#FF91A4", "source": "seasonal_warm_spring"},
            {"name": "Caramel", "hex": "#C68E17", "source": "seasonal_warm_spring"},
            {"name": "Ivory", "hex": "#FFFFF0", "source": "seasonal_warm_spring"},
            {"name": "Light Teal", "hex": "#77DD77", "source": "seasonal_warm_spring"}
        ],
        "Light Spring": [
            {"name": "Soft Pink", "hex": "#FFB6C1", "source": "seasonal_light_spring"},
            {"name": "Light Yellow", "hex": "#FFFFE0", "source": "seasonal_light_spring"},
            {"name": "Mint Green", "hex": "#98FF98", "source": "seasonal_light_spring"},
            {"name": "Baby Blue", "hex": "#89CFF0", "source": "seasonal_light_spring"},
            {"name": "Lavender", "hex": "#E6E6FA", "source": "seasonal_light_spring"},
            {"name": "Light Peach", "hex": "#FFCBA4", "source": "seasonal_light_spring"},
            {"name": "Soft Coral", "hex": "#F08080", "source": "seasonal_light_spring"},
            {"name": "Cream", "hex": "#FFFDD0", "source": "seasonal_light_spring"},
            {"name": "Light Aqua", "hex": "#7FFFD4", "source": "seasonal_light_spring"},
            {"name": "Soft Green", "hex": "#90EE90", "source": "seasonal_light_spring"}
        ],
        "Cool Winter": [
            {"name": "Icy Blue", "hex": "#B0E0E6", "source": "seasonal_cool_winter"},
            {"name": "Deep Navy", "hex": "#000080", "source": "seasonal_cool_winter"},
            {"name": "Pure White", "hex": "#FFFFFF", "source": "seasonal_cool_winter"},
            {"name": "Charcoal Gray", "hex": "#36454F", "source": "seasonal_cool_winter"},
            {"name": "Burgundy Wine", "hex": "#722F37", "source": "seasonal_cool_winter"},
            {"name": "Emerald Green", "hex": "#50C878", "source": "seasonal_cool_winter"},
            {"name": "Royal Purple", "hex": "#663399", "source": "seasonal_cool_winter"},
            {"name": "Cool Pink", "hex": "#FF1493", "source": "seasonal_cool_winter"},
            {"name": "Silver Gray", "hex": "#C0C0C0", "source": "seasonal_cool_winter"},
            {"name": "True Red", "hex": "#FF0000", "source": "seasonal_cool_winter"}
        ],
        "Deep Winter": [
            {"name": "True Black", "hex": "#000000", "source": "seasonal_deep_winter"},
            {"name": "Pure White", "hex": "#FFFFFF", "source": "seasonal_deep_winter"},
            {"name": "Deep Red", "hex": "#8B0000", "source": "seasonal_deep_winter"},
            {"name": "Royal Blue", "hex": "#4169E1", "source": "seasonal_deep_winter"},
            {"name": "Emerald Green", "hex": "#50C878", "source": "seasonal_deep_winter"},
            {"name": "Deep Purple", "hex": "#663399", "source": "seasonal_deep_winter"},
            {"name": "Hot Pink", "hex": "#FF69B4", "source": "seasonal_deep_winter"},
            {"name": "Bright Yellow", "hex": "#FFFF00", "source": "seasonal_deep_winter"},
            {"name": "True Navy", "hex": "#000080", "source": "seasonal_deep_winter"},
            {"name": "Magenta", "hex": "#FF00FF", "source": "seasonal_deep_winter"}
        ],
        "Clear Winter": [
            {"name": "Bright White", "hex": "#FFFFFF", "source": "seasonal_clear_winter"},
            {"name": "True Black", "hex": "#000000", "source": "seasonal_clear_winter"},
            {"name": "Electric Blue", "hex": "#00BFFF", "source": "seasonal_clear_winter"},
            {"name": "Bright Red", "hex": "#FF0000", "source": "seasonal_clear_winter"},
            {"name": "Emerald Green", "hex": "#50C878", "source": "seasonal_clear_winter"},
            {"name": "Fuchsia", "hex": "#FF00FF", "source": "seasonal_clear_winter"},
            {"name": "Lemon Yellow", "hex": "#FFFF00", "source": "seasonal_clear_winter"},
            {"name": "Royal Purple", "hex": "#7851A9", "source": "seasonal_clear_winter"},
            {"name": "Turquoise", "hex": "#40E0D0", "source": "seasonal_clear_winter"},
            {"name": "Hot Pink", "hex": "#FF69B4", "source": "seasonal_clear_winter"}
        ]
    }
    
    # Return colors for the specific seasonal type, or default colors if not found
    colors = seasonal_palettes.get(seasonal_type, [])
    
    if not colors:
        # Universal fallback colors for any seasonal type
        colors = [
            {"name": "Navy Blue", "hex": "#000080", "source": "universal_fallback"},
            {"name": "Forest Green", "hex": "#228B22", "source": "universal_fallback"},
            {"name": "Burgundy", "hex": "#800020", "source": "universal_fallback"},
            {"name": "Charcoal Gray", "hex": "#36454F", "source": "universal_fallback"},
            {"name": "Cream White", "hex": "#F5F5DC", "source": "universal_fallback"},
            {"name": "Soft Pink", "hex": "#FFB6C1", "source": "universal_fallback"},
            {"name": "Royal Purple", "hex": "#663399", "source": "universal_fallback"},
            {"name": "Emerald Green", "hex": "#50C878", "source": "universal_fallback"},
            {"name": "Deep Orange", "hex": "#FF6600", "source": "universal_fallback"},
            {"name": "Chocolate Brown", "hex": "#8B4513", "source": "universal_fallback"}
        ]
    
    return colors


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
