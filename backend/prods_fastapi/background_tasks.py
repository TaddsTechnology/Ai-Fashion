"""
Background Task Processing for AI Fashion Backend
Handles CPU-intensive operations like image processing, color analysis, and recommendations.
"""

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
import logging
import numpy as np
import cv2
from PIL import Image
import io
import base64
from typing import Dict, Any, List, Optional
import json
from cache_manager import cache_manager, cached

logger = logging.getLogger(__name__)

# Configure Dramatiq with Redis broker (using environment variable)
import os
try:
    redis_url = os.getenv("DRAMATIQ_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/1"))
    if redis_url.startswith(("redis://", "rediss://")):
        # Parse Redis URL for dramatiq
        import urllib.parse
        parsed = urllib.parse.urlparse(redis_url)
        redis_host = parsed.hostname or "localhost"
        redis_port = parsed.port or 6379
        redis_password = parsed.password  # Extract password
        # Use DB 1 for background tasks, or extract from URL
        redis_db = int(parsed.path.lstrip('/')) if parsed.path and parsed.path != '/' else 1
        
        # Configure broker with authentication if password is present
        # Check if SSL is needed (rediss:// protocol)
        use_ssl = redis_url.startswith("rediss://")
        
        if redis_password:
            if use_ssl:
                redis_broker = RedisBroker(host=redis_host, port=redis_port, db=redis_db, password=redis_password, connection_kwargs={"ssl": True, "ssl_cert_reqs": None})
                logger.info(f"Dramatiq broker configured with Redis at {redis_host}:{redis_port} (with auth + SSL)")
            else:
                redis_broker = RedisBroker(host=redis_host, port=redis_port, db=redis_db, password=redis_password)
                logger.info(f"Dramatiq broker configured with Redis at {redis_host}:{redis_port} (with auth)")
        else:
            if use_ssl:
                redis_broker = RedisBroker(host=redis_host, port=redis_port, db=redis_db, connection_kwargs={"ssl": True, "ssl_cert_reqs": None})
                logger.info(f"Dramatiq broker configured with Redis at {redis_host}:{redis_port} (SSL only)")
            else:
                redis_broker = RedisBroker(host=redis_host, port=redis_port, db=redis_db)
                logger.info(f"Dramatiq broker configured with Redis at {redis_host}:{redis_port} (no auth)")
            
        dramatiq.set_broker(redis_broker)
    else:
        logger.warning("Invalid REDIS_URL format, using localhost fallback")
        redis_broker = RedisBroker(host="localhost", port=6379, db=1)
        dramatiq.set_broker(redis_broker)
except Exception as e:
    logger.error(f"Failed to configure Redis broker: {e}")
    # Use stub broker as fallback
    redis_broker = StubBroker()
    dramatiq.set_broker(redis_broker)

@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=10000)
def process_image_analysis_task(image_data_b64: str, analysis_id: str) -> Dict[str, Any]:
    """
    Background task for image processing and skin tone analysis
    
    Args:
        image_data_b64: Base64 encoded image data
        analysis_id: Unique identifier for this analysis task
    
    Returns:
        Analysis results dictionary
    """
    try:
        logger.info(f"Starting background image analysis task: {analysis_id}")
        
        # Decode image data
        image_data = base64.b64decode(image_data_b64)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Apply comprehensive lighting correction
        corrected_image = apply_lighting_correction_task(image_array)
        
        # Perform skin tone analysis
        result = analyze_skin_tone_lab_task(corrected_image)
        
        # Cache the result
        cache_key = f"analysis_result:{analysis_id}"
        cache_manager.set(cache_key, result, expire_seconds=3600)
        
        logger.info(f"Completed background image analysis task: {analysis_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in background image analysis task {analysis_id}: {e}")
        error_result = {
            'success': False,
            'error': str(e),
            'monk_skin_tone': 'Monk05',
            'confidence': 0.0
        }
        
        # Cache error result too
        cache_key = f"analysis_result:{analysis_id}"
        cache_manager.set(cache_key, error_result, expire_seconds=300)
        
        return error_result

