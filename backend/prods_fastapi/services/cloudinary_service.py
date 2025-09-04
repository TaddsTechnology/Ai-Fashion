"""
Cloudinary Integration for AI Fashion Backend
Handles image upload, transformation, and management
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import logging
from typing import Dict, Any, Optional, List
import io
import base64
from PIL import Image
import numpy as np

try:
    from config import settings
except ImportError:
    # Fallback configuration if config module fails
    import os
    class FallbackSettings:
        cloudinary_cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "")
        cloudinary_api_key = os.getenv("CLOUDINARY_API_KEY", "")
        cloudinary_api_secret = os.getenv("CLOUDINARY_API_SECRET", "")
    settings = FallbackSettings()

logger = logging.getLogger(__name__)

class CloudinaryService:
    """Service for handling Cloudinary operations"""
    
    def __init__(self):
        """Initialize Cloudinary configuration"""
        self.configure_cloudinary()
    
    def configure_cloudinary(self):
        """Configure Cloudinary with credentials"""
        try:
            cloudinary.config(
                cloud_name=settings.cloudinary_cloud_name,
                api_key=settings.cloudinary_api_key,
                api_secret=settings.cloudinary_api_secret,
                secure=True
            )
            logger.info("Cloudinary configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Cloudinary: {e}")
            raise
    
    def upload_image(self, image_data: bytes, public_id: Optional[str] = None, 
                    folder: str = "ai-fashion", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Upload image to Cloudinary
        
        Args:
            image_data: Raw image bytes
            public_id: Custom public ID for the image
            folder: Cloudinary folder to store the image
            tags: List of tags for the image
            
        Returns:
            Dict containing upload result
        """
        try:
            upload_options = {
                "folder": folder,
                "resource_type": "image",
                "use_filename": True,
                "unique_filename": True,
                "overwrite": False,
                "quality": "auto:best",
                "fetch_format": "auto",
                "transformation": [
                    {"quality": "auto:best"},
                    {"fetch_format": "auto"}
                ]
            }
            
            if public_id:
                upload_options["public_id"] = f"{folder}/{public_id}"
            
            if tags:
                upload_options["tags"] = tags
            
            # Upload image
            result = cloudinary.uploader.upload(
                image_data,
                **upload_options
            )
            
            logger.info(f"Image uploaded successfully: {result.get('public_id')}")
            
            return {
                "success": True,
                "public_id": result.get("public_id"),
                "url": result.get("secure_url"),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
                "etag": result.get("etag"),
                "version": result.get("version"),
                "created_at": result.get("created_at")
            }
            
        except Exception as e:
            logger.error(f"Failed to upload image to Cloudinary: {e}")
            return {
                "success": False,
                "error": str(e),
                "public_id": None,
                "url": None
            }
    
    def upload_skin_tone_analysis(self, image_data: bytes, analysis_result: Dict[str, Any], 
                                 user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload image with skin tone analysis metadata
        
        Args:
            image_data: Raw image bytes
            analysis_result: Skin tone analysis results
            user_id: Optional user identifier
            
        Returns:
            Dict containing upload result with analysis context
        """
        try:
            # Generate public ID with analysis info
            monk_tone = analysis_result.get('monk_skin_tone', 'unknown')
            public_id = f"analysis_{monk_tone}_{user_id or 'anonymous'}"
            
            # Prepare tags
            tags = [
                "skin-tone-analysis",
                monk_tone,
                f"confidence-{int(analysis_result.get('confidence', 0) * 100)}"
            ]
            
            # Add context metadata
            context = {
                "monk_tone": analysis_result.get('monk_skin_tone'),
                "monk_hex": analysis_result.get('monk_hex'),
                "confidence": analysis_result.get('confidence'),
                "dominant_rgb": str(analysis_result.get('dominant_rgb', [])),
                "analysis_method": analysis_result.get('analysis_method', 'enhanced')
            }
            
            upload_options = {
                "folder": "ai-fashion/skin-tone-analysis",
                "public_id": public_id,
                "tags": tags,
                "context": context,
                "resource_type": "image",
                "quality": "auto:best",
                "fetch_format": "auto"
            }
            
            result = cloudinary.uploader.upload(image_data, **upload_options)
            
            logger.info(f"Skin tone analysis image uploaded: {result.get('public_id')}")
            
            return {
                "success": True,
                "public_id": result.get("public_id"),
                "url": result.get("secure_url"),
                "analysis_context": context,
                "tags": tags,
                "bytes": result.get("bytes")
            }
            
        except Exception as e:
            logger.error(f"Failed to upload skin tone analysis image: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_optimized_url(self, public_id: str, transformations: Optional[List[Dict]] = None) -> str:
        """
        Get optimized URL for an image
        
        Args:
            public_id: Cloudinary public ID
            transformations: List of transformation parameters
            
        Returns:
            Optimized image URL
        """
        try:
            default_transformations = [
                {"quality": "auto:best"},
                {"fetch_format": "auto"},
                {"dpr": "auto"}
            ]
            
            if transformations:
                default_transformations.extend(transformations)
            
            url, _ = cloudinary_url(
                public_id,
                transformation=default_transformations,
                secure=True
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate optimized URL: {e}")
            return ""
    
    def delete_image(self, public_id: str) -> Dict[str, Any]:
        """
        Delete image from Cloudinary
        
        Args:
            public_id: Cloudinary public ID
            
        Returns:
            Dict containing deletion result
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            
            success = result.get("result") == "ok"
            
            if success:
                logger.info(f"Image deleted successfully: {public_id}")
            else:
                logger.warning(f"Failed to delete image: {public_id}, result: {result}")
            
            return {
                "success": success,
                "result": result.get("result"),
                "public_id": public_id
            }
            
        except Exception as e:
            logger.error(f"Error deleting image {public_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "public_id": public_id
            }
    
    def get_image_info(self, public_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an image
        
        Args:
            public_id: Cloudinary public ID
            
        Returns:
            Dict containing image information
        """
        try:
            result = cloudinary.api.resource(public_id)
            
            return {
                "success": True,
                "public_id": result.get("public_id"),
                "url": result.get("secure_url"),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
                "created_at": result.get("created_at"),
                "tags": result.get("tags", []),
                "context": result.get("context", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get image info for {public_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_images_by_tag(self, tag: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search images by tag
        
        Args:
            tag: Tag to search for
            max_results: Maximum number of results
            
        Returns:
            Dict containing search results
        """
        try:
            result = cloudinary.api.resources_by_tag(
                tag,
                max_results=max_results,
                resource_type="image"
            )
            
            images = []
            for resource in result.get("resources", []):
                images.append({
                    "public_id": resource.get("public_id"),
                    "url": resource.get("secure_url"),
                    "width": resource.get("width"),
                    "height": resource.get("height"),
                    "created_at": resource.get("created_at"),
                    "tags": resource.get("tags", [])
                })
            
            return {
                "success": True,
                "images": images,
                "total_count": len(images)
            }
            
        except Exception as e:
            logger.error(f"Failed to search images by tag {tag}: {e}")
            return {
                "success": False,
                "error": str(e),
                "images": []
            }

# Create global instance
cloudinary_service = CloudinaryService()
