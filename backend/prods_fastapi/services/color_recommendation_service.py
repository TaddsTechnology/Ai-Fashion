"""
Color Recommendation Service
Breaks down large endpoint functions into focused services
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.database_manager import get_database_manager

logger = logging.getLogger(__name__)

class ColorRecommendationService:
    """
    Service for handling color recommendations
    Breaks down complex endpoint logic into focused methods
    """
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    async def get_color_recommendations(
        self,
        skin_tone: str,
        hex_color: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get comprehensive color recommendations for a skin tone
        
        Args:
            skin_tone: Monk skin tone (e.g., "Monk05")
            hex_color: Optional hex color for matching
            limit: Maximum number of colors to return
            
        Returns:
            Dictionary with color recommendations
        """
        try:
            all_colors = []
            seasonal_type = "Universal"
            sources_used = []
            
            # Step 1: Get seasonal type mapping
            seasonal_type = await self._get_seasonal_type(skin_tone)
            
            # Step 2: Get colors from different sources
            if seasonal_type != "Universal":
                # Get from seasonal palettes
                palette_colors = await self._get_palette_colors(seasonal_type)
                all_colors.extend(palette_colors)
                if palette_colors:
                    sources_used.append(f"seasonal_palette ({len(palette_colors)} colors)")
                
                # Get from colors table
                table_colors = await self._get_table_colors(seasonal_type, skin_tone)
                all_colors.extend(table_colors)
                if table_colors:
                    sources_used.append(f"colors_table ({len(table_colors)} colors)")
            
            # Get from comprehensive colors
            comprehensive_colors = await self._get_comprehensive_colors(skin_tone)
            all_colors.extend(comprehensive_colors)
            if comprehensive_colors:
                sources_used.append(f"comprehensive_colors ({len(comprehensive_colors)} colors)")
            
            # Add universal colors if needed
            if len(all_colors) < 10:
                universal_colors = await self._get_universal_colors()
                all_colors.extend(universal_colors)
                if universal_colors:
                    sources_used.append(f"universal_colors ({len(universal_colors)} colors)")
            
            # Apply limit and prioritize colors
            final_colors = self._prioritize_and_limit_colors(all_colors, limit)
            
            logger.info(f"Returning {len(final_colors)} colors from {len(sources_used)} sources")
            
            return self._format_color_response(final_colors, seasonal_type, skin_tone)
            
        except Exception as e:
            logger.error(f"Error in get_color_recommendations: {e}")
            raise
    
    async def _get_seasonal_type(self, skin_tone: str) -> str:
        """Get seasonal type from Monk tone mapping"""
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT seasonal_type 
                        FROM skin_tone_mappings 
                        WHERE monk_tone = :skin_tone
                    """),
                    {"skin_tone": skin_tone}
                )
                
                mapping = result.fetchone()
                if mapping:
                    return mapping[0]
                else:
                    logger.info(f"No seasonal mapping found for {skin_tone}, using Universal")
                    return "Universal"
                    
        except Exception as e:
            logger.error(f"Error getting seasonal type: {e}")
            return "Universal"
    
    async def _get_palette_colors(self, seasonal_type: str) -> List[Dict[str, Any]]:
        """Get colors from seasonal color palettes"""
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT flattering_colors 
                        FROM color_palettes 
                        WHERE skin_tone = :seasonal_type
                    """),
                    {"seasonal_type": seasonal_type}
                )
                
                palette = result.fetchone()
                if palette and palette[0]:
                    flattering_colors = palette[0] if isinstance(palette[0], list) else []
                    return [
                        {
                            "hex_code": color.get("hex", "#000000"),
                            "color_name": color.get("name", "Unknown Color"),
                            "category": "recommended",
                            "source": "seasonal_palette",
                            "seasonal_type": seasonal_type
                        }
                        for color in flattering_colors
                    ]
                    
        except Exception as e:
            logger.error(f"Error getting palette colors: {e}")
        
        return []
    
    async def _get_comprehensive_colors(self, skin_tone: str) -> List[Dict[str, Any]]:
        """Get colors from comprehensive colors table"""
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                        FROM comprehensive_colors 
                        WHERE monk_tones::text LIKE :skin_tone_pattern
                        AND hex_code IS NOT NULL
                        AND color_name IS NOT NULL
                        ORDER BY color_name
                        LIMIT 40
                    """),
                    {"skin_tone_pattern": f'%{skin_tone}%'}
                )
                
                colors = result.fetchall()
                return [
                    {
                        "hex_code": row[0],
                        "color_name": row[1],
                        "category": "recommended",
                        "source": "comprehensive_colors",
                        "color_family": row[2] or "unknown",
                        "brightness_level": row[3] or "medium",
                        "monk_compatible": skin_tone
                    }
                    for row in colors
                ]
                
        except Exception as e:
            logger.error(f"Error getting comprehensive colors: {e}")
        
        return []
    
    async def _get_table_colors(self, seasonal_type: str, skin_tone: str) -> List[Dict[str, Any]]:
        """Get colors from main colors table"""
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT DISTINCT hex_code, color_name, seasonal_palette, category, suitable_skin_tone
                        FROM colors 
                        WHERE (seasonal_palette = :seasonal_type OR suitable_skin_tone LIKE :skin_tone_pattern)
                        AND category = 'recommended'
                        AND hex_code IS NOT NULL
                        AND color_name IS NOT NULL
                        ORDER BY color_name
                        LIMIT 30
                    """),
                    {
                        "seasonal_type": seasonal_type,
                        "skin_tone_pattern": f'%{skin_tone}%'
                    }
                )
                
                colors = result.fetchall()
                return [
                    {
                        "hex_code": row[0],
                        "color_name": row[1],
                        "category": row[3],
                        "source": "colors_table",
                        "seasonal_palette": row[2] or seasonal_type,
                        "suitable_skin_tone": row[4] or "universal"
                    }
                    for row in colors
                ]
                
        except Exception as e:
            logger.error(f"Error getting table colors: {e}")
        
        return []
    
    async def _get_universal_colors(self) -> List[Dict[str, Any]]:
        """Get universal colors as fallback"""
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                        FROM comprehensive_colors 
                        WHERE color_family IN ('blue', 'green', 'red', 'purple', 'neutral', 'brown', 'pink')
                        AND brightness_level IN ('medium', 'dark', 'light')
                        AND hex_code IS NOT NULL
                        AND color_name IS NOT NULL
                        ORDER BY color_name
                        LIMIT 25
                    """)
                )
                
                colors = result.fetchall()
                return [
                    {
                        "hex_code": row[0],
                        "color_name": row[1],
                        "category": "recommended",
                        "source": "universal_colors",
                        "color_family": row[2] or "unknown",
                        "brightness_level": row[3] or "medium"
                    }
                    for row in colors
                ]
                
        except Exception as e:
            logger.error(f"Error getting universal colors: {e}")
        
        return []
    
    def _prioritize_and_limit_colors(self, all_colors: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Prioritize colors and apply limit"""
        # Remove duplicates by hex code
        seen_colors = set()
        unique_colors = []
        
        for color in all_colors:
            hex_code = color.get("hex_code", "").lower()
            if hex_code not in seen_colors:
                seen_colors.add(hex_code)
                unique_colors.append(color)
        
        if len(unique_colors) <= limit:
            return unique_colors
        
        # Prioritize colors from seasonal palettes and comprehensive colors
        priority_sources = ["seasonal_palette", "comprehensive_colors"]
        priority_colors = [c for c in unique_colors if c.get("source") in priority_sources]
        other_colors = [c for c in unique_colors if c.get("source") not in priority_sources]
        
        # Take priority colors first, then fill with others
        final_colors = priority_colors[:limit]
        remaining_slots = limit - len(final_colors)
        
        if remaining_slots > 0:
            final_colors.extend(other_colors[:remaining_slots])
        
        return final_colors
    
    def _format_color_response(self, colors: List[Dict[str, Any]], seasonal_type: str, skin_tone: str) -> Dict[str, Any]:
        """Format the final color response"""
        return {
            "colors_that_suit": [
                {
                    "name": color.get("color_name", "Unknown Color"),
                    "hex": color.get("hex_code", "#000000")
                }
                for color in colors
            ],
            "seasonal_type": seasonal_type,
            "monk_skin_tone": skin_tone,
            "message": f"Enhanced color recommendations for {skin_tone or 'universal skin tone'} from multiple database sources",
            "total_colors": len(colors)
        }


