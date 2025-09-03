"""
Enhanced Color Recommendation Service using MST Master Palette Data
Integrates the comprehensive mst_master_palette_all.json data for better recommendations
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class EnhancedColorRecommendationService:
    def __init__(self):
        self.mst_palette_data: Dict[int, Dict] = {}
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
        )
        self.load_mst_master_palette()
    
    def load_mst_master_palette(self) -> None:
        """Load the MST master palette data from PostgreSQL database"""
        try:
            # Try to load from database first
            self._load_from_database()
            if self.mst_palette_data:
                logger.info(f"Loaded MST master palette data from database for {len(self.mst_palette_data)} skin tones")
                return
        except Exception as e:
            logger.warning(f"Failed to load from database: {e}")
        
        # Fallback to JSON file if database fails
        try:
            self._load_from_json_file()
            if self.mst_palette_data:
                logger.info(f"Loaded MST master palette data from JSON file for {len(self.mst_palette_data)} skin tones")
                return
        except Exception as e:
            logger.warning(f"Failed to load from JSON file: {e}")
        
        # Ultimate fallback to hardcoded data
        logger.warning("Using fallback data")
        self._load_fallback_data()
    
    def _load_from_database(self) -> None:
        """Load MST data from PostgreSQL database"""
        try:
            conn = psycopg2.connect(self.database_url)
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        mst_id,
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
                    ORDER BY mst_id
                """)
                
                records = cursor.fetchall()
                
                for record in records:
                    mst_id = record['mst_id']
                    # Convert the database record to our expected format
                    # JSONB columns are already parsed, no need for json.loads()
                    self.mst_palette_data[mst_id] = {
                        'mst_id': mst_id,
                        'seasonal_type': record['seasonal_type'] if record['seasonal_type'] else [],
                        'common_undertones': record['common_undertones'] if record['common_undertones'] else [],
                        'base_palette': record['base_palette'] if record['base_palette'] else [],
                        'accent_palette': record['accent_palette'] if record['accent_palette'] else [],
                        'avoid_palette': record['avoid_palette'] if record['avoid_palette'] else [],
                        'neutrals_light': record['neutrals_light'] if record['neutrals_light'] else [],
                        'neutrals_dark': record['neutrals_dark'] if record['neutrals_dark'] else [],
                        'metals': record['metals'] if record['metals'] else [],
                        'denim_wash': record['denim_wash'] if record['denim_wash'] else [],
                        'prints_patterns': record['prints_patterns'] or '',
                        'contrast_rules': record['contrast_rules'] or '',
                        'pairing_rules': record['pairing_rules'] or '',
                        'occasion_palettes': record['occasion_palettes'] if record['occasion_palettes'] else {},
                        'examples': record['examples'] if record['examples'] else [],
                        'notes': record['notes'] or ''
                    }
                
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to load MST data from database: {e}")
            raise
    
    def _load_from_json_file(self) -> None:
        """Load MST data from JSON file as fallback"""
        possible_paths = [
            "backend/datasets/mst_master_palette_all.json",
            "../datasets/mst_master_palette_all.json",
            "datasets/mst_master_palette_all.json",
            os.path.join(os.path.dirname(__file__), "../../../datasets/mst_master_palette_all.json")
        ]
        
        json_path = None
        for path in possible_paths:
            if os.path.exists(path):
                json_path = path
                break
        
        if not json_path:
            raise FileNotFoundError("MST master palette JSON file not found")
        
        with open(json_path, 'r', encoding='utf-8') as file:
            palette_list = json.load(file)
            
        # Convert list to dictionary keyed by mst_id for faster lookup
        for palette in palette_list:
            self.mst_palette_data[palette['mst_id']] = palette
    
    def _load_fallback_data(self) -> None:
        """Load basic fallback data if main file is not available"""
        self.mst_palette_data = {
            3: {
                "base_palette": ["#00A499", "#007FA3", "#FFB81C", "#DA291C"],
                "accent_palette": ["#FFCD00", "#FF8200", "#E40046"],
                "seasonal_type": ["Clear Spring"],
                "common_undertones": ["warm", "clear", "light"]
            },
            5: {
                "base_palette": ["#24563F", "#B58150", "#7C4D3A", "#71C5E8"],
                "accent_palette": ["#009CA6", "#009F4D", "#1A83D7"],
                "seasonal_type": ["Soft Summer", "Soft Autumn"],
                "common_undertones": ["neutral", "soft"]
            }
        }
    
    def monk_tone_to_mst_id(self, monk_tone: str) -> int:
        """Convert Monk tone string to MST ID integer"""
        try:
            # Handle different formats: "Monk03", "Monk 3", "3", etc.
            if "monk" in monk_tone.lower():
                # Extract number from string like "Monk03" or "Monk 3"
                import re
                match = re.search(r'\d+', monk_tone)
                if match:
                    return int(match.group())
            else:
                # Direct number string
                return int(monk_tone)
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse monk_tone: {monk_tone}, defaulting to 5")
            return 5  # Default to MST-5 (middle range)
    
    def get_comprehensive_recommendations(
        self, 
        monk_tone: str, 
        occasion: str = "casual",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get comprehensive color recommendations based on MST master palette
        
        Args:
            monk_tone: Monk skin tone (e.g., "Monk03", "Monk 5")
            occasion: Occasion type (work, casual, festive_wedding, formal_black_tie)
            limit: Maximum number of colors to return
            
        Returns:
            Dict with comprehensive color recommendations
        """
        mst_id = self.monk_tone_to_mst_id(monk_tone)
        
        if mst_id not in self.mst_palette_data:
            logger.warning(f"No palette data for MST-{mst_id}, using closest available")
            mst_id = min(self.mst_palette_data.keys(), key=lambda x: abs(x - mst_id))
        
        palette_data = self.mst_palette_data[mst_id]
        
        # Get occasion-specific palette
        occasion_palette = self._get_occasion_palette(palette_data, occasion)
        
        # Combine base and accent palettes for variety
        all_colors = []
        
        # Add occasion-specific colors first (highest priority)
        if occasion_palette:
            all_colors.extend([
                {"name": self._get_color_name(color), "hex": color, "category": "occasion", "priority": 1}
                for color in occasion_palette[:limit//2]
            ])
        
        # Add base palette colors
        base_colors = palette_data.get("base_palette", [])
        all_colors.extend([
            {"name": self._get_color_name(color), "hex": color, "category": "base", "priority": 2}
            for color in base_colors[:limit//3]
        ])
        
        # Add accent colors for pop
        accent_colors = palette_data.get("accent_palette", [])
        all_colors.extend([
            {"name": self._get_color_name(color), "hex": color, "category": "accent", "priority": 3}
            for color in accent_colors[:limit//4]
        ])
        
        # Remove duplicates while preserving priority order
        seen_colors = set()
        unique_colors = []
        for color in all_colors:
            if color["hex"] not in seen_colors:
                seen_colors.add(color["hex"])
                unique_colors.append(color)
        
        # Limit results
        final_colors = unique_colors[:limit]
        
        return {
            "monk_skin_tone": monk_tone,
            "mst_id": mst_id,
            "seasonal_type": palette_data.get("seasonal_type", ["Unknown"]),
            "common_undertones": palette_data.get("common_undertones", ["neutral"]),
            "occasion": occasion,
            "colors_that_suit": [
                {"name": color["name"], "hex": color["hex"]} 
                for color in final_colors
            ],
            "total_colors": len(final_colors),
            "styling_advice": {
                "metals": palette_data.get("metals", ["silver", "gold"]),
                "denim_wash": palette_data.get("denim_wash", ["mid"]),
                "prints_patterns": palette_data.get("prints_patterns", "Versatile prints work well"),
                "contrast_rules": palette_data.get("contrast_rules", "Medium contrast is ideal"),
                "pairing_rules": palette_data.get("pairing_rules", "Balance warm and cool tones")
            },
            "colors_to_avoid": [
                {"name": self._get_color_name(color), "hex": color}
                for color in palette_data.get("avoid_palette", [])
            ],
            "neutrals": {
                "light": palette_data.get("neutrals_light", ["#FFFFFF", "#F5F5F5"]),
                "dark": palette_data.get("neutrals_dark", ["#333333", "#000000"])
            }
        }
    
    def _get_occasion_palette(self, palette_data: Dict, occasion: str) -> List[str]:
        """Get colors for specific occasion from palette data"""
        occasion_palettes = palette_data.get("occasion_palettes", {})
        
        # Map common occasion names to our palette keys
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
        return occasion_palettes.get(mapped_occasion, [])
    
    def _get_color_name(self, hex_color: str) -> str:
        """Generate a descriptive name for a hex color"""
        # Basic color name mapping - you could expand this with a proper color name library
        color_names = {
            "#FF0000": "Red", "#00FF00": "Green", "#0000FF": "Blue",
            "#FFFF00": "Yellow", "#FF00FF": "Magenta", "#00FFFF": "Cyan",
            "#000000": "Black", "#FFFFFF": "White", "#808080": "Gray",
            "#FFA500": "Orange", "#800080": "Purple", "#FFC0CB": "Pink",
            "#A52A2A": "Brown", "#008000": "Forest Green", "#000080": "Navy",
            "#FF1493": "Deep Pink", "#FFD700": "Gold", "#C0C0C0": "Silver"
        }
        
        return color_names.get(hex_color.upper(), f"Color {hex_color}")
    
    def get_seasonal_analysis(self, monk_tone: str) -> Dict[str, Any]:
        """Get detailed seasonal color analysis for a Monk skin tone"""
        mst_id = self.monk_tone_to_mst_id(monk_tone)
        
        if mst_id not in self.mst_palette_data:
            return {"error": f"No seasonal analysis available for MST-{mst_id}"}
        
        palette_data = self.mst_palette_data[mst_id]
        
        return {
            "monk_skin_tone": monk_tone,
            "mst_id": mst_id,
            "seasonal_types": palette_data.get("seasonal_type", []),
            "undertones": palette_data.get("common_undertones", []),
            "style_guide": {
                "metals": palette_data.get("metals", []),
                "denim_recommendations": palette_data.get("denim_wash", []),
                "print_patterns": palette_data.get("prints_patterns", ""),
                "contrast_level": palette_data.get("contrast_rules", ""),
                "color_pairing_tips": palette_data.get("pairing_rules", "")
            },
            "color_examples": palette_data.get("examples", []),
            "notes": palette_data.get("notes", "")
        }
    
    def compare_seasons(self, monk_tone1: str, monk_tone2: str) -> Dict[str, Any]:
        """Compare seasonal analysis between two Monk skin tones"""
        analysis1 = self.get_seasonal_analysis(monk_tone1)
        analysis2 = self.get_seasonal_analysis(monk_tone2)
        
        if "error" in analysis1 or "error" in analysis2:
            return {"error": "Could not compare - missing data for one or both skin tones"}
        
        # Find common and different elements
        common_seasons = set(analysis1["seasonal_types"]) & set(analysis2["seasonal_types"])
        common_undertones = set(analysis1["undertones"]) & set(analysis2["undertones"])
        
        return {
            "comparison": {
                "monk_tone_1": monk_tone1,
                "monk_tone_2": monk_tone2,
                "common_seasons": list(common_seasons),
                "different_seasons": {
                    monk_tone1: list(set(analysis1["seasonal_types"]) - common_seasons),
                    monk_tone2: list(set(analysis2["seasonal_types"]) - common_seasons)
                },
                "common_undertones": list(common_undertones),
                "different_undertones": {
                    monk_tone1: list(set(analysis1["undertones"]) - common_undertones),
                    monk_tone2: list(set(analysis2["undertones"]) - common_undertones)
                }
            },
            "individual_analyses": {
                monk_tone1: analysis1,
                monk_tone2: analysis2
            }
        }


# Initialize the service
enhanced_color_service = EnhancedColorRecommendationService()
