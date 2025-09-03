"""
Advanced color matching and analysis module for AI-Fashion backend.

This module provides sophisticated color matching algorithms, undertone detection,
and seasonal color analysis for both makeup and fashion products.
"""

import colorsys
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import math
import re
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Undertone(Enum):
    """Skin undertone classifications."""
    COOL = "cool"
    WARM = "warm"
    NEUTRAL = "neutral"


class ColorTemperature(Enum):
    """Color temperature classifications."""
    VERY_COOL = "very_cool"
    COOL = "cool"
    NEUTRAL_COOL = "neutral_cool"
    NEUTRAL = "neutral"
    NEUTRAL_WARM = "neutral_warm"
    WARM = "warm"
    VERY_WARM = "very_warm"


@dataclass
class ColorProfile:
    """Color profile for a product or recommendation."""
    hex_code: str
    rgb: Tuple[int, int, int]
    hsl: Tuple[float, float, float]
    hsv: Tuple[float, float, float]
    undertone: Undertone
    temperature: ColorTemperature
    saturation_level: str
    lightness_level: str
    complementary_colors: List[str]
    analogous_colors: List[str]
    triadic_colors: List[str]


class ColorMatcher:
    """Advanced color matching and analysis engine."""
    
    def __init__(self):
        """Initialize the color matcher with reference data."""
        self.undertone_ranges = self._load_undertone_ranges()
        self.seasonal_palettes = self._load_enhanced_seasonal_palettes()
        self.skin_tone_database = self._load_skin_tone_database()
        
    def _load_undertone_ranges(self) -> Dict[str, Any]:
        """Load undertone detection ranges."""
        return {
            "cool": {
                "hue_ranges": [(240, 300), (0, 30)],  # Blues, purples, cool reds
                "saturation_min": 0.3,
                "keywords": ["pink", "blue", "purple", "cool", "ash", "platinum", "silver"]
            },
            "warm": {
                "hue_ranges": [(30, 60), (300, 360)],  # Yellows, oranges, warm reds
                "saturation_min": 0.3,
                "keywords": ["yellow", "orange", "gold", "warm", "honey", "caramel", "bronze"]
            },
            "neutral": {
                "hue_ranges": [(60, 240)],  # Greens and some blues
                "saturation_max": 0.2,
                "keywords": ["beige", "taupe", "neutral", "natural", "balanced"]
            }
        }
    
    def _load_enhanced_seasonal_palettes(self) -> Dict[str, Any]:
        """Load comprehensive seasonal color palettes."""
        return {
            "spring": {
                "light": {
                    "colors": [
                        "#FFE4E1", "#FFB6C1", "#FFA07A", "#FFE4B5", "#F0FFF0",
                        "#E0FFFF", "#F5F5DC", "#FFF8DC", "#FFEFD5", "#FFE4CC"
                    ],
                    "characteristics": ["light", "warm", "clear", "delicate"]
                },
                "warm": {
                    "colors": [
                        "#FF6347", "#FF4500", "#FFD700", "#ADFF2F", "#32CD32",
                        "#00CED1", "#FF1493", "#FF69B4", "#FFA500", "#8B4513"
                    ],
                    "characteristics": ["warm", "vibrant", "clear", "energetic"]
                },
                "clear": {
                    "colors": [
                        "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF",
                        "#00FFFF", "#FFA500", "#800080", "#008000", "#000080"
                    ],
                    "characteristics": ["clear", "bright", "saturated", "bold"]
                }
            },
            "summer": {
                "light": {
                    "colors": [
                        "#E6E6FA", "#DDA0DD", "#AFEEEE", "#F0F8FF", "#F5F5F5",
                        "#FFE4E1", "#E0E0E0", "#D3D3D3", "#C0C0C0", "#B0C4DE"
                    ],
                    "characteristics": ["light", "cool", "soft", "muted"]
                },
                "cool": {
                    "colors": [
                        "#4169E1", "#0000CD", "#8A2BE2", "#9400D3", "#4B0082",
                        "#483D8B", "#6495ED", "#7B68EE", "#9370DB", "#8B008B"
                    ],
                    "characteristics": ["cool", "blue-based", "elegant", "sophisticated"]
                },
                "soft": {
                    "colors": [
                        "#D8BFD8", "#DDA0DD", "#EE82EE", "#DA70D6", "#BA55D3",
                        "#9370DB", "#8FBC8F", "#20B2AA", "#48D1CC", "#87CEEB"
                    ],
                    "characteristics": ["soft", "muted", "gentle", "romantic"]
                }
            },
            "autumn": {
                "warm": {
                    "colors": [
                        "#A0522D", "#8B4513", "#CD853F", "#D2691E", "#B8860B",
                        "#DAA520", "#FF8C00", "#FF7F50", "#DC143C", "#B22222"
                    ],
                    "characteristics": ["warm", "rich", "earthy", "golden"]
                },
                "deep": {
                    "colors": [
                        "#8B0000", "#800000", "#8B4513", "#A0522D", "#556B2F",
                        "#808000", "#6B8E23", "#228B22", "#008B8B", "#483D8B"
                    ],
                    "characteristics": ["deep", "rich", "intense", "sophisticated"]
                },
                "soft": {
                    "colors": [
                        "#BC8F8F", "#F4A460", "#DEB887", "#D2B48C", "#BDB76B",
                        "#CD853F", "#DAA520", "#B8860B", "#20B2AA", "#708090"
                    ],
                    "characteristics": ["muted", "soft", "earthy", "natural"]
                }
            },
            "winter": {
                "cool": {
                    "colors": [
                        "#000000", "#FFFFFF", "#FF0000", "#0000FF", "#008000",
                        "#800080", "#FF1493", "#00CED1", "#4169E1", "#8B008B"
                    ],
                    "characteristics": ["cool", "crisp", "contrasting", "clear"]
                },
                "deep": {
                    "colors": [
                        "#000000", "#8B0000", "#800000", "#4B0082", "#483D8B",
                        "#2F4F4F", "#008B8B", "#006400", "#8B008B", "#191970"
                    ],
                    "characteristics": ["deep", "rich", "dramatic", "intense"]
                },
                "clear": {
                    "colors": [
                        "#FF0000", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
                        "#000000", "#FFFFFF", "#008000", "#800080", "#FFA500"
                    ],
                    "characteristics": ["clear", "bright", "pure", "vivid"]
                }
            }
        }
    
    def _load_skin_tone_database(self) -> Dict[str, Any]:
        """Load comprehensive skin tone database."""
        return {
            "very_fair": {
                "hex_ranges": ["#F5F5DC", "#FAF0E6", "#FFF8DC", "#FFFAF0"],
                "rgb_ranges": [(245, 245, 220), (250, 240, 230)],
                "undertones": {
                    "cool": ["#F5F5DC", "#FAF0E6"],
                    "warm": ["#FFF8DC", "#FFFAF0"],
                    "neutral": ["#F8F8FF", "#F0F8FF"]
                },
                "best_colors": ["soft pink", "peach", "light coral", "baby blue", "lavender"],
                "avoid_colors": ["bright orange", "warm yellow", "olive", "brown"]
            },
            "fair": {
                "hex_ranges": ["#FAEBD7", "#FFE4C4", "#FFDAB9", "#FFEBCD"],
                "rgb_ranges": [(250, 235, 215), (255, 228, 196)],
                "undertones": {
                    "cool": ["#FAEBD7", "#FFE4C4"],
                    "warm": ["#FFDAB9", "#FFEBCD"],
                    "neutral": ["#F5DEB3", "#WHEAT"]
                },
                "best_colors": ["rose", "coral", "soft red", "dusty blue", "sage"],
                "avoid_colors": ["bright yellow", "orange", "olive green"]
            },
            "light": {
                "hex_ranges": ["#F5DEB3", "#DEB887", "#D2B48C", "#BC8F8F"],
                "rgb_ranges": [(245, 222, 179), (210, 180, 140)],
                "undertones": {
                    "cool": ["#BC8F8F", "#D2B48C"],
                    "warm": ["#F5DEB3", "#DEB887"],
                    "neutral": ["#D3D3D3", "#C0C0C0"]
                },
                "best_colors": ["coral", "peach", "teal", "forest green", "burgundy"],
                "avoid_colors": ["neon colors", "very pale pastels"]
            },
            "medium": {
                "hex_ranges": ["#CD853F", "#DAA520", "#B8860B", "#A0522D"],
                "rgb_ranges": [(205, 133, 63), (160, 82, 45)],
                "undertones": {
                    "cool": ["#CD853F", "#DAA520"],
                    "warm": ["#B8860B", "#A0522D"],
                    "neutral": ["#808080", "#696969"]
                },
                "best_colors": ["warm red", "orange", "gold", "emerald", "deep purple"],
                "avoid_colors": ["pale colors", "ash tones"]
            },
            "deep": {
                "hex_ranges": ["#8B4513", "#A0522D", "#654321", "#8B7355"],
                "rgb_ranges": [(139, 69, 19), (101, 67, 33)],
                "undertones": {
                    "cool": ["#8B7355", "#696969"],
                    "warm": ["#8B4513", "#A0522D"],
                    "neutral": ["#654321", "#555555"]
                },
                "best_colors": ["deep red", "burgundy", "gold", "emerald", "royal blue"],
                "avoid_colors": ["pale pastels", "light colors"]
            },
            "very_deep": {
                "hex_ranges": ["#654321", "#3C2414", "#2F1B14", "#1C1C1C"],
                "rgb_ranges": [(101, 67, 33), (28, 28, 28)],
                "undertones": {
                    "cool": ["#2F1B14", "#1C1C1C"],
                    "warm": ["#654321", "#3C2414"],
                    "neutral": ["#333333", "#2C2C2C"]
                },
                "best_colors": ["rich colors", "jewel tones", "gold", "copper", "emerald"],
                "avoid_colors": ["pale colors", "pastels", "light neutrals"]
            }
        }
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except ValueError:
            raise ValueError(f"Invalid hex color: {hex_color}")
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB to hex color."""
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def rgb_to_hsl(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSL."""
        r, g, b = [x / 255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s, l)
    
    def rgb_to_hsv(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSV."""
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return (h * 360, s, v)
    
    def color_distance(self, color1: str, color2: str) -> float:
        """Calculate color distance using CIEDE2000 formula (simplified)."""
        try:
            rgb1 = self.hex_to_rgb(color1)
            rgb2 = self.hex_to_rgb(color2)
            
            # Simplified Euclidean distance in RGB space
            # For production, consider implementing proper CIEDE2000
            distance = math.sqrt(
                sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2))
            )
            
            # Normalize to 0-1 range
            return distance / (255 * math.sqrt(3))
        except ValueError:
            return 1.0  # Maximum distance for invalid colors
    
    def detect_undertone(self, hex_color: str) -> Undertone:
        """Detect undertone of a color."""
        try:
            rgb = self.hex_to_rgb(hex_color)
            hsl = self.rgb_to_hsl(rgb)
            hue, saturation, lightness = hsl
            
            # Cool undertones: blues, purples, cool reds
            if (240 <= hue <= 300) or (hue <= 30 and saturation > 0.3):
                return Undertone.COOL
            
            # Warm undertones: yellows, oranges, warm reds
            elif (30 <= hue <= 120) and saturation > 0.3:
                return Undertone.WARM
            
            # Neutral: low saturation or green-based colors
            else:
                return Undertone.NEUTRAL
                
        except ValueError:
            return Undertone.NEUTRAL
    
    def get_color_temperature(self, hex_color: str) -> ColorTemperature:
        """Get detailed color temperature classification."""
        try:
            rgb = self.hex_to_rgb(hex_color)
            hsl = self.rgb_to_hsl(rgb)
            hue, saturation, lightness = hsl
            
            if hue <= 30 or hue >= 330:  # Reds
                if saturation > 0.7:
                    return ColorTemperature.WARM if hue < 15 else ColorTemperature.COOL
                else:
                    return ColorTemperature.NEUTRAL
            elif 30 < hue <= 60:  # Oranges/Yellows
                return ColorTemperature.VERY_WARM if saturation > 0.5 else ColorTemperature.WARM
            elif 60 < hue <= 120:  # Yellows/Greens
                return ColorTemperature.WARM if saturation > 0.5 else ColorTemperature.NEUTRAL_WARM
            elif 120 < hue <= 180:  # Greens/Cyans
                return ColorTemperature.NEUTRAL_COOL if saturation > 0.3 else ColorTemperature.NEUTRAL
            elif 180 < hue <= 240:  # Cyans/Blues
                return ColorTemperature.COOL if saturation > 0.5 else ColorTemperature.NEUTRAL_COOL
            else:  # Blues/Purples
                return ColorTemperature.VERY_COOL if saturation > 0.7 else ColorTemperature.COOL
                
        except ValueError:
            return ColorTemperature.NEUTRAL
    
    def get_complementary_colors(self, hex_color: str) -> List[str]:
        """Get complementary colors for a given color."""
        try:
            rgb = self.hex_to_rgb(hex_color)
            hsl = self.rgb_to_hsl(rgb)
            hue, saturation, lightness = hsl
            
            # Complementary hue is 180 degrees opposite
            comp_hue = (hue + 180) % 360
            
            # Create variations with different saturations and lightness
            complementary_colors = []
            
            for s_var in [saturation * 0.8, saturation, saturation * 1.2]:
                for l_var in [lightness * 0.8, lightness, lightness * 1.2]:
                    s_var = min(1.0, max(0.0, s_var))
                    l_var = min(1.0, max(0.0, l_var))
                    
                    # Convert back to RGB
                    r, g, b = colorsys.hls_to_rgb(comp_hue / 360, l_var, s_var)
                    rgb_comp = (int(r * 255), int(g * 255), int(b * 255))
                    hex_comp = self.rgb_to_hex(rgb_comp)
                    
                    if hex_comp not in complementary_colors:
                        complementary_colors.append(hex_comp)
            
            return complementary_colors[:5]  # Return top 5
            
        except ValueError:
            return []
    
    def get_analogous_colors(self, hex_color: str) -> List[str]:
        """Get analogous colors (adjacent on color wheel)."""
        try:
            rgb = self.hex_to_rgb(hex_color)
            hsl = self.rgb_to_hsl(rgb)
            hue, saturation, lightness = hsl
            
            analogous_colors = []
            
            # Get colors 30 degrees on either side
            for hue_shift in [-60, -30, 30, 60]:
                new_hue = (hue + hue_shift) % 360
                
                # Convert back to RGB
                r, g, b = colorsys.hls_to_rgb(new_hue / 360, lightness, saturation)
                rgb_analog = (int(r * 255), int(g * 255), int(b * 255))
                hex_analog = self.rgb_to_hex(rgb_analog)
                analogous_colors.append(hex_analog)
            
            return analogous_colors
            
        except ValueError:
            return []
    
    def get_triadic_colors(self, hex_color: str) -> List[str]:
        """Get triadic colors (120 degrees apart on color wheel)."""
        try:
            rgb = self.hex_to_rgb(hex_color)
            hsl = self.rgb_to_hsl(rgb)
            hue, saturation, lightness = hsl
            
            triadic_colors = []
            
            # Get colors 120 degrees apart
            for hue_shift in [120, 240]:
                new_hue = (hue + hue_shift) % 360
                
                # Convert back to RGB
                r, g, b = colorsys.hls_to_rgb(new_hue / 360, lightness, saturation)
                rgb_triadic = (int(r * 255), int(g * 255), int(b * 255))
                hex_triadic = self.rgb_to_hex(rgb_triadic)
                triadic_colors.append(hex_triadic)
            
            return triadic_colors
            
        except ValueError:
            return []
    
    def create_color_profile(self, hex_color: str) -> ColorProfile:
        """Create a comprehensive color profile."""
        try:
            rgb = self.hex_to_rgb(hex_color)
            hsl = self.rgb_to_hsl(rgb)
            hsv = self.rgb_to_hsv(rgb)
            
            undertone = self.detect_undertone(hex_color)
            temperature = self.get_color_temperature(hex_color)
            
            # Determine saturation and lightness levels
            saturation_level = self._get_saturation_level(hsl[1])
            lightness_level = self._get_lightness_level(hsl[2])
            
            # Get color harmonies
            complementary = self.get_complementary_colors(hex_color)
            analogous = self.get_analogous_colors(hex_color)
            triadic = self.get_triadic_colors(hex_color)
            
            return ColorProfile(
                hex_code=hex_color,
                rgb=rgb,
                hsl=hsl,
                hsv=hsv,
                undertone=undertone,
                temperature=temperature,
                saturation_level=saturation_level,
                lightness_level=lightness_level,
                complementary_colors=complementary,
                analogous_colors=analogous,
                triadic_colors=triadic
            )
            
        except ValueError as e:
            logger.error(f"Error creating color profile for {hex_color}: {e}")
            # Return default profile
            return ColorProfile(
                hex_code="#000000",
                rgb=(0, 0, 0),
                hsl=(0, 0, 0),
                hsv=(0, 0, 0),
                undertone=Undertone.NEUTRAL,
                temperature=ColorTemperature.NEUTRAL,
                saturation_level="unknown",
                lightness_level="unknown",
                complementary_colors=[],
                analogous_colors=[],
                triadic_colors=[]
            )
    
    def _get_saturation_level(self, saturation: float) -> str:
        """Classify saturation level."""
        if saturation < 0.2:
            return "muted"
        elif saturation < 0.5:
            return "moderate"
        elif saturation < 0.8:
            return "vibrant"
        else:
            return "intense"
    
    def _get_lightness_level(self, lightness: float) -> str:
        """Classify lightness level."""
        if lightness < 0.2:
            return "very_dark"
        elif lightness < 0.4:
            return "dark"
        elif lightness < 0.6:
            return "medium"
        elif lightness < 0.8:
            return "light"
        else:
            return "very_light"
    
    def match_colors_for_skin_tone(self, skin_tone_hex: str, product_colors: List[str]) -> List[Dict[str, Any]]:
        """Match product colors to a specific skin tone."""
        skin_profile = self.create_color_profile(skin_tone_hex)
        matches = []
        
        for color in product_colors:
            try:
                color_profile = self.create_color_profile(color)
                distance = self.color_distance(skin_tone_hex, color)
                
                # Calculate compatibility score
                compatibility_score = self._calculate_compatibility(skin_profile, color_profile)
                
                matches.append({
                    "color": color,
                    "profile": color_profile,
                    "distance": distance,
                    "compatibility_score": compatibility_score,
                    "undertone_match": skin_profile.undertone == color_profile.undertone,
                    "recommended": compatibility_score > 0.7
                })
                
            except Exception as e:
                logger.error(f"Error matching color {color}: {e}")
                continue
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return matches
    
    def _calculate_compatibility(self, skin_profile: ColorProfile, color_profile: ColorProfile) -> float:
        """Calculate compatibility score between skin tone and product color."""
        score = 0.0
        
        # Undertone compatibility (40% weight)
        if skin_profile.undertone == color_profile.undertone:
            score += 0.4
        elif skin_profile.undertone == Undertone.NEUTRAL or color_profile.undertone == Undertone.NEUTRAL:
            score += 0.2
        
        # Color temperature compatibility (30% weight)
        temp_compatibility = self._get_temperature_compatibility(
            skin_profile.temperature, color_profile.temperature
        )
        score += temp_compatibility * 0.3
        
        # Saturation compatibility (20% weight)
        sat_compatibility = self._get_saturation_compatibility(
            skin_profile.saturation_level, color_profile.saturation_level
        )
        score += sat_compatibility * 0.2
        
        # Lightness compatibility (10% weight)
        light_compatibility = self._get_lightness_compatibility(
            skin_profile.lightness_level, color_profile.lightness_level
        )
        score += light_compatibility * 0.1
        
        return min(1.0, score)
    
    def _get_temperature_compatibility(self, skin_temp: ColorTemperature, color_temp: ColorTemperature) -> float:
        """Calculate temperature compatibility score."""
        temp_values = {
            ColorTemperature.VERY_COOL: -3,
            ColorTemperature.COOL: -2,
            ColorTemperature.NEUTRAL_COOL: -1,
            ColorTemperature.NEUTRAL: 0,
            ColorTemperature.NEUTRAL_WARM: 1,
            ColorTemperature.WARM: 2,
            ColorTemperature.VERY_WARM: 3
        }
        
        skin_val = temp_values[skin_temp]
        color_val = temp_values[color_temp]
        
        # Calculate compatibility based on temperature difference
        diff = abs(skin_val - color_val)
        
        if diff == 0:
            return 1.0
        elif diff <= 1:
            return 0.8
        elif diff <= 2:
            return 0.6
        elif diff <= 3:
            return 0.4
        else:
            return 0.2
    
    def _get_saturation_compatibility(self, skin_sat: str, color_sat: str) -> float:
        """Calculate saturation compatibility score."""
        sat_values = {"muted": 1, "moderate": 2, "vibrant": 3, "intense": 4}
        
        skin_val = sat_values.get(skin_sat, 2)
        color_val = sat_values.get(color_sat, 2)
        
        diff = abs(skin_val - color_val)
        
        if diff == 0:
            return 1.0
        elif diff <= 1:
            return 0.8
        elif diff <= 2:
            return 0.6
        else:
            return 0.4
    
    def _get_lightness_compatibility(self, skin_light: str, color_light: str) -> float:
        """Calculate lightness compatibility score."""
        light_values = {
            "very_dark": 1, "dark": 2, "medium": 3, "light": 4, "very_light": 5
        }
        
        skin_val = light_values.get(skin_light, 3)
        color_val = light_values.get(color_light, 3)
        
        diff = abs(skin_val - color_val)
        
        if diff == 0:
            return 1.0
        elif diff <= 1:
            return 0.8
        elif diff <= 2:
            return 0.6
        else:
            return 0.4
    
    def get_seasonal_recommendations(self, season: str, subtype: str) -> List[str]:
        """Get color recommendations for a specific seasonal type."""
        try:
            return self.seasonal_palettes[season.lower()][subtype.lower()]["colors"]
        except KeyError:
            logger.warning(f"Unknown seasonal type: {season} {subtype}")
            return []
    
    def detect_season_from_colors(self, colors: List[str]) -> Dict[str, Any]:
        """Detect seasonal type from a list of colors."""
        season_scores = {}
        
        for season, subtypes in self.seasonal_palettes.items():
            season_scores[season] = {}
            
            for subtype, data in subtypes.items():
                palette_colors = data["colors"]
                score = 0
                
                # Calculate how well the input colors match this seasonal palette
                for color in colors:
                    min_distance = float('inf')
                    for palette_color in palette_colors:
                        distance = self.color_distance(color, palette_color)
                        min_distance = min(min_distance, distance)
                    
                    # Convert distance to score (closer = higher score)
                    score += max(0, 1 - min_distance)
                
                season_scores[season][subtype] = score / len(colors) if colors else 0
        
        # Find the best match
        best_season = None
        best_subtype = None
        best_score = 0
        
        for season, subtypes in season_scores.items():
            for subtype, score in subtypes.items():
                if score > best_score:
                    best_score = score
                    best_season = season
                    best_subtype = subtype
        
        return {
            "season": best_season,
            "subtype": best_subtype,
            "confidence": best_score,
            "all_scores": season_scores
        }


# Global color matcher instance
_color_matcher = None


def get_color_matcher() -> ColorMatcher:
    """Get the global color matcher instance."""
    global _color_matcher
    if _color_matcher is None:
        _color_matcher = ColorMatcher()
    return _color_matcher