class ColorPaletteService:
    """Service for handling color palette operations"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    async def get_color_palettes_for_skin_tone(self, skin_tone: str, hex_color: Optional[str] = None) -> Dict[str, Any]:
        """
        Get color palettes for specific skin tone
        
        Args:
            skin_tone: Monk skin tone
            hex_color: Optional hex color for matching
            
        Returns:
            Color palette dictionary
        """
        try:
            # Try database approach first
            seasonal_type = await self._get_seasonal_type_mapping(skin_tone)
            
            if seasonal_type:
                palette = await self._get_palette_by_seasonal_type(seasonal_type)
                if palette:
                    return palette
            
            # Fallback to basic colors
            return await self._get_fallback_palette(skin_tone)
            
        except Exception as e:
            logger.error(f"Error getting color palettes: {e}")
            return await self._get_fallback_palette(skin_tone)
    
    async def _get_seasonal_type_mapping(self, skin_tone: str) -> Optional[str]:
        """Get seasonal type from Monk tone mapping"""
        try:
            if "monk" in skin_tone.lower():
                monk_number = ''.join(filter(str.isdigit, skin_tone))
                if monk_number:
                    monk_tone_formatted = f"Monk{monk_number.zfill(2)}"
                    
                    async with self.db_manager.get_async_session() as session:
                        result = await session.execute(
                            text("""
                                SELECT seasonal_type 
                                FROM skin_tone_mappings 
                                WHERE monk_tone = :monk_tone
                            """),
                            {"monk_tone": monk_tone_formatted}
                        )
                        
                        mapping = result.fetchone()
                        if mapping:
                            return mapping[0]
            
            return skin_tone  # Assume it's already a seasonal type
            
        except Exception as e:
            logger.error(f"Error getting seasonal type mapping: {e}")
            return None
    
    async def _get_palette_by_seasonal_type(self, seasonal_type: str) -> Optional[Dict[str, Any]]:
        """Get palette by seasonal type"""
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT flattering_colors, colors_to_avoid, description 
                        FROM color_palettes 
                        WHERE skin_tone = :seasonal_type
                    """),
                    {"seasonal_type": seasonal_type}
                )
                
                palette = result.fetchone()
                if palette:
                    return {
                        "colors": palette[0] or [],
                        "colors_to_avoid": palette[1] or [],
                        "seasonal_type": seasonal_type,
                        "description": palette[2] or f"Colors for {seasonal_type}"
                    }
        
        except Exception as e:
            logger.error(f"Error getting palette by seasonal type: {e}")
        
        return None
    
    async def _get_fallback_palette(self, skin_tone: str) -> Dict[str, Any]:
        """Get fallback color palette"""
        try:
            # Try to get basic colors from database
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT DISTINCT hex_code, color_name 
                        FROM comprehensive_colors 
                        WHERE color_family IN ('blue', 'green', 'red', 'neutral', 'brown')
                        AND hex_code IS NOT NULL AND color_name IS NOT NULL
                        LIMIT 10
                    """)
                )
                
                colors = result.fetchall()
                if colors:
                    colors_list = [{"name": row[1], "hex": row[0]} for row in colors]
                else:
                    colors_list = self._get_hardcoded_fallback_colors()
        
        except Exception:
            colors_list = self._get_hardcoded_fallback_colors()
        
        return {
            "colors": colors_list,
            "colors_to_avoid": [],
            "seasonal_type": skin_tone or "Unknown",
            "description": f"Fallback color palette for {skin_tone or 'unknown skin tone'}"
        }
    
    def _get_hardcoded_fallback_colors(self) -> List[Dict[str, str]]:
        """Get hardcoded fallback colors"""
        return [
            {"name": "Navy Blue", "hex": "#002D72"},
            {"name": "Forest Green", "hex": "#205C40"},
            {"name": "Burgundy", "hex": "#890C58"},
            {"name": "Charcoal", "hex": "#36454F"}
        ]
