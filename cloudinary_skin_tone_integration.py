#!/usr/bin/env python3
"""
Cloudinary + Skin Tone Analysis Integration
Enhanced pipeline for better skin tone detection using Cloudinary transformations
"""

import numpy as np
import cv2
import requests
from io import BytesIO
from PIL import Image
import logging
from typing import Dict, Any, Optional, List
import asyncio

# Import your existing services
from backend.prods_fastapi.services.cloudinary_service import cloudinary_service
from backend.prods_fastapi.enhanced_skin_tone_analyzer import EnhancedSkinToneAnalyzer

logger = logging.getLogger(__name__)

class CloudinaryEnhancedSkinToneAnalyzer:
    """
    Enhanced skin tone analyzer that leverages Cloudinary's image processing
    capabilities for better analysis results.
    """
    
    def __init__(self):
        self.analyzer = EnhancedSkinToneAnalyzer()
        self.cloudinary_service = cloudinary_service
    
    async def analyze_with_cloudinary_optimization(
        self, 
        image_data: bytes, 
        monk_tones: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Main integration method that uses Cloudinary for image optimization
        before running skin tone analysis.
        """
        try:
            logger.info("Starting Cloudinary-enhanced skin tone analysis...")
            
            # Step 1: Upload original image to Cloudinary
            upload_result = await self.cloudinary_service.upload_image(
                image_data=image_data,
                folder='skin_tone_analysis',
                tags=['analysis', 'processing']
            )
            
            if not upload_result['success']:
                raise Exception(f"Failed to upload image: {upload_result.get('error')}")
            
            public_id = upload_result['public_id']
            logger.info(f"Image uploaded to Cloudinary: {public_id}")
            
            # Step 2: Generate multiple optimized versions for analysis
            optimized_versions = await self._generate_analysis_versions(public_id)
            
            # Step 3: Run analysis on each version and combine results
            analysis_results = []
            
            for version_name, image_url in optimized_versions.items():
                try:
                    # Download optimized image
                    optimized_image = await self._download_image(image_url)
                    
                    # Run skin tone analysis
                    result = self.analyzer.analyze_skin_tone(optimized_image, monk_tones)
                    result['version'] = version_name
                    result['cloudinary_url'] = image_url
                    
                    analysis_results.append(result)
                    logger.info(f"Analysis completed for {version_name}: {result.get('monk_skin_tone')}")
                    
                except Exception as e:
                    logger.warning(f"Analysis failed for {version_name}: {e}")
                    continue
            
            # Step 4: Combine results using weighted confidence
            final_result = await self._combine_analysis_results(analysis_results)
            
            # Step 5: Store analysis result with reference to original image
            final_result.update({
                'cloudinary_public_id': public_id,
                'original_url': upload_result['url'],
                'analysis_versions': len(analysis_results),
                'processing_method': 'cloudinary_multi_version_analysis'
            })
            
            logger.info(f"Final analysis result: {final_result.get('monk_skin_tone')} "
                       f"(confidence: {final_result.get('confidence')})")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Cloudinary-enhanced analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'monk_skin_tone': 'Monk04',
                'confidence': 0.0
            }
    
    async def _generate_analysis_versions(self, public_id: str) -> Dict[str, str]:
        """
        Generate multiple optimized versions of the image for analysis.
        Each version is optimized for different skin tone detection scenarios.
        """
        versions = {}
        
        # Version 1: Standard optimization for general analysis
        versions['standard'] = self.cloudinary_service.get_optimized_url(
            public_id=public_id,
            width=800,
            height=800,
            crop='fill',
            quality='auto:best'
        )
        
        # Version 2: Enhanced brightness for fair skin detection
        versions['bright_enhanced'] = self._get_enhanced_url(
            public_id, 
            brightness=20,
            contrast=10,
            saturation=5
        )
        
        # Version 3: Shadow/highlight balance for challenging lighting
        versions['balanced_lighting'] = self._get_enhanced_url(
            public_id,
            auto_brightness=True,
            auto_contrast=True,
            gamma=1.2
        )
        
        # Version 4: Color temperature adjusted for warm lighting
        versions['color_corrected'] = self._get_enhanced_url(
            public_id,
            color_temperature=5500,  # Daylight color temperature
            vibrance=10
        )
        
        # Version 5: High contrast for dark skin tone detection
        versions['high_contrast'] = self._get_enhanced_url(
            public_id,
            contrast=25,
            brightness=10,
            saturation=15
        )
        
        logger.info(f"Generated {len(versions)} analysis versions")
        return versions
    
    def _get_enhanced_url(self, public_id: str, **transformations) -> str:
        """
        Generate enhanced Cloudinary URL with specific transformations.
        """
        try:
            from cloudinary import CloudinaryImage
            
            # Build transformation parameters
            transform_params = {
                'width': 800,
                'height': 800,
                'crop': 'fill',
                'quality': 'auto:best',
                'fetch_format': 'auto'
            }
            
            # Add enhancement parameters
            if 'brightness' in transformations:
                transform_params['brightness'] = transformations['brightness']
            
            if 'contrast' in transformations:
                transform_params['contrast'] = transformations['contrast']
            
            if 'saturation' in transformations:
                transform_params['saturation'] = transformations['saturation']
            
            if 'gamma' in transformations:
                transform_params['gamma'] = transformations['gamma']
            
            if 'auto_brightness' in transformations:
                transform_params['auto_brightness'] = 'auto'
            
            if 'auto_contrast' in transformations:
                transform_params['auto_contrast'] = 'auto'
            
            if 'color_temperature' in transformations:
                transform_params['color_temperature'] = transformations['color_temperature']
            
            if 'vibrance' in transformations:
                transform_params['vibrance'] = transformations['vibrance']
            
            return CloudinaryImage(public_id).build_url(**transform_params)
            
        except Exception as e:
            logger.warning(f"Failed to generate enhanced URL: {e}")
            return self.cloudinary_service.get_optimized_url(public_id)
    
    async def _download_image(self, image_url: str) -> np.ndarray:
        """
        Download and convert Cloudinary image to numpy array for analysis.
        """
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Convert to PIL Image
            pil_image = Image.open(BytesIO(response.content))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            return np.array(pil_image)
            
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {e}")
            raise
    
    async def _combine_analysis_results(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Combine multiple analysis results using weighted confidence scoring.
        """
        if not results:
            return {
                'success': False,
                'error': 'No analysis results to combine'
            }
        
        # Filter successful results
        successful_results = [r for r in results if r.get('success', False)]
        
        if not successful_results:
            return results[0]  # Return first result as fallback
        
        # Weight results by confidence and method
        weighted_scores = {}
        total_weight = 0
        
        for result in successful_results:
            monk_tone = result.get('monk_skin_tone', 'Monk04')
            confidence = result.get('confidence', 0.0)
            version = result.get('version', 'standard')
            
            # Apply version-specific weights
            version_weight = self._get_version_weight(version, result)
            final_weight = confidence * version_weight
            
            if monk_tone not in weighted_scores:
                weighted_scores[monk_tone] = {
                    'weight': 0,
                    'results': [],
                    'avg_confidence': 0
                }
            
            weighted_scores[monk_tone]['weight'] += final_weight
            weighted_scores[monk_tone]['results'].append(result)
            total_weight += final_weight
        
        # Find the highest weighted result
        best_monk_tone = max(weighted_scores.keys(), 
                           key=lambda k: weighted_scores[k]['weight'])
        
        best_results = weighted_scores[best_monk_tone]['results']
        
        # Calculate combined confidence
        combined_confidence = min(1.0, weighted_scores[best_monk_tone]['weight'] / max(1, len(successful_results)))
        
        # Use the result with highest individual confidence as base
        base_result = max(best_results, key=lambda r: r.get('confidence', 0))
        
        # Enhanced result with combination metadata
        base_result.update({
            'confidence': round(combined_confidence, 2),
            'combined_from_versions': len(successful_results),
            'version_weights': {v['version']: v.get('confidence', 0) for v in successful_results},
            'analysis_consensus': len(set(r.get('monk_skin_tone') for r in successful_results)),
            'success': True
        })
        
        return base_result
    
    def _get_version_weight(self, version: str, result: Dict) -> float:
        """
        Calculate version-specific weights based on analysis context.
        """
        base_weights = {
            'standard': 1.0,
            'bright_enhanced': 1.2,  # Better for fair skin
            'balanced_lighting': 1.1,
            'color_corrected': 1.0,
            'high_contrast': 1.1  # Better for dark skin
        }
        
        weight = base_weights.get(version, 1.0)
        
        # Boost weight based on detected skin tone suitability
        monk_tone = result.get('monk_skin_tone', 'Monk04')
        if monk_tone in ['Monk01', 'Monk02', 'Monk03'] and version == 'bright_enhanced':
            weight *= 1.3  # Boost for fair skin detection
        elif monk_tone in ['Monk08', 'Monk09', 'Monk10'] and version == 'high_contrast':
            weight *= 1.3  # Boost for dark skin detection
        
        return weight
    
    async def get_training_data_urls(self, public_id: str) -> Dict[str, str]:
        """
        Generate training-optimized versions of uploaded images for model improvement.
        """
        training_versions = {}
        
        # High-resolution version for detailed analysis
        training_versions['high_res'] = self.cloudinary_service.get_optimized_url(
            public_id=public_id,
            width=1200,
            height=1200,
            crop='fill',
            quality='auto:best'
        )
        
        # Standardized version for consistent training
        training_versions['standardized'] = self._get_enhanced_url(
            public_id,
            auto_brightness=True,
            auto_contrast=True,
            width=512,
            height=512
        )
        
        # Multiple exposure versions for robustness
        for exposure in [-20, -10, 0, 10, 20]:
            training_versions[f'exposure_{exposure}'] = self._get_enhanced_url(
                public_id,
                brightness=exposure,
                width=512,
                height=512
            )
        
        return training_versions
    
    async def analyze_batch_images(self, image_batch: List[bytes]) -> List[Dict]:
        """
        Process multiple images for batch analysis and training data collection.
        """
        results = []
        
        for i, image_data in enumerate(image_batch):
            try:
                result = await self.analyze_with_cloudinary_optimization(
                    image_data, 
                    self.analyzer.monk_tones if hasattr(self.analyzer, 'monk_tones') else {}
                )
                result['batch_index'] = i
                results.append(result)
                
            except Exception as e:
                logger.error(f"Batch analysis failed for image {i}: {e}")
                results.append({
                    'batch_index': i,
                    'success': False,
                    'error': str(e)
                })
        
        return results

# Usage example and integration points
async def main():
    """Example usage of the Cloudinary-enhanced analyzer"""
    analyzer = CloudinaryEnhancedSkinToneAnalyzer()
    
    # Example: Analyze a single image
    with open('sample_image.jpg', 'rb') as f:
        image_data = f.read()
    
    monk_tones = {
        'Monk 1': '#f6ede4',
        'Monk 2': '#f3e7db', 
        'Monk 3': '#f7ead0',
        'Monk 4': '#eadaba',
        'Monk 5': '#d7bd96'
        # ... rest of the monk tones
    }
    
    result = await analyzer.analyze_with_cloudinary_optimization(image_data, monk_tones)
    print(f"Analysis result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
