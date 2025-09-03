"""
Image Optimization System for Performance Enhancement
"""
import io
import time
import logging
from typing import Tuple, Optional, Union
from PIL import Image, ImageOps
import numpy as np
import cv2
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OptimizationStats:
    """Image optimization statistics"""
    original_size: int
    optimized_size: int
    original_dimensions: Tuple[int, int]
    optimized_dimensions: Tuple[int, int]
    compression_ratio: float
    processing_time_ms: float
    optimization_applied: str

class ImageOptimizer:
    """High-performance image optimizer for skin tone analysis"""
    
    # Optimal dimensions for skin tone analysis
    ANALYSIS_MAX_WIDTH = 800
    ANALYSIS_MAX_HEIGHT = 800
    
    # Quality settings
    HIGH_QUALITY = 85
    MEDIUM_QUALITY = 75
    LOW_QUALITY = 60
    
    # Size thresholds in bytes
    LARGE_IMAGE_THRESHOLD = 2 * 1024 * 1024  # 2MB
    MEDIUM_IMAGE_THRESHOLD = 500 * 1024      # 500KB
    
    def __init__(self):
        self.stats_history = []
        
    def optimize_for_analysis(
        self, 
        image_data: bytes, 
        target_quality: str = "medium"
    ) -> Tuple[np.ndarray, OptimizationStats]:
        """
        Optimize image specifically for skin tone analysis
        
        Args:
            image_data: Raw image bytes
            target_quality: "high", "medium", or "low"
            
        Returns:
            Tuple of (optimized_image_array, optimization_stats)
        """
        start_time = time.time()
        original_size = len(image_data)
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            original_dimensions = image.size
            
            # Convert to RGB if needed (handles RGBA, CMYK, etc.)
            if image.mode != 'RGB':
                if image.mode == 'RGBA':
                    # Create white background for transparency
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                else:
                    image = image.convert('RGB')
            
            # Apply optimization based on image size
            if original_size > self.LARGE_IMAGE_THRESHOLD:
                image, optimization_type = self._aggressive_optimization(image)
            elif original_size > self.MEDIUM_IMAGE_THRESHOLD:
                image, optimization_type = self._medium_optimization(image)
            else:
                image, optimization_type = self._light_optimization(image)
            
            # Apply quality-specific optimizations
            if target_quality == "high":
                quality = self.HIGH_QUALITY
            elif target_quality == "low":
                quality = self.LOW_QUALITY
            else:
                quality = self.MEDIUM_QUALITY
            
            # Final resize for analysis if still too large
            if max(image.size) > max(self.ANALYSIS_MAX_WIDTH, self.ANALYSIS_MAX_HEIGHT):
                image = self._smart_resize(image, self.ANALYSIS_MAX_WIDTH, self.ANALYSIS_MAX_HEIGHT)
                optimization_type += "_final_resize"
            
            # Convert to numpy array for analysis
            image_array = np.array(image)
            
            # Calculate optimized size (approximate)
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=quality, optimize=True)
            optimized_size = buffer.tell()
            
            # Calculate stats
            processing_time = (time.time() - start_time) * 1000
            compression_ratio = original_size / optimized_size if optimized_size > 0 else 1.0
            
            stats = OptimizationStats(
                original_size=original_size,
                optimized_size=optimized_size,
                original_dimensions=original_dimensions,
                optimized_dimensions=image.size,
                compression_ratio=compression_ratio,
                processing_time_ms=round(processing_time, 2),
                optimization_applied=optimization_type
            )
            
            self.stats_history.append(stats)
            
            logger.debug(
                f"Image optimized: {original_dimensions} -> {image.size}, "
                f"{original_size//1024}KB -> {optimized_size//1024}KB, "
                f"{processing_time:.1f}ms"
            )
            
            return image_array, stats
            
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            # Fallback: return original image as numpy array
            try:
                image = Image.open(io.BytesIO(image_data))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                stats = OptimizationStats(
                    original_size=original_size,
                    optimized_size=original_size,
                    original_dimensions=image.size,
                    optimized_dimensions=image.size,
                    compression_ratio=1.0,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    optimization_applied="fallback_no_optimization"
                )
                
                return np.array(image), stats
                
            except Exception as fallback_error:
                logger.error(f"Fallback image processing failed: {fallback_error}")
                raise
    
    def _aggressive_optimization(self, image: Image.Image) -> Tuple[Image.Image, str]:
        """Apply aggressive optimization for large images"""
        
        # Resize significantly
        max_dim = 600
        image = self._smart_resize(image, max_dim, max_dim)
        
        # Apply noise reduction
        image_array = np.array(image)
        image_array = cv2.bilateralFilter(image_array, 9, 75, 75)
        image = Image.fromarray(image_array)
        
        # Apply slight sharpening to compensate for resizing
        image = ImageOps.autocontrast(image, cutoff=1)
        
        return image, "aggressive"
    
    def _medium_optimization(self, image: Image.Image) -> Tuple[Image.Image, str]:
        """Apply medium optimization for medium-sized images"""
        
        # Moderate resize
        max_dim = 700
        image = self._smart_resize(image, max_dim, max_dim)
        
        # Light noise reduction
        image_array = np.array(image)
        image_array = cv2.bilateralFilter(image_array, 5, 50, 50)
        image = Image.fromarray(image_array)
        
        return image, "medium"
    
    def _light_optimization(self, image: Image.Image) -> Tuple[Image.Image, str]:
        """Apply light optimization for smaller images"""
        
        # Minimal resize if needed
        max_dim = 800
        if max(image.size) > max_dim:
            image = self._smart_resize(image, max_dim, max_dim)
            return image, "light_resize"
        
        return image, "light_no_resize"
    
    def _smart_resize(self, image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Smart resize maintaining aspect ratio and quality"""
        
        width, height = image.size
        
        # Calculate scaling factor
        scale_factor = min(max_width / width, max_height / height)
        
        if scale_factor >= 1.0:
            return image  # No resize needed
        
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Use high-quality resampling
        image = image.resize((new_width, new_height), Image.LANCZOS)
        
        return image
    
    def preprocess_for_skin_analysis(self, image_array: np.ndarray) -> np.ndarray:
        """
        Additional preprocessing specifically for skin tone analysis
        
        Args:
            image_array: Optimized image array
            
        Returns:
            Preprocessed image array ready for analysis
        """
        
        try:
            # Convert to LAB color space for better skin tone detection
            lab_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab_image)
            
            # Apply adaptive histogram equalization to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_channel = clahe.apply(l_channel)
            
            # Merge channels back
            lab_image = cv2.merge([l_channel, a_channel, b_channel])
            
            # Convert back to RGB
            processed_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2RGB)
            
            # Apply gentle gaussian blur to reduce noise
            processed_image = cv2.GaussianBlur(processed_image, (3, 3), 0)
            
            return processed_image
            
        except Exception as e:
            logger.warning(f"Preprocessing failed: {e}, using original image")
            return image_array
    
    def get_optimization_stats(self) -> dict:
        """Get optimization statistics"""
        
        if not self.stats_history:
            return {"message": "No optimization stats available"}
        
        recent_stats = self.stats_history[-100:]  # Last 100 optimizations
        
        avg_compression = sum(s.compression_ratio for s in recent_stats) / len(recent_stats)
        avg_processing_time = sum(s.processing_time_ms for s in recent_stats) / len(recent_stats)
        
        total_original_size = sum(s.original_size for s in recent_stats)
        total_optimized_size = sum(s.optimized_size for s in recent_stats)
        
        optimization_types = {}
        for stat in recent_stats:
            optimization_types[stat.optimization_applied] = optimization_types.get(stat.optimization_applied, 0) + 1
        
        return {
            "total_optimizations": len(self.stats_history),
            "recent_optimizations": len(recent_stats),
            "avg_compression_ratio": round(avg_compression, 2),
            "avg_processing_time_ms": round(avg_processing_time, 2),
            "total_data_saved_kb": round((total_original_size - total_optimized_size) / 1024, 2),
            "optimization_distribution": optimization_types,
            "max_processing_time_ms": max(s.processing_time_ms for s in recent_stats),
            "min_processing_time_ms": min(s.processing_time_ms for s in recent_stats)
        }

# Global image optimizer instance
image_optimizer = ImageOptimizer()

def get_image_optimizer() -> ImageOptimizer:
    """Get the global image optimizer instance"""
    return image_optimizer
