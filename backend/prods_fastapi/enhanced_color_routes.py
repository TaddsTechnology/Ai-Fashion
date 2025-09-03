"""
Enhanced Color Routes using MST Master Palette Data
Provides comprehensive color recommendations with seasonal analysis
"""

from fastapi import APIRouter, Query, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional, Dict, Any
import logging

from services.enhanced_color_service import enhanced_color_service

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

# Create router
enhanced_router = APIRouter(prefix="/api/v2", tags=["Enhanced Color Recommendations"])


@enhanced_router.get("/color-recommendations/enhanced")
@limiter.limit("60/minute")  
async def get_enhanced_color_recommendations(
    request: Request,
    monk_tone: str = Query(..., description="Monk skin tone (e.g., 'Monk03', 'Monk 5', '3')"),
    occasion: str = Query("casual", description="Occasion type: work, casual, party, formal"),
    limit: int = Query(20, ge=5, le=50, description="Maximum number of colors to return")
) -> Dict[str, Any]:
    """
    Get enhanced color recommendations using MST master palette data.
    
    **New Features:**
    - Occasion-specific color palettes (work, casual, party, formal)
    - Detailed styling advice (metals, denim, patterns)
    - Colors to avoid
    - Neutral color suggestions
    - Seasonal type analysis
    """
    try:
        logger.info(f"Enhanced color recommendation request: {monk_tone}, occasion: {occasion}")
        
        recommendations = enhanced_color_service.get_comprehensive_recommendations(
            monk_tone=monk_tone,
            occasion=occasion,
            limit=limit
        )
        
        return {
            "success": True,
            "data": recommendations,
            "message": f"Enhanced color recommendations for {monk_tone} ({occasion} occasion)"
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced color recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced recommendations: {str(e)}")


@enhanced_router.get("/seasonal-analysis")
@limiter.limit("30/minute")
async def get_seasonal_analysis(
    request: Request,
    monk_tone: str = Query(..., description="Monk skin tone (e.g., 'Monk03', 'Monk 5')")
) -> Dict[str, Any]:
    """
    Get comprehensive seasonal color analysis for a specific Monk skin tone.
    
    **Features:**
    - Seasonal type classification (Spring, Summer, Autumn, Winter)
    - Undertone analysis
    - Detailed style guide
    - Color examples
    - Professional styling advice
    """
    try:
        logger.info(f"Seasonal analysis request for: {monk_tone}")
        
        analysis = enhanced_color_service.get_seasonal_analysis(monk_tone)
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return {
            "success": True,
            "data": analysis,
            "message": f"Seasonal analysis for {monk_tone}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in seasonal analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get seasonal analysis: {str(e)}")


@enhanced_router.get("/compare-seasons")
@limiter.limit("20/minute")
async def compare_seasonal_analysis(
    request: Request,
    monk_tone1: str = Query(..., description="First Monk skin tone to compare"),
    monk_tone2: str = Query(..., description="Second Monk skin tone to compare")
) -> Dict[str, Any]:
    """
    Compare seasonal color analysis between two Monk skin tones.
    
    **Use Cases:**
    - Understanding differences between similar skin tones
    - Family/couple styling coordination
    - Educational purposes
    """
    try:
        logger.info(f"Season comparison request: {monk_tone1} vs {monk_tone2}")
        
        comparison = enhanced_color_service.compare_seasons(monk_tone1, monk_tone2)
        
        if "error" in comparison:
            raise HTTPException(status_code=400, detail=comparison["error"])
        
        return {
            "success": True,
            "data": comparison,
            "message": f"Seasonal comparison between {monk_tone1} and {monk_tone2}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in season comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare seasons: {str(e)}")


@enhanced_router.get("/occasion-colors")
@limiter.limit("40/minute")
async def get_occasion_specific_colors(
    request: Request,
    monk_tone: str = Query(..., description="Monk skin tone"),
    occasions: str = Query("work,casual,party,formal", description="Comma-separated list of occasions")
) -> Dict[str, Any]:
    """
    Get color recommendations for multiple occasions at once.
    
    **Perfect for:**
    - Wardrobe planning
    - Shopping preparation
    - Style consultations
    """
    try:
        occasion_list = [occ.strip().lower() for occ in occasions.split(",")]
        
        results = {}
        for occasion in occasion_list:
            if occasion:  # Skip empty strings
                results[occasion] = enhanced_color_service.get_comprehensive_recommendations(
                    monk_tone=monk_tone,
                    occasion=occasion,
                    limit=15  # Smaller limit per occasion
                )
        
        return {
            "success": True,
            "data": {
                "monk_tone": monk_tone,
                "occasions": results,
                "total_occasions": len(results)
            },
            "message": f"Multi-occasion color recommendations for {monk_tone}"
        }
        
    except Exception as e:
        logger.error(f"Error in occasion-specific colors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get occasion colors: {str(e)}")


@enhanced_router.get("/styling-guide")
@limiter.limit("30/minute")
async def get_comprehensive_styling_guide(
    request: Request,
    monk_tone: str = Query(..., description="Monk skin tone")
) -> Dict[str, Any]:
    """
    Get comprehensive styling guide including colors, metals, patterns, and rules.
    
    **Complete Styling Package:**
    - Color palette for all occasions
    - Metal recommendations (jewelry, accessories)
    - Denim wash suggestions
    - Print and pattern guidance
    - Contrast and pairing rules
    """
    try:
        # Get comprehensive recommendations for all occasions
        occasions = ["work", "casual", "party", "formal"]
        color_guides = {}
        
        for occasion in occasions:
            color_guides[occasion] = enhanced_color_service.get_comprehensive_recommendations(
                monk_tone=monk_tone,
                occasion=occasion,
                limit=10
            )
        
        # Get seasonal analysis
        seasonal = enhanced_color_service.get_seasonal_analysis(monk_tone)
        
        # Combine into comprehensive guide
        styling_guide = {
            "monk_skin_tone": monk_tone,
            "seasonal_profile": seasonal,
            "occasion_colors": color_guides,
            "universal_styling_tips": {
                "best_metals": color_guides["casual"]["styling_advice"]["metals"],
                "recommended_denim": color_guides["casual"]["styling_advice"]["denim_wash"],
                "pattern_guidance": color_guides["casual"]["styling_advice"]["prints_patterns"],
                "contrast_level": color_guides["casual"]["styling_advice"]["contrast_rules"],
                "color_pairing": color_guides["casual"]["styling_advice"]["pairing_rules"]
            },
            "colors_to_avoid": color_guides["casual"]["colors_to_avoid"],
            "neutral_foundations": color_guides["casual"]["neutrals"]
        }
        
        return {
            "success": True,
            "data": styling_guide,
            "message": f"Comprehensive styling guide for {monk_tone}"
        }
        
    except Exception as e:
        logger.error(f"Error in styling guide: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate styling guide: {str(e)}")


@enhanced_router.get("/quick-palette")
@limiter.limit("100/minute")  # Higher rate limit for quick requests
async def get_quick_color_palette(
    request: Request,
    monk_tone: str = Query(..., description="Monk skin tone"),
    count: int = Query(8, ge=3, le=15, description="Number of colors to return")
) -> Dict[str, Any]:
    """
    Get a quick, simplified color palette - perfect for mobile apps and quick decisions.
    
    **Optimized for:**
    - Mobile applications
    - Quick color choices
    - Real-time styling decisions
    """
    try:
        recommendations = enhanced_color_service.get_comprehensive_recommendations(
            monk_tone=monk_tone,
            occasion="casual",  # Use casual as default
            limit=count
        )
        
        # Simplified response
        quick_palette = {
            "monk_tone": monk_tone,
            "mst_id": recommendations["mst_id"],
            "colors": recommendations["colors_that_suit"],
            "seasonal_type": recommendations["seasonal_type"][0] if recommendations["seasonal_type"] else "Unknown",
            "primary_undertone": recommendations["common_undertones"][0] if recommendations["common_undertones"] else "neutral"
        }
        
        return {
            "success": True,
            "data": quick_palette,
            "message": f"Quick palette for {monk_tone}"
        }
        
    except Exception as e:
        logger.error(f"Error in quick palette: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get quick palette: {str(e)}")


@enhanced_router.get("/mst-info")
async def get_mst_information() -> Dict[str, Any]:
    """
    Get information about available MST (Monk Skin Tone) data and capabilities.
    """
    try:
        available_tones = list(enhanced_color_service.mst_palette_data.keys())
        
        info = {
            "available_mst_ids": sorted(available_tones),
            "total_tones": len(available_tones),
            "supported_occasions": ["work", "casual", "party", "formal", "business", "wedding", "evening"],
            "features": [
                "Seasonal color analysis",
                "Occasion-specific palettes", 
                "Styling advice (metals, denim, patterns)",
                "Colors to avoid",
                "Neutral color suggestions",
                "Undertone analysis",
                "Season comparison"
            ],
            "api_endpoints": {
                "enhanced_recommendations": "/api/v2/color-recommendations/enhanced",
                "seasonal_analysis": "/api/v2/seasonal-analysis",
                "compare_seasons": "/api/v2/compare-seasons",
                "occasion_colors": "/api/v2/occasion-colors",
                "styling_guide": "/api/v2/styling-guide",
                "quick_palette": "/api/v2/quick-palette"
            }
        }
        
        return {
            "success": True,
            "data": info,
            "message": "MST master palette system information"
        }
        
    except Exception as e:
        logger.error(f"Error getting MST info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MST information: {str(e)}")
