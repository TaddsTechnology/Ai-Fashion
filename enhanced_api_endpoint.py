"""
Enhanced API endpoint that integrates Cloudinary with skin tone analysis
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
import logging
from cloudinary_skin_tone_integration import CloudinaryEnhancedSkinToneAnalyzer

logger = logging.getLogger(__name__)

# Initialize the enhanced analyzer
enhanced_analyzer = CloudinaryEnhancedSkinToneAnalyzer()

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

@app.post("/analyze-skin-tone-enhanced")
async def analyze_skin_tone_enhanced(file: UploadFile = File(...)):
    """
    Enhanced skin tone analysis using Cloudinary optimization.
    
    This endpoint:
    1. Uploads the image to Cloudinary
    2. Generates multiple optimized versions
    3. Runs analysis on each version
    4. Combines results for better accuracy
    5. Returns enhanced analysis results
    """
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image."
            )
        
        # Read image data
        image_data = await file.read()
        
        # Run enhanced analysis
        result = await enhanced_analyzer.analyze_with_cloudinary_optimization(
            image_data=image_data,
            monk_tones=MONK_SKIN_TONES
        )
        
        # Add additional metadata
        result.update({
            'filename': file.filename,
            'file_size': len(image_data),
            'content_type': file.content_type,
            'enhancement_method': 'cloudinary_multi_version_analysis'
        })
        
        logger.info(f"Enhanced analysis completed: {result.get('monk_skin_tone')} "
                   f"(confidence: {result.get('confidence')})")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced skin tone analysis failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'monk_skin_tone': 'Monk04',
            'confidence': 0.0,
            'fallback': True
        }

@app.post("/batch-analyze-skin-tone")
async def batch_analyze_skin_tone(files: List[UploadFile] = File(...)):
    """
    Batch analyze multiple images for training data collection.
    """
    try:
        if len(files) > 10:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 images allowed per batch"
            )
        
        # Read all image data
        image_batch = []
        for file in files:
            if not file.content_type or not file.content_type.startswith('image/'):
                continue
            image_data = await file.read()
            image_batch.append(image_data)
        
        # Run batch analysis
        results = await enhanced_analyzer.analyze_batch_images(image_batch)
        
        return {
            'success': True,
            'total_images': len(image_batch),
            'results': results,
            'processing_method': 'cloudinary_batch_analysis'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'total_images': 0,
            'results': []
        }

@app.get("/training-data/{public_id}")
async def get_training_data_urls(public_id: str):
    """
    Get training-optimized URLs for a previously uploaded image.
    """
    try:
        training_urls = await enhanced_analyzer.get_training_data_urls(public_id)
        
        return {
            'success': True,
            'public_id': public_id,
            'training_versions': training_urls,
            'total_versions': len(training_urls)
        }
        
    except Exception as e:
        logger.error(f"Failed to generate training URLs: {e}")
        return {
            'success': False,
            'error': str(e),
            'public_id': public_id,
            'training_versions': {}
        }