@dramatiq.actor(max_retries=2)
def generate_color_recommendations_task(monk_skin_tone: str, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Background task for generating color recommendations
    
    Args:
        monk_skin_tone: User's monk skin tone (e.g., "Monk05")
        user_preferences: User preference dictionary
    
    Returns:
        Color recommendations dictionary
    """
    try:
        logger.info(f"Generating color recommendations for {monk_skin_tone}")
        
        # Import here to avoid circular imports
        from main import monk_to_seasonal, seasonal_palettes
        
        # Get seasonal type from monk tone
        seasonal_type = monk_to_seasonal.get(monk_skin_tone, "Universal")
        
        # Get color palette
        colors_that_suit = []
        if seasonal_type in seasonal_palettes:
            palette = seasonal_palettes[seasonal_type]
            if isinstance(palette, dict) and "recommended" in palette:
                colors_that_suit = palette["recommended"]
            elif isinstance(palette, list):
                colors_that_suit = palette[:20]  # Limit to first 20 colors
        
        # Default fallback colors
        if not colors_that_suit:
            colors_that_suit = [
                {"name": "Navy Blue", "hex": "#000080"},
                {"name": "Forest Green", "hex": "#228B22"},
                {"name": "Burgundy", "hex": "#800020"},
                {"name": "Charcoal Gray", "hex": "#36454F"},
                {"name": "Cream White", "hex": "#F5F5DC"},
                {"name": "Deep Purple", "hex": "#301934"}
            ]
        
        result = {
            "colors_that_suit": colors_that_suit,
            "seasonal_type": seasonal_type,
            "monk_skin_tone": monk_skin_tone,
            "success": True
        }
        
        # Cache result
        cache_key = f"color_rec:{monk_skin_tone}"
        cache_manager.set(cache_key, result, expire_seconds=7200)
        
        logger.info(f"Generated {len(colors_that_suit)} color recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error generating color recommendations: {e}")
        return {
            "success": False,
            "error": str(e),
            "colors_that_suit": [],
            "seasonal_type": "Universal",
            "monk_skin_tone": monk_skin_tone
        }

@dramatiq.actor(max_retries=2)
def generate_product_recommendations_task(
    skin_tone: str, 
    product_type: str = "makeup", 
    limit: int = 20,
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Background task for generating product recommendations
    
    Args:
        skin_tone: User's skin tone
        product_type: Type of products to recommend
        limit: Number of recommendations to generate
        user_preferences: User preferences dictionary
    
    Returns:
        Product recommendations dictionary
    """
    try:
        logger.info(f"Generating {product_type} recommendations for {skin_tone}")
        
        if user_preferences is None:
            user_preferences = {}
        
        # Import here to avoid circular imports
        from main import df_sephora, get_diverse_recommendations
        
        # Get base product data
        if product_type == "makeup" and not df_sephora.empty:
            products = df_sephora.to_dict(orient="records")
        else:
            # Generate synthetic products for demo
            products = generate_synthetic_products(product_type, skin_tone, limit * 2)
        
        # Generate diverse recommendations
        recommendations = get_diverse_recommendations(
            products, user_preferences, skin_tone, limit
        )
        
        result = {
            "success": True,
            "recommendations": recommendations,
            "total_items": len(recommendations),
            "skin_tone": skin_tone,
            "product_type": product_type
        }
        
        # Cache result
        cache_key = f"prod_rec:{skin_tone}:{product_type}:{limit}"
        cache_manager.set(cache_key, result, expire_seconds=1800)
        
        logger.info(f"Generated {len(recommendations)} product recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error generating product recommendations: {e}")
        return {
            "success": False,
            "error": str(e),
            "recommendations": [],
            "total_items": 0,
            "skin_tone": skin_tone,
            "product_type": product_type
        }

@dramatiq.actor(max_retries=1)
def warm_cache_task():
    """Background task to warm up caches with frequently accessed data"""
    try:
        logger.info("Starting cache warming task")
        
        # Import here to avoid circular imports
        from cache_manager import warm_cache_skin_tones, warm_cache_color_palettes
        
        # Warm skin tone cache
        warm_cache_skin_tones()
        
        # Warm color palette cache
        warm_cache_color_palettes()
        
        # Pre-generate popular recommendations
        popular_skin_tones = ["Monk01", "Monk03", "Monk05", "Monk07", "Monk10"]
        for skin_tone in popular_skin_tones:
            generate_color_recommendations_task.send(skin_tone, {})
            generate_product_recommendations_task.send(skin_tone, "makeup", 20, {})
        
        logger.info("Cache warming task completed")
        return {"success": True, "message": "Cache warmed successfully"}
        
    except Exception as e:
        logger.error(f"Error in cache warming task: {e}")
        return {"success": False, "error": str(e)}

@dramatiq.actor(max_retries=1)
def cleanup_expired_cache_task():
    """Background task to cleanup expired cache entries"""
    try:
        logger.info("Starting cache cleanup task")
        
        # Cleanup old analysis results (older than 1 hour)
        cache_manager.flush_pattern("analysis_result:*")
        
        # Cleanup old temporary data
        cache_manager.flush_pattern("temp:*")
        
        logger.info("Cache cleanup task completed")
        return {"success": True, "message": "Cache cleaned up successfully"}
        
    except Exception as e:
        logger.error(f"Error in cache cleanup task: {e}")
        return {"success": False, "error": str(e)}

# Helper functions for background tasks

def apply_lighting_correction_task(image_array: np.ndarray) -> np.ndarray:
    """Apply lighting correction in background task"""
    try:
        # Simplified lighting correction for background processing
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        mean_brightness = np.mean(gray)
        
        # Apply CLAHE for contrast enhancement
        lab_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_image)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_channel_corrected = clahe.apply(l_channel)
        
        corrected_lab = cv2.merge([l_channel_corrected, a_channel, b_channel])
        corrected_rgb = cv2.cvtColor(corrected_lab, cv2.COLOR_LAB2RGB)
        
        # Apply gamma correction based on brightness
        gamma = 1.2 if mean_brightness < 120 else 1.0
        gamma_corrected = np.power(corrected_rgb / 255.0, gamma) * 255.0
        gamma_corrected = np.clip(gamma_corrected, 0, 255).astype(np.uint8)
        
        return gamma_corrected
        
    except Exception as e:
        logger.warning(f"Background lighting correction failed: {e}")
        return image_array

