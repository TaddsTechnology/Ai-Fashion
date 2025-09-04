"""
Color Analysis Utilities
Helper functions for color processing, analysis, and Monk Skin Tone operations
"""

import re
import colorsys
import math
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ColorAnalysisUtils:
    """Utility class for color analysis operations"""
    
    @staticmethod
    def extract_mst_id_from_skin_tone(skin_tone: str) -> Optional[int]:
        """
        Extract MST ID from various skin tone formats
        
        Args:
            skin_tone: Input skin tone string (e.g., "Monk05", "MST-5", "Monk 5")
            
        Returns:
            MST ID as integer or None if not found
        """
        if not skin_tone:
            return None
            
        # Handle various formats
        patterns = [
            r'monk\s*(\d+)',      # Monk05, Monk 5, monk5
            r'mst[-\s]*(\d+)',    # MST-5, MST 5, mst5
            r'^(\d+)$'            # Just the number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, skin_tone.lower())
            if match:
                mst_id = int(match.group(1))
                # Validate MST ID range (typically 1-10)
                if 1 <= mst_id <= 10:
                    return mst_id
                    
        return None
    
    @staticmethod
    def normalize_monk_tone_format(skin_tone: str) -> Optional[str]:
        """
        Normalize monk tone to standard format (MonkXX)
        
        Args:
            skin_tone: Input skin tone string
            
        Returns:
            Normalized format or None if invalid
        """
        mst_id = ColorAnalysisUtils.extract_mst_id_from_skin_tone(skin_tone)
        if mst_id:
            return f"Monk{mst_id:02d}"
        return None
    
    @staticmethod
    def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB values
        
        Args:
            hex_code: Hex color code (with or without #)
            
        Returns:
            RGB values as tuple
        """
        hex_code = hex_code.lstrip('#')
        if len(hex_code) != 6:
            raise ValueError(f"Invalid hex code: {hex_code}")
            
        return (
            int(hex_code[0:2], 16),
            int(hex_code[2:4], 16),
            int(hex_code[4:6], 16)
        )
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """
        Convert RGB values to hex color
        
        Args:
            r, g, b: RGB values (0-255)
            
        Returns:
            Hex color code with #
        """
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def calculate_color_distance(color1: str, color2: str) -> float:
        """
        Calculate perceptual distance between two colors using Delta E CIE76
        
        Args:
            color1, color2: Hex color codes
            
        Returns:
            Distance value (lower = more similar)
        """
        try:
            r1, g1, b1 = ColorAnalysisUtils.hex_to_rgb(color1)
            r2, g2, b2 = ColorAnalysisUtils.hex_to_rgb(color2)
            
            # Convert to LAB color space for better perceptual distance
            # Simplified calculation - for production, use proper LAB conversion
            dr = r2 - r1
            dg = g2 - g1
            db = b2 - b1
            
            # Weighted Euclidean distance (approximate perceptual distance)
            return math.sqrt(2 * dr * dr + 4 * dg * dg + 3 * db * db)
            
        except Exception as e:
            logger.error(f"Error calculating color distance: {e}")
            return float('inf')
    
    @staticmethod
    def get_color_temperature(hex_code: str) -> str:
        """
        Determine if a color is warm, cool, or neutral
        
        Args:
            hex_code: Hex color code
            
        Returns:
            Temperature classification: 'warm', 'cool', or 'neutral'
        """
        try:
            r, g, b = ColorAnalysisUtils.hex_to_rgb(hex_code)
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            # Convert hue to degrees
            hue_degrees = h * 360
            
            # Warm colors: red, orange, yellow (0-60, 300-360)
            # Cool colors: blue, green, purple (120-300)
            # Neutral: low saturation or intermediate hues
            
            if s < 0.15:  # Low saturation = neutral
                return 'neutral'
            elif (0 <= hue_degrees <= 60) or (300 <= hue_degrees <= 360):
                return 'warm'
            elif 120 <= hue_degrees <= 240:
                return 'cool'
            else:
                return 'neutral'
                
        except Exception:
            return 'neutral'
    
    @staticmethod
    def get_color_brightness(hex_code: str) -> str:
        """
        Determine color brightness level
        
        Args:
            hex_code: Hex color code
            
        Returns:
            Brightness level: 'light', 'medium', or 'dark'
        """
        try:
            r, g, b = ColorAnalysisUtils.hex_to_rgb(hex_code)
            
            # Calculate perceived brightness (luminance)
            brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255.0
            
            if brightness > 0.7:
                return 'light'
            elif brightness > 0.4:
                return 'medium'
            else:
                return 'dark'
                
        except Exception:
            return 'medium'
    
    @staticmethod
    def generate_color_name(hex_code: str) -> str:
        """
        Generate a descriptive name for a color based on its properties
        
        Args:
            hex_code: Hex color code
            
        Returns:
            Descriptive color name
        """
        try:
            r, g, b = ColorAnalysisUtils.hex_to_rgb(hex_code)
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            # Determine base hue name
            hue_names = {
                (0, 15): "Red", (15, 45): "Orange", (45, 75): "Yellow",
                (75, 105): "Yellow-Green", (105, 135): "Green", (135, 165): "Blue-Green",
                (165, 195): "Cyan", (195, 225): "Blue", (225, 255): "Purple",
                (255, 285): "Magenta", (285, 315): "Pink", (315, 345): "Rose",
                (345, 360): "Red"
            }
            
            hue_degrees = h * 360
            base_name = "Gray"
            
            for (min_h, max_h), name in hue_names.items():
                if min_h <= hue_degrees < max_h:
                    base_name = name
                    break
            
            # Add descriptors based on saturation and value
            if s < 0.2:  # Low saturation
                if v > 0.9:
                    return "White"
                elif v > 0.7:
                    return f"Light {base_name}"
                elif v < 0.3:
                    return "Black" if v < 0.1 else "Dark Gray"
                else:
                    return "Gray"
            elif s < 0.5:  # Medium saturation
                if v > 0.8:
                    return f"Pale {base_name}"
                elif v < 0.4:
                    return f"Dark {base_name}"
                else:
                    return f"Muted {base_name}"
            else:  # High saturation
                if v > 0.8:
                    return f"Bright {base_name}"
                elif v < 0.4:
                    return f"Deep {base_name}"
                else:
                    return base_name
                    
        except Exception:
            return f"Color {hex_code}"
    
    @staticmethod
    def get_complementary_color(hex_code: str) -> str:
        """
        Get the complementary color (opposite on color wheel)
        
        Args:
            hex_code: Input hex color
            
        Returns:
            Complementary color hex code
        """
        try:
            r, g, b = ColorAnalysisUtils.hex_to_rgb(hex_code)
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            # Add 180 degrees to hue
            comp_h = (h + 0.5) % 1.0
            comp_r, comp_g, comp_b = colorsys.hsv_to_rgb(comp_h, s, v)
            
            return ColorAnalysisUtils.rgb_to_hex(
                int(comp_r * 255), int(comp_g * 255), int(comp_b * 255)
            )
            
        except Exception:
            return hex_code
    
    @staticmethod
    def generate_color_harmony(hex_code: str, harmony_type: str) -> List[str]:
        """
        Generate color harmony based on color theory
        
        Args:
            hex_code: Base color
            harmony_type: Type of harmony ('complementary', 'triadic', 'analogous', 'split_complementary')
            
        Returns:
            List of harmony colors
        """
        try:
            r, g, b = ColorAnalysisUtils.hex_to_rgb(hex_code)
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            harmony_colors = []
            
            if harmony_type == "complementary":
                # 180 degrees apart
                comp_h = (h + 0.5) % 1.0
                comp_r, comp_g, comp_b = colorsys.hsv_to_rgb(comp_h, s, v)
                harmony_colors.append(ColorAnalysisUtils.rgb_to_hex(
                    int(comp_r * 255), int(comp_g * 255), int(comp_b * 255)
                ))
                
            elif harmony_type == "triadic":
                # 120 degrees apart
                for offset in [1/3, 2/3]:
                    tri_h = (h + offset) % 1.0
                    tri_r, tri_g, tri_b = colorsys.hsv_to_rgb(tri_h, s, v)
                    harmony_colors.append(ColorAnalysisUtils.rgb_to_hex(
                        int(tri_r * 255), int(tri_g * 255), int(tri_b * 255)
                    ))
                    
            elif harmony_type == "analogous":
                # Adjacent colors (±30 degrees)
                for offset in [-1/12, 1/12]:
                    ana_h = (h + offset) % 1.0
                    ana_r, ana_g, ana_b = colorsys.hsv_to_rgb(ana_h, s, v)
                    harmony_colors.append(ColorAnalysisUtils.rgb_to_hex(
                        int(ana_r * 255), int(ana_g * 255), int(ana_b * 255)
                    ))
                    
            elif harmony_type == "split_complementary":
                # Complementary split (150 and 210 degrees)
                for offset in [5/12, 7/12]:
                    split_h = (h + offset) % 1.0
                    split_r, split_g, split_b = colorsys.hsv_to_rgb(split_h, s, v)
                    harmony_colors.append(ColorAnalysisUtils.rgb_to_hex(
                        int(split_r * 255), int(split_g * 255), int(split_b * 255)
                    ))
            
            return harmony_colors
            
        except Exception as e:
            logger.error(f"Error generating color harmony: {e}")
            return []
    
    @staticmethod
    def find_closest_colors(
        target_color: str, 
        color_list: List[str], 
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find closest matching colors from a list
        
        Args:
            target_color: Target hex color
            color_list: List of hex colors to search
            max_results: Maximum number of results to return
            
        Returns:
            List of closest colors with distance scores
        """
        try:
            matches = []
            
            for color in color_list:
                distance = ColorAnalysisUtils.calculate_color_distance(target_color, color)
                matches.append({
                    "hex": color,
                    "distance": distance,
                    "name": ColorAnalysisUtils.generate_color_name(color)
                })
            
            # Sort by distance and return top matches
            matches.sort(key=lambda x: x["distance"])
            return matches[:max_results]
            
        except Exception as e:
            logger.error(f"Error finding closest colors: {e}")
            return []
    
    @staticmethod
    def analyze_color_palette(colors: List[str]) -> Dict[str, Any]:
        """
        Analyze a color palette and provide insights
        
        Args:
            colors: List of hex colors
            
        Returns:
            Analysis results with temperature, brightness, and harmony info
        """
        try:
            if not colors:
                return {"error": "No colors provided"}
            
            temperatures = []
            brightness_levels = []
            hues = []
            
            for color in colors:
                temperatures.append(ColorAnalysisUtils.get_color_temperature(color))
                brightness_levels.append(ColorAnalysisUtils.get_color_brightness(color))
                
                # Get hue for diversity analysis
                r, g, b = ColorAnalysisUtils.hex_to_rgb(color)
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                hues.append(h * 360)
            
            # Analyze temperature distribution
            temp_counts = {temp: temperatures.count(temp) for temp in set(temperatures)}
            dominant_temp = max(temp_counts, key=temp_counts.get)
            
            # Analyze brightness distribution
            bright_counts = {level: brightness_levels.count(level) for level in set(brightness_levels)}
            
            # Calculate hue diversity (standard deviation of hues)
            if len(hues) > 1:
                hue_mean = sum(hues) / len(hues)
                hue_variance = sum((h - hue_mean) ** 2 for h in hues) / len(hues)
                hue_diversity = math.sqrt(hue_variance)
            else:
                hue_diversity = 0
            
            return {
                "total_colors": len(colors),
                "temperature_analysis": {
                    "dominant_temperature": dominant_temp,
                    "distribution": temp_counts,
                    "is_cohesive": max(temp_counts.values()) / len(colors) > 0.6
                },
                "brightness_analysis": {
                    "distribution": bright_counts,
                    "has_contrast": len(bright_counts) > 1
                },
                "diversity": {
                    "hue_diversity": hue_diversity,
                    "is_diverse": hue_diversity > 60,  # Arbitrary threshold
                    "is_monochromatic": hue_diversity < 30
                },
                "harmony_score": min(100, max(0, 100 - hue_diversity / 3))  # Simple harmony score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing color palette: {e}")
            return {"error": str(e)}

    @staticmethod
    def filter_colors_by_preference(
        colors: List[Dict[str, Any]], 
        preference: str
    ) -> List[Dict[str, Any]]:
        """
        Filter colors based on user preference
        
        Args:
            colors: List of color dictionaries with hex codes
            preference: User preference ('bright', 'muted', 'dark', 'light', 'warm', 'cool')
            
        Returns:
            Filtered list of colors
        """
        try:
            if not preference or preference.lower() == 'all':
                return colors
            
            filtered_colors = []
            preference = preference.lower()
            
            for color in colors:
                hex_code = color.get('hex', color.get('hex_code', ''))
                if not hex_code:
                    continue
                
                temperature = ColorAnalysisUtils.get_color_temperature(hex_code)
                brightness = ColorAnalysisUtils.get_color_brightness(hex_code)
                
                # Apply preference filters
                if preference == 'bright' and brightness == 'light':
                    filtered_colors.append(color)
                elif preference == 'muted' and brightness == 'medium':
                    filtered_colors.append(color)
                elif preference == 'dark' and brightness == 'dark':
                    filtered_colors.append(color)
                elif preference == 'light' and brightness == 'light':
                    filtered_colors.append(color)
                elif preference == 'warm' and temperature == 'warm':
                    filtered_colors.append(color)
                elif preference == 'cool' and temperature == 'cool':
                    filtered_colors.append(color)
                elif preference == 'neutral' and temperature == 'neutral':
                    filtered_colors.append(color)
            
            # If no matches found, return original list
            return filtered_colors if filtered_colors else colors
            
        except Exception as e:
            logger.error(f"Error filtering colors by preference: {e}")
            return colors

    @staticmethod
    def get_seasonal_color_mapping() -> Dict[str, List[str]]:
        """
        Get mapping of MST IDs to seasonal color types
        
        Returns:
            Dictionary mapping MST ranges to seasonal types
        """
        return {
            "1-2": ["Light Spring", "Light Summer"],
            "3": ["Clear Spring"],
            "4": ["Warm Spring"],
            "5": ["Soft Summer", "Soft Autumn"],
            "6": ["Warm Autumn"],
            "7": ["Deep Autumn"],
            "8": ["Deep Winter"],
            "9": ["Cool Winter"],
            "10": ["Clear Winter"]
        }
    
    @staticmethod
    def validate_hex_color(hex_code: str) -> bool:
        """
        Validate if a string is a valid hex color
        
        Args:
            hex_code: Color code to validate
            
        Returns:
            True if valid hex color
        """
        try:
            hex_code = hex_code.lstrip('#')
            return len(hex_code) == 6 and all(c in '0123456789ABCDEFabcdef' for c in hex_code)
        except Exception:
            return False
