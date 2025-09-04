"""
Enhanced MST-based Color Recommendation Service
Leverages the comprehensive mst_master_palette database table for sophisticated color recommendations
"""
import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.database_manager import get_database_manager
import colorsys

logger = logging.getLogger(__name__)

class MSTColorRecommendationService:
    """
    Advanced color recommendation service using MST Master Palette data
    Provides comprehensive color recommendations based on Monk Skin Tone with 
    occasion-specific, undertone-aware, and style-conscious suggestions
    """
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    async def get_comprehensive_color_recommendations(
        self,
        skin_tone: str,
        occasion: Optional[str] = None,
        preference: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get comprehensive color recommendations using MST Master Palette data
        
        Args:
            skin_tone: Monk skin tone (e.g., "Monk05", "MST-5")
            occasion: Optional occasion filter (work, casual, festive_wedding, formal_black_tie)
            preference: Optional preference (bright, neutral, pastels, bold)
            limit: Maximum number of colors to return per category
            
        Returns:
            Comprehensive color recommendation dictionary with multiple categories
        """
        try:
            # Extract MST ID from skin tone
            mst_id = self._extract_mst_id(skin_tone)
            if not mst_id:
                return await self._get_fallback_recommendations(skin_tone)
            
            # Get MST master palette data
            palette_data = await self._get_mst_palette_data(mst_id)
            if not palette_data:
                return await self._get_fallback_recommendations(skin_tone)
            
            # Build comprehensive recommendations
            recommendations = await self._build_comprehensive_recommendations(
                palette_data, occasion, preference, limit
            )
            
            # Add metadata and styling guidance
            recommendations.update({
                "mst_id": mst_id,
                "monk_skin_tone": skin_tone,
                "seasonal_types": palette_data.get("seasonal_type", []),
                "common_undertones": palette_data.get("common_undertones", []),
                "recommended_metals": palette_data.get("metals", []),
                "denim_recommendations": palette_data.get("denim_wash", []),
                "styling_guidance": {
                    "contrast_rules": palette_data.get("contrast_rules", ""),
                    "pairing_rules": palette_data.get("pairing_rules", ""),
                    "prints_patterns": palette_data.get("prints_patterns", "")
                }
            })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in get_comprehensive_color_recommendations: {e}")
            return await self._get_fallback_recommendations(skin_tone)
    
    async def get_occasion_specific_colors(
        self,
        skin_tone: str,
        occasion: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get colors specifically tailored for an occasion
        
        Args:
            skin_tone: Monk skin tone
            occasion: Specific occasion (work, casual, festive_wedding, formal_black_tie)
            limit: Maximum colors to return
            
        Returns:
            Occasion-specific color recommendations
        """
        try:
            mst_id = self._extract_mst_id(skin_tone)
            if not mst_id:
                return {"error": "Invalid skin tone format"}
            
            palette_data = await self._get_mst_palette_data(mst_id)
            if not palette_data:
                return {"error": "No palette data found"}
            
            # Get occasion-specific palette
            occasion_palettes = palette_data.get("occasion_palettes", {})
            if occasion not in occasion_palettes:
                # Default to base palette if specific occasion not found
                occasion_colors = palette_data.get("base_palette", [])
            else:
                occasion_colors = occasion_palettes[occasion]
            
            # Format colors with names and additional info
            formatted_colors = []
            for hex_code in occasion_colors[:limit]:
                color_info = await self._get_color_details(hex_code)
                formatted_colors.append(color_info)
            
            return {
                "occasion": occasion,
                "colors": formatted_colors,
                "styling_tips": self._get_occasion_styling_tips(occasion, palette_data),
                "complementary_neutrals": await self._get_complementary_neutrals(palette_data),
                "recommended_metals": palette_data.get("metals", [])
            }
            
        except Exception as e:
            logger.error(f"Error in get_occasion_specific_colors: {e}")
            return {"error": str(e)}
    
    async def get_color_harmony_suggestions(
        self,
        skin_tone: str,
        base_color: str,
        harmony_type: str = "complementary"
    ) -> Dict[str, Any]:
        """
        Get color harmony suggestions based on a base color and MST palette
        
        Args:
            skin_tone: Monk skin tone
            base_color: Base hex color for harmony calculation
            harmony_type: Type of harmony (complementary, triadic, analogous, split_complementary)
            
        Returns:
            Color harmony suggestions within the MST palette
        """
        try:
            mst_id = self._extract_mst_id(skin_tone)
            if not mst_id:
                return {"error": "Invalid skin tone format"}
            
            palette_data = await self._get_mst_palette_data(mst_id)
            if not palette_data:
                return {"error": "No palette data found"}
            
            # Get all available colors from palette
            all_palette_colors = self._get_all_palette_colors(palette_data)
            
            # Calculate harmony colors
            harmony_colors = self._calculate_color_harmony(base_color, harmony_type)
            
            # Find closest matches in MST palette
            matching_colors = await self._find_closest_palette_matches(
                harmony_colors, all_palette_colors
            )
            
            return {
                "base_color": base_color,
                "harmony_type": harmony_type,
                "suggested_combinations": matching_colors,
                "palette_guidance": palette_data.get("pairing_rules", ""),
                "contrast_level": palette_data.get("contrast_rules", "")
            }
            
        except Exception as e:
            logger.error(f"Error in get_color_harmony_suggestions: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    def _extract_mst_id(self, skin_tone: str) -> Optional[int]:
        """Extract MST ID from various skin tone formats"""
        if not skin_tone:
            return None
            
        # Handle various formats: "Monk05", "MST-5", "Monk 5", "5", etc.
        patterns = [
            r'monk\s*(\d+)',  # Monk05, Monk 5, monk5
            r'mst[-\s]*(\d+)',  # MST-5, MST 5, mst5
            r'^(\d+)$'  # Just the number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, skin_tone.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    async def _get_mst_palette_data(self, mst_id: int) -> Optional[Dict[str, Any]]:
        """Get MST master palette data from database"""
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT 
                            seasonal_type,
                            common_undertones,
                            base_palette,
                            accent_palette,
                            avoid_palette,
                            neutrals_light,
                            neutrals_dark,
                            metals,
                            denim_wash,
                            prints_patterns,
                            contrast_rules,
                            pairing_rules,
                            occasion_palettes,
                            examples,
                            notes
                        FROM mst_master_palette 
                        WHERE mst_id = :mst_id
                    """),
                    {"mst_id": mst_id}
                )
                
                row = result.fetchone()
                if row:
                    return {
                        "seasonal_type": row[0],
                        "common_undertones": row[1],
                        "base_palette": row[2],
                        "accent_palette": row[3],
                        "avoid_palette": row[4],
                        "neutrals_light": row[5],
                        "neutrals_dark": row[6],
                        "metals": row[7],
                        "denim_wash": row[8],
                        "prints_patterns": row[9],
                        "contrast_rules": row[10],
                        "pairing_rules": row[11],
                        "occasion_palettes": row[12],
                        "examples": row[13],
                        "notes": row[14]
                    }
                    
        except Exception as e:
            logger.error(f"Error getting MST palette data: {e}")
            
        return None
    
    async def _build_comprehensive_recommendations(
        self,
        palette_data: Dict[str, Any],
        occasion: Optional[str],
        preference: Optional[str],
        limit: int
    ) -> Dict[str, Any]:
        """Build comprehensive color recommendations from palette data"""
        recommendations = {
            "primary_colors": [],
            "accent_colors": [],
            "neutral_lights": [],
            "neutral_darks": [],
            "colors_to_avoid": [],
            "occasion_specific": {}
        }
        
        # Process base palette
        base_colors = palette_data.get("base_palette", [])
        for hex_code in base_colors[:limit//2]:
            color_info = await self._get_color_details(hex_code)
            recommendations["primary_colors"].append(color_info)
        
        # Process accent palette
        accent_colors = palette_data.get("accent_palette", [])
        for hex_code in accent_colors[:limit//3]:
            color_info = await self._get_color_details(hex_code)
            recommendations["accent_colors"].append(color_info)
        
        # Process neutrals
        light_neutrals = palette_data.get("neutrals_light", [])
        for hex_code in light_neutrals:
            color_info = await self._get_color_details(hex_code)
            recommendations["neutral_lights"].append(color_info)
        
        dark_neutrals = palette_data.get("neutrals_dark", [])
        for hex_code in dark_neutrals:
            color_info = await self._get_color_details(hex_code)
            recommendations["neutral_darks"].append(color_info)
        
        # Process avoid colors
        avoid_colors = palette_data.get("avoid_palette", [])
        for hex_code in avoid_colors:
            color_info = await self._get_color_details(hex_code)
            recommendations["colors_to_avoid"].append(color_info)
        
        # Process occasion-specific colors
        occasion_palettes = palette_data.get("occasion_palettes", {})
        for occ, colors in occasion_palettes.items():
            occ_colors = []
            for hex_code in colors[:10]:  # Limit per occasion
                color_info = await self._get_color_details(hex_code)
                occ_colors.append(color_info)
            recommendations["occasion_specific"][occ] = occ_colors
        
        return recommendations
    
    async def _get_color_details(self, hex_code: str) -> Dict[str, Any]:
        """Get detailed color information including name and properties"""
        try:
            # Try to get color name from comprehensive colors table
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT color_name, color_family, brightness_level, undertone
                        FROM comprehensive_colors 
                        WHERE hex_code = :hex_code
                        LIMIT 1
                    """),
                    {"hex_code": hex_code}
                )
                
                row = result.fetchone()
                if row:
                    return {
                        "hex": hex_code,
                        "name": row[0],
                        "color_family": row[1],
                        "brightness_level": row[2],
                        "undertone": row[3]
                    }
        except Exception:
            pass
        
        # Fallback to basic color analysis
        color_name = self._generate_color_name(hex_code)
        return {
            "hex": hex_code,
            "name": color_name,
            "color_family": self._get_color_family(hex_code),
            "brightness_level": self._get_brightness_level(hex_code),
            "undertone": self._analyze_undertone(hex_code)
        }
    
    def _generate_color_name(self, hex_code: str) -> str:
        """Generate a descriptive name for a hex color"""
        try:
            # Remove # if present
            hex_code = hex_code.lstrip('#')
            
            # Convert to RGB
            r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
            
            # Convert to HSV for better color analysis
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            # Determine base color
            hue_names = {
                (0, 30): "Red", (30, 60): "Orange", (60, 120): "Yellow",
                (120, 180): "Green", (180, 240): "Blue", (240, 300): "Purple",
                (300, 360): "Pink"
            }
            
            base_name = "Gray"
            for (min_h, max_h), name in hue_names.items():
                if min_h <= h * 360 < max_h:
                    base_name = name
                    break
            
            # Add descriptors based on saturation and value
            if s < 0.2:
                if v > 0.8:
                    return f"Light {base_name}"
                elif v < 0.3:
                    return f"Dark Gray"
                else:
                    return f"Gray"
            elif s < 0.5:
                if v > 0.8:
                    return f"Pale {base_name}"
                elif v < 0.4:
                    return f"Dark {base_name}"
                else:
                    return f"Muted {base_name}"
            else:
                if v > 0.8:
                    return f"Bright {base_name}"
                elif v < 0.4:
                    return f"Deep {base_name}"
                else:
                    return base_name
                    
        except Exception:
            return f"Color {hex_code}"
    
    def _get_color_family(self, hex_code: str) -> str:
        """Determine color family from hex code"""
        try:
            hex_code = hex_code.lstrip('#')
            r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            if s < 0.15:
                return "neutral"
            
            h_deg = h * 360
            if 345 <= h_deg or h_deg < 15:
                return "red"
            elif 15 <= h_deg < 45:
                return "orange"
            elif 45 <= h_deg < 75:
                return "yellow"
            elif 75 <= h_deg < 165:
                return "green"
            elif 165 <= h_deg < 255:
                return "blue"
            elif 255 <= h_deg < 285:
                return "purple"
            else:
                return "pink"
                
        except Exception:
            return "unknown"
    
    def _get_brightness_level(self, hex_code: str) -> str:
        """Determine brightness level from hex code"""
        try:
            hex_code = hex_code.lstrip('#')
            r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
            
            # Calculate perceived brightness
            brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255.0
            
            if brightness > 0.7:
                return "light"
            elif brightness > 0.4:
                return "medium"
            else:
                return "dark"
                
        except Exception:
            return "medium"
    
    def _analyze_undertone(self, hex_code: str) -> str:
        """Analyze color undertone"""
        try:
            hex_code = hex_code.lstrip('#')
            r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
            
            # Simple undertone analysis
            if r > g and r > b:
                return "warm"
            elif b > r and b > g:
                return "cool"
            else:
                return "neutral"
                
        except Exception:
            return "neutral"
    
    def _get_all_palette_colors(self, palette_data: Dict[str, Any]) -> List[str]:
        """Get all colors from all palette categories"""
        all_colors = []
        
        color_fields = [
            "base_palette", "accent_palette", "neutrals_light", "neutrals_dark"
        ]
        
        for field in color_fields:
            colors = palette_data.get(field, [])
            if colors:
                all_colors.extend(colors)
        
        # Add occasion colors
        occasion_palettes = palette_data.get("occasion_palettes", {})
        for colors in occasion_palettes.values():
            if colors:
                all_colors.extend(colors)
        
        return list(set(all_colors))  # Remove duplicates
    
    def _calculate_color_harmony(self, base_color: str, harmony_type: str) -> List[str]:
        """Calculate color harmony based on color theory"""
        try:
            hex_code = base_color.lstrip('#')
            r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            harmony_colors = []
            
            if harmony_type == "complementary":
                # Add 180 degrees
                comp_h = (h + 0.5) % 1.0
                comp_r, comp_g, comp_b = colorsys.hsv_to_rgb(comp_h, s, v)
                comp_hex = f"#{int(comp_r*255):02x}{int(comp_g*255):02x}{int(comp_b*255):02x}"
                harmony_colors.append(comp_hex)
                
            elif harmony_type == "triadic":
                # Add 120 and 240 degrees
                for offset in [1/3, 2/3]:
                    tri_h = (h + offset) % 1.0
                    tri_r, tri_g, tri_b = colorsys.hsv_to_rgb(tri_h, s, v)
                    tri_hex = f"#{int(tri_r*255):02x}{int(tri_g*255):02x}{int(tri_b*255):02x}"
                    harmony_colors.append(tri_hex)
                    
            elif harmony_type == "analogous":
                # Add +/- 30 degrees
                for offset in [-1/12, 1/12]:
                    ana_h = (h + offset) % 1.0
                    ana_r, ana_g, ana_b = colorsys.hsv_to_rgb(ana_h, s, v)
                    ana_hex = f"#{int(ana_r*255):02x}{int(ana_g*255):02x}{int(ana_b*255):02x}"
                    harmony_colors.append(ana_hex)
            
            return harmony_colors
            
        except Exception:
            return []
    
    async def _find_closest_palette_matches(
        self, 
        target_colors: List[str], 
        palette_colors: List[str]
    ) -> List[Dict[str, Any]]:
        """Find closest matches in palette for target colors"""
        matches = []
        
        for target in target_colors:
            closest_color = None
            min_distance = float('inf')
            
            for palette_color in palette_colors:
                distance = self._calculate_color_distance(target, palette_color)
                if distance < min_distance:
                    min_distance = distance
                    closest_color = palette_color
            
            if closest_color:
                color_info = await self._get_color_details(closest_color)
                color_info["distance_from_ideal"] = min_distance
                matches.append(color_info)
        
        return matches
    
    def _calculate_color_distance(self, color1: str, color2: str) -> float:
        """Calculate perceptual distance between two colors"""
        try:
            # Convert both colors to RGB
            hex1, hex2 = color1.lstrip('#'), color2.lstrip('#')
            r1, g1, b1 = int(hex1[0:2], 16), int(hex1[2:4], 16), int(hex1[4:6], 16)
            r2, g2, b2 = int(hex2[0:2], 16), int(hex2[2:4], 16), int(hex2[4:6], 16)
            
            # Simple Euclidean distance in RGB space
            return ((r2-r1)**2 + (g2-g1)**2 + (b2-b1)**2)**0.5
            
        except Exception:
            return float('inf')
    
    async def _get_complementary_neutrals(self, palette_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get complementary neutral colors"""
        neutrals = []
        
        light_neutrals = palette_data.get("neutrals_light", [])
        dark_neutrals = palette_data.get("neutrals_dark", [])
        
        for hex_code in (light_neutrals + dark_neutrals)[:6]:
            color_info = await self._get_color_details(hex_code)
            neutrals.append(color_info)
        
        return neutrals
    
    def _get_occasion_styling_tips(self, occasion: str, palette_data: Dict[str, Any]) -> List[str]:
        """Get styling tips for specific occasions"""
        base_rules = palette_data.get("pairing_rules", "").split(";") if palette_data.get("pairing_rules") else []
        contrast_rules = palette_data.get("contrast_rules", "")
        
        occasion_tips = {
            "work": [
                "Stick to medium contrast combinations for professional settings",
                "Pair neutrals with one accent color for sophistication",
                "Avoid overly bright or neon colors in conservative environments"
            ],
            "casual": [
                "Feel free to experiment with brighter accent colors",
                "Mix textures and patterns within your color palette",
                "Comfortable combinations work best for daily wear"
            ],
            "festive_wedding": [
                "Embrace richer, more vibrant colors from your palette",
                "Consider metallic accessories in your recommended metals",
                "Balance bright colors with complementary neutrals"
            ],
            "formal_black_tie": [
                "Choose deeper, more sophisticated colors",
                "Stick to classic combinations with minimal contrast",
                "Let one statement color be the focal point"
            ]
        }
        
        tips = occasion_tips.get(occasion, ["Follow your palette's pairing rules"])
        if contrast_rules:
            tips.append(f"Contrast guidance: {contrast_rules}")
        
        return tips + base_rules
    
    async def _get_fallback_recommendations(self, skin_tone: str) -> Dict[str, Any]:
        """Provide fallback recommendations when MST data is unavailable"""
        return {
            "primary_colors": [
                {"hex": "#002D72", "name": "Navy Blue", "color_family": "blue"},
                {"hex": "#205C40", "name": "Forest Green", "color_family": "green"},
                {"hex": "#890C58", "name": "Burgundy", "color_family": "red"}
            ],
            "accent_colors": [
                {"hex": "#FF8D6D", "name": "Coral", "color_family": "orange"},
                {"hex": "#8E4EC6", "name": "Purple", "color_family": "purple"}
            ],
            "neutral_lights": [
                {"hex": "#F5F5F5", "name": "Off White", "color_family": "neutral"}
            ],
            "neutral_darks": [
                {"hex": "#36454F", "name": "Charcoal", "color_family": "neutral"}
            ],
            "colors_to_avoid": [],
            "occasion_specific": {},
            "error": "MST data not available, showing universal recommendations",
            "monk_skin_tone": skin_tone
        }