def analyze_skin_tone_lab_task(image_array: np.ndarray) -> Dict[str, Any]:
    """Analyze skin tone in background task"""
    try:
        # Convert to LAB color space
        lab_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_image)
        
        # Calculate median values
        lightness_median = np.median(l_channel)
        median_a = np.median(a_channel)
        median_b = np.median(b_channel)
        
        final_color_lab = np.array([lightness_median, median_a, median_b])
        final_color_rgb = cv2.cvtColor(np.uint8([[final_color_lab]]), cv2.COLOR_LAB2RGB)[0][0]
        
        # Find closest Monk tone
        closest_monk = find_closest_monk_tone_task(final_color_rgb)
        
        # Calculate basic confidence
        confidence = min(0.9, max(0.3, (lightness_median / 255.0) * 0.8 + 0.2))
        
        return {
            'monk_skin_tone': closest_monk['monk_id'],
            'monk_tone_display': closest_monk['monk_name'],
            'monk_hex': closest_monk['monk_hex'],
            'derived_hex_code': closest_monk['derived_hex'],
            'dominant_rgb': final_color_rgb.astype(int).tolist(),
            'confidence': confidence,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Background skin tone analysis failed: {e}")
        return {
            'monk_skin_tone': 'Monk05',
            'monk_tone_display': 'Monk 5',
            'monk_hex': '#d7bd96',
            'derived_hex_code': '#d7bd96',
            'dominant_rgb': [215, 189, 150],
            'confidence': 0.3,
            'success': False,
            'error': str(e)
        }

def find_closest_monk_tone_task(rgb_color: np.ndarray) -> Dict[str, str]:
    """Find closest Monk tone in background task"""
    try:
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
        
        min_distance = float('inf')
        closest_monk = 'Monk 5'
        
        avg_brightness = np.mean(rgb_color)
        
        for monk_name, monk_hex in MONK_SKIN_TONES.items():
            monk_rgb = np.array([
                int(monk_hex[1:3], 16),
                int(monk_hex[3:5], 16),
                int(monk_hex[5:7], 16)
            ])
            
            # Calculate Euclidean distance
            distance = np.sqrt(np.sum((rgb_color - monk_rgb) ** 2))
            
            # Add brightness bias
            brightness_diff = abs(avg_brightness - np.mean(monk_rgb))
            total_distance = distance + brightness_diff * 0.5
            
            if total_distance < min_distance:
                min_distance = total_distance
                closest_monk = monk_name
        
        # Format result
        monk_number = closest_monk.split()[1]
        monk_id = f"Monk{monk_number.zfill(2)}"
        
        from webcolors import rgb_to_hex
        derived_hex = rgb_to_hex((int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2])))
        
        return {
            'monk_name': closest_monk,
            'monk_id': monk_id,
            'monk_hex': MONK_SKIN_TONES[closest_monk],
            'derived_hex': derived_hex
        }
        
    except Exception as e:
        logger.error(f"Error finding closest Monk tone: {e}")
        return {
            'monk_name': 'Monk 5',
            'monk_id': 'Monk05',
            'monk_hex': '#d7bd96',
            'derived_hex': '#d7bd96'
        }

