"""
MST Master Palette Database Service
Integrates MST data with main application's color recommendation system
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class MSTDatabaseService:
    """Service to fetch MST master palette data from PostgreSQL database"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
        )
        self._cached_data = {}
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url)
    
    def monk_tone_to_mst_id(self, monk_tone: str) -> int:
        """Convert various Monk tone formats to MST ID"""
        try:
            import re
            # Try to extract number from string
            match = re.search(r'\d+', str(monk_tone))
            if match:
                return int(match.group())
            # If no number found, try direct conversion
            return int(monk_tone)
        except (ValueError, AttributeError, TypeError):
            logger.warning(f"Could not parse monk_tone: {monk_tone}, defaulting to 5")
            return 5
    
    def get_mst_palette(self, monk_tone: str) -> Optional[Dict[str, Any]]:
        """Get complete MST palette data for a monk tone"""
        try:
            mst_id = self.monk_tone_to_mst_id(monk_tone)
            
            # Check cache first
            if mst_id in self._cached_data:
                return self._cached_data[mst_id]
            
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM mst_master_palette 
                        WHERE mst_id = %s
                    """, (mst_id,))
                    
                    record = cursor.fetchone()
                    if not record:
                        logger.warning(f"No MST data found for mst_id: {mst_id}")
                        return None
                    
                    # Convert to our format
                    palette_data = {
                        'mst_id': record['mst_id'],
                        'seasonal_type': record['seasonal_type'] or [],
                        'common_undertones': record['common_undertones'] or [],
                        'base_palette': record['base_palette'] or [],
                        'accent_palette': record['accent_palette'] or [],
                        'avoid_palette': record['avoid_palette'] or [],
                        'neutrals_light': record['neutrals_light'] or [],
                        'neutrals_dark': record['neutrals_dark'] or [],
                        'metals': record['metals'] or [],
                        'denim_wash': record['denim_wash'] or [],
                        'prints_patterns': record['prints_patterns'] or '',
                        'contrast_rules': record['contrast_rules'] or '',
                        'pairing_rules': record['pairing_rules'] or '',
                        'occasion_palettes': record['occasion_palettes'] or {},
                        'examples': record['examples'] or [],
                        'notes': record['notes'] or ''
                    }
                    
                    # Cache the result
                    self._cached_data[mst_id] = palette_data
                    return palette_data
                    
        except Exception as e:
            logger.error(f"Error fetching MST palette for {monk_tone}: {e}")
            return None
    
    def get_colors_for_occasion(self, monk_tone: str, occasion: str = "casual") -> List[Dict[str, str]]:
        """Get colors specifically for an occasion"""
        palette_data = self.get_mst_palette(monk_tone)
        if not palette_data:
            return []
        
        # Map occasions to palette keys
        occasion_mapping = {
            "work": "work",
            "business": "work", 
            "professional": "work",
            "office": "work",
            "casual": "casual",
            "everyday": "casual",
            "weekend": "casual",
            "party": "festive_wedding",
            "wedding": "festive_wedding",
            "festive": "festive_wedding",
            "celebration": "festive_wedding",
            "formal": "formal_black_tie",
            "black_tie": "formal_black_tie",
            "evening": "formal_black_tie",
            "gala": "formal_black_tie"
        }
        
        mapped_occasion = occasion_mapping.get(occasion.lower(), "casual")
        occasion_colors = palette_data['occasion_palettes'].get(mapped_occasion, [])
        
        # Format for API response
        formatted_colors = []
        for color_hex in occasion_colors:
            formatted_colors.append({
                "name": self._get_color_name(color_hex),
                "hex": color_hex
            })
        
        return formatted_colors
    
    def get_comprehensive_colors(self, monk_tone: str, occasion: str = "casual", limit: int = 20) -> Dict[str, Any]:
        """Get comprehensive color recommendations in the same format as existing API"""
        palette_data = self.get_mst_palette(monk_tone)
        if not palette_data:
            return {"error": f"No palette data found for {monk_tone}"}
        
        # Get occasion-specific colors
        occasion_colors = self.get_colors_for_occasion(monk_tone, occasion)
        
        # Combine base and accent colors
        all_colors = []
        
        # Add occasion colors first (priority 1)
        all_colors.extend(occasion_colors[:limit//2])
        
        # Add base palette colors (priority 2)
        base_colors = palette_data.get('base_palette', [])
        for color_hex in base_colors[:limit//3]:
            if color_hex not in [c['hex'] for c in all_colors]:  # Avoid duplicates
                all_colors.append({
                    "name": self._get_color_name(color_hex),
                    "hex": color_hex
                })
        
        # Add accent colors (priority 3)
        accent_colors = palette_data.get('accent_palette', [])
        for color_hex in accent_colors[:limit//4]:
            if color_hex not in [c['hex'] for c in all_colors]:  # Avoid duplicates
                all_colors.append({
                    "name": self._get_color_name(color_hex),
                    "hex": color_hex
                })
        
        # Limit results
        final_colors = all_colors[:limit]
        
        return {
            "colors_that_suit": final_colors,
            "seasonal_type": ', '.join(palette_data.get('seasonal_type', [])),
            "monk_skin_tone": monk_tone,
            "mst_id": palette_data['mst_id'],
            "common_undertones": palette_data.get('common_undertones', []),
            "styling_advice": {
                "metals": palette_data.get('metals', []),
                "denim_wash": palette_data.get('denim_wash', []),
                "prints_patterns": palette_data.get('prints_patterns', ''),
                "contrast_rules": palette_data.get('contrast_rules', ''),
                "pairing_rules": palette_data.get('pairing_rules', '')
            },
            "colors_to_avoid": [
                {"name": self._get_color_name(color), "hex": color}
                for color in palette_data.get('avoid_palette', [])
            ],
            "neutrals": {
                "light": palette_data.get('neutrals_light', []),
                "dark": palette_data.get('neutrals_dark', [])
            },
            "message": f"Enhanced MST recommendations for {monk_tone} ({occasion} occasion)"
        }
    
    def get_styling_advice(self, monk_tone: str) -> Dict[str, Any]:
        """Get detailed styling advice for a monk tone"""
        palette_data = self.get_mst_palette(monk_tone)
        if not palette_data:
            return {"error": f"No styling advice found for {monk_tone}"}
        
        return {
            "monk_skin_tone": monk_tone,
            "mst_id": palette_data['mst_id'],
            "seasonal_types": palette_data.get('seasonal_type', []),
            "undertones": palette_data.get('common_undertones', []),
            "metals": palette_data.get('metals', []),
            "denim_recommendations": palette_data.get('denim_wash', []),
            "print_patterns": palette_data.get('prints_patterns', ''),
            "contrast_level": palette_data.get('contrast_rules', ''),
            "color_pairing_tips": palette_data.get('pairing_rules', ''),
            "color_examples": palette_data.get('examples', []),
            "notes": palette_data.get('notes', '')
        }
    
    def get_all_available_mst_ids(self) -> List[int]:
        """Get all available MST IDs in the database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT mst_id FROM mst_master_palette ORDER BY mst_id")
                    return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching MST IDs: {e}")
            return []
    
    def _get_color_name(self, hex_color: str) -> str:
        """Generate a descriptive name for a hex color"""
        # Basic color name mapping
        color_names = {
            "#FF0000": "Red", "#00FF00": "Green", "#0000FF": "Blue",
            "#FFFF00": "Yellow", "#FF00FF": "Magenta", "#00FFFF": "Cyan",
            "#000000": "Black", "#FFFFFF": "White", "#808080": "Gray",
            "#FFA500": "Orange", "#800080": "Purple", "#FFC0CB": "Pink",
            "#A52A2A": "Brown", "#008000": "Forest Green", "#000080": "Navy",
            "#FF1493": "Deep Pink", "#FFD700": "Gold", "#C0C0C0": "Silver"
        }
        
        return color_names.get(hex_color.upper(), f"Color {hex_color}")

# Global instance
mst_db_service = MSTDatabaseService()


def get_mst_color_recommendations(monk_tone: str, occasion: str = "casual", limit: int = 20) -> Dict[str, Any]:
    """
    Main function to get MST-based color recommendations
    This can be used directly in your existing API endpoints
    """
    return mst_db_service.get_comprehensive_colors(monk_tone, occasion, limit)


def get_mst_styling_advice(monk_tone: str) -> Dict[str, Any]:
    """
    Get MST-based styling advice
    """
    return mst_db_service.get_styling_advice(monk_tone)


def get_mst_occasion_colors(monk_tone: str, occasion: str) -> List[Dict[str, str]]:
    """
    Get colors specifically for an occasion
    """
    return mst_db_service.get_colors_for_occasion(monk_tone, occasion)


def get_comprehensive_recommendations(monk_tone: str, occasion: str = "casual", limit: int = 20) -> Dict[str, Any]:
    """
    Get comprehensive color recommendations (alias for get_mst_color_recommendations)
    """
    return get_mst_color_recommendations(monk_tone, occasion, limit)


def get_all_mst_ids() -> List[int]:
    """
    Get all available MST IDs
    """
    return mst_db_service.get_all_available_mst_ids()
