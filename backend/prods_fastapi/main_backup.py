from fastapi import FastAPI, Query, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import math
from typing import List, Optional, Dict
from PIL import Image
import io
from webcolors import hex_to_rgb, rgb_to_hex
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Fashion Backend",
    version="1.0.0",
    description="AI Fashion recommendation system with skin tone analysis"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monk skin tone scale
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
    """Enhanced skin tone analysis with LAB color space, CLAHE, multi-region analysis, and confidence scoring."""
    try:
        logger.info("Starting enhanced skin tone analysis...")

        corrected_image = apply_lighting_correction(image_array)
        region_colors = extract_multi_region_colors(corrected_image)

        if not region_colors:
            h, w = corrected_image.shape[:2]
            center_region = corrected_image[h//4:3*h//4, w//4:3*w//4]
            avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
        else:
            region_colors_array = np.array(region_colors)
            brightness_weights = np.mean(region_colors_array, axis=1)

            if np.sum(brightness_weights) > 0:
                brightness_weights = brightness_weights / np.sum(brightness_weights)
                avg_color = np.average(region_colors_array, axis=0, weights=brightness_weights)
            else:
                avg_color = np.mean(region_colors_array, axis=0)

        lab_color = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_RGB2LAB)[0][0]
        closest_monk, min_distance = find_closest_monk_tone_enhanced(avg_color)
        confidence = calculate_confidence_score(image_array, avg_color, min_distance)

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
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        image_array = np.array(image)

        try:
            result = analyze_skin_tone_enhanced(image_array)
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"Enhanced analysis failed: {e}, falling back to simple analysis")
            
        # Fallback
        return {
            'monk_skin_tone': 'Monk02',
            'monk_tone_display': 'Monk 2',
            'monk_hex': MONK_SKIN_TONES['Monk 2'],
            'derived_hex_code': '#f3e7db',
            'dominant_rgb': [243, 231, 219],
            'confidence': 0.3,
            'success': False,
            'error': 'Fallback to default'
        }

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