def generate_synthetic_products(product_type: str, skin_tone: str, count: int) -> List[Dict[str, Any]]:
    """Generate synthetic products for demo purposes"""
    try:
        import random
        
        brands = ["Fenty Beauty", "MAC", "NARS", "Maybelline", "L'Oreal", "Urban Decay"]
        
        if product_type == "makeup":
            product_names = ["Foundation", "Concealer", "Blush", "Lipstick", "Eyeshadow"]
            adjectives = ["Matte", "Dewy", "Radiant", "Luminous", "Velvet"]
        else:
            product_names = ["Dress", "Top", "Pants", "Skirt", "Jacket"]
            adjectives = ["Elegant", "Casual", "Stylish", "Modern", "Classic"]
        
        colors = ["Nude", "Rose", "Berry", "Coral", "Bronze", "Gold"]
        
        products = []
        for i in range(count):
            brand = random.choice(brands)
            product_name = random.choice(product_names)
            adjective = random.choice(adjectives)
            color = random.choice(colors)
            
            products.append({
                "product": f"{adjective} {product_name} - {color}",
                "brand": brand,
                "price": f"${random.randint(15, 89)}.99",
                "imgSrc": f"https://via.placeholder.com/150/cccccc/FFFFFF?text={brand}",
                "mst": skin_tone,
                "desc": f"Beautiful {adjective.lower()} {product_name.lower()} in {color.lower()}",
                "product_type": product_name
            })
        
        return products
        
    except Exception as e:
        logger.error(f"Error generating synthetic products: {e}")
        return []

# Periodic tasks
@dramatiq.actor(max_retries=0)
def scheduled_cache_warmup():
    """Scheduled task to warm cache periodically"""
    warm_cache_task.send()

@dramatiq.actor(max_retries=0)
def scheduled_cache_cleanup():
    """Scheduled task to cleanup cache periodically"""
    cleanup_expired_cache_task.send()

# Task result polling
def get_task_result(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get result of a background task
    
    Args:
        task_id: Task identifier
    
    Returns:
        Task result if available, None otherwise
    """
    cache_key = f"analysis_result:{task_id}"
    return cache_manager.get(cache_key)

def is_task_complete(task_id: str) -> bool:
    """
    Check if a background task is complete
    
    Args:
        task_id: Task identifier
    
    Returns:
        True if task is complete, False otherwise
    """
    cache_key = f"analysis_result:{task_id}"
    result = cache_manager.get(cache_key)
    return result is not None
