"""
Product service module for AI-Fashion backend.

This module provides enhanced product categorization, filtering, and recommendation
capabilities for both makeup and fashion products.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ProductCategory(Enum):
    """Enhanced product categories."""
    # Makeup Categories
    FOUNDATION = "foundation"
    CONCEALER = "concealer"
    POWDER = "powder"
    BLUSH = "blush"
    BRONZER = "bronzer"
    HIGHLIGHTER = "highlighter"
    CONTOUR = "contour"
    EYESHADOW = "eyeshadow"
    EYELINER = "eyeliner"
    MASCARA = "mascara"
    EYEBROW = "eyebrow"
    LIPSTICK = "lipstick"
    LIP_GLOSS = "lip_gloss"
    LIP_LINER = "lip_liner"
    LIP_BALM = "lip_balm"
    PRIMER = "primer"
    SETTING_SPRAY = "setting_spray"
    SETTING_POWDER = "setting_powder"
    MAKEUP_REMOVER = "makeup_remover"
    SKINCARE = "skincare"
    
    # Fashion Categories
    TOPS = "tops"
    BOTTOMS = "bottoms"
    DRESSES = "dresses"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORIES = "accessories"
    BAGS = "bags"
    JEWELRY = "jewelry"
    ACTIVEWEAR = "activewear"
    SWIMWEAR = "swimwear"
    UNDERGARMENTS = "undergarments"
    FORMAL_WEAR = "formal_wear"
    CASUAL_WEAR = "casual_wear"


class SkinTone(Enum):
    """Enhanced skin tone classifications."""
    VERY_FAIR = "very_fair"
    FAIR = "fair"
    LIGHT = "light"
    LIGHT_MEDIUM = "light_medium"
    MEDIUM = "medium"
    MEDIUM_DEEP = "medium_deep"
    DEEP = "deep"
    VERY_DEEP = "very_deep"


class SeasonalType(Enum):
    """Seasonal color analysis types."""
    SPRING_LIGHT = "spring_light"
    SPRING_WARM = "spring_warm"
    SPRING_CLEAR = "spring_clear"
    SUMMER_LIGHT = "summer_light"
    SUMMER_COOL = "summer_cool"
    SUMMER_SOFT = "summer_soft"
    AUTUMN_WARM = "autumn_warm"
    AUTUMN_DEEP = "autumn_deep"
    AUTUMN_SOFT = "autumn_soft"
    WINTER_COOL = "winter_cool"
    WINTER_DEEP = "winter_deep"
    WINTER_CLEAR = "winter_clear"


@dataclass
class ProductFilter:
    """Enhanced product filtering criteria."""
    category: Optional[ProductCategory] = None
    subcategory: Optional[str] = None
    brand: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    skin_tone: Optional[SkinTone] = None
    seasonal_type: Optional[SeasonalType] = None
    color: Optional[List[str]] = None
    rating_min: Optional[float] = None
    is_cruelty_free: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_organic: Optional[bool] = None
    is_hypoallergenic: Optional[bool] = None
    occasion: Optional[List[str]] = None
    size: Optional[List[str]] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None


class ProductService:
    """Enhanced product service with advanced categorization and filtering."""
    
    def __init__(self):
        """Initialize the product service."""
        self.makeup_categories = self._load_makeup_categories()
        self.fashion_categories = self._load_fashion_categories()
        self.brand_mappings = self._load_brand_mappings()
        self.color_mappings = self._load_color_mappings()
        
    def _load_makeup_categories(self) -> Dict[str, Any]:
        """Load detailed makeup product categories."""
        return {
            "face": {
                "base": ["foundation", "concealer", "primer", "bb cream", "cc cream", "tinted moisturizer"],
                "powder": ["setting powder", "finishing powder", "translucent powder", "compact powder"],
                "color": ["blush", "bronzer", "highlighter", "contour", "cheek tint"],
                "skincare": ["serum", "moisturizer", "sunscreen", "face mask", "cleanser"]
            },
            "eyes": {
                "color": ["eyeshadow", "eyeshadow palette", "cream eyeshadow", "liquid eyeshadow"],
                "definition": ["eyeliner", "eye pencil", "gel liner", "liquid liner", "kohl"],
                "lashes": ["mascara", "false lashes", "lash primer", "lash serum"],
                "brows": ["eyebrow pencil", "brow gel", "brow powder", "brow pomade", "brow wax"]
            },
            "lips": {
                "color": ["lipstick", "liquid lipstick", "lip stain", "lip crayon"],
                "gloss": ["lip gloss", "lip oil", "tinted balm"],
                "care": ["lip balm", "lip scrub", "lip mask", "lip primer"],
                "definition": ["lip liner", "lip pencil"]
            },
            "tools": {
                "brushes": ["foundation brush", "concealer brush", "powder brush", "blush brush", 
                          "eyeshadow brush", "lip brush", "contour brush"],
                "sponges": ["beauty sponge", "makeup sponge", "blending sponge"],
                "accessories": ["mirror", "tweezers", "eyelash curler", "makeup bag"]
            }
        }
    
    def _load_fashion_categories(self) -> Dict[str, Any]:
        """Load detailed fashion product categories."""
        return {
            "tops": {
                "casual": ["t-shirt", "tank top", "camisole", "crop top", "blouse", "tunic"],
                "formal": ["dress shirt", "button down", "blazer", "suit jacket", "vest"],
                "knitwear": ["sweater", "cardigan", "hoodie", "pullover", "jumper"],
                "activewear": ["sports bra", "athletic top", "workout shirt", "yoga top"]
            },
            "bottoms": {
                "pants": ["jeans", "trousers", "chinos", "cargo pants", "dress pants"],
                "shorts": ["denim shorts", "athletic shorts", "bermuda shorts", "board shorts"],
                "skirts": ["mini skirt", "midi skirt", "maxi skirt", "pencil skirt", "a-line skirt"],
                "activewear": ["leggings", "yoga pants", "athletic shorts", "track pants"]
            },
            "dresses": {
                "casual": ["sundress", "shift dress", "wrap dress", "shirt dress"],
                "formal": ["cocktail dress", "evening gown", "little black dress", "party dress"],
                "special": ["wedding dress", "bridesmaid dress", "prom dress", "graduation dress"]
            },
            "outerwear": {
                "jackets": ["denim jacket", "leather jacket", "bomber jacket", "blazer"],
                "coats": ["trench coat", "wool coat", "parka", "peacoat", "overcoat"],
                "sweaters": ["cardigan", "pullover", "hoodie", "zip-up", "poncho"]
            },
            "footwear": {
                "casual": ["sneakers", "flats", "sandals", "slip-ons", "canvas shoes"],
                "formal": ["dress shoes", "heels", "pumps", "oxfords", "loafers"],
                "athletic": ["running shoes", "training shoes", "basketball shoes", "hiking boots"],
                "boots": ["ankle boots", "knee-high boots", "combat boots", "rain boots"]
            },
            "accessories": {
                "jewelry": ["necklace", "earrings", "bracelet", "ring", "watch", "brooch"],
                "bags": ["handbag", "backpack", "tote bag", "clutch", "crossbody bag", "wallet"],
                "other": ["scarf", "hat", "sunglasses", "belt", "gloves", "hair accessories"]
            }
        }
    
    def _load_brand_mappings(self) -> Dict[str, Any]:
        """Load brand categories and price ranges."""
        return {
            "luxury": {
                "makeup": ["Chanel", "Dior", "Tom Ford", "La Mer", "Sisley", "Clé de Peau"],
                "fashion": ["Gucci", "Prada", "Louis Vuitton", "Hermès", "Chanel", "Dior"],
                "price_range": (100, 1000)
            },
            "high_end": {
                "makeup": ["MAC", "Urban Decay", "NARS", "Too Faced", "Benefit", "Clinique"],
                "fashion": ["Coach", "Kate Spade", "Michael Kors", "Marc Jacobs", "Theory"],
                "price_range": (50, 200)
            },
            "mid_range": {
                "makeup": ["Sephora Collection", "Morphe", "ColourPop", "The Ordinary", "Glossier"],
                "fashion": ["Zara", "H&M", "Uniqlo", "Gap", "Banana Republic", "J.Crew"],
                "price_range": (20, 80)
            },
            "drugstore": {
                "makeup": ["Maybelline", "L'Oreal", "Revlon", "CoverGirl", "NYX", "e.l.f."],
                "fashion": ["Target", "Walmart", "Old Navy", "Forever 21", "H&M"],
                "price_range": (5, 30)
            }
        }
    
    def _load_color_mappings(self) -> Dict[str, Any]:
        """Load color mappings for different skin tones and seasonal types."""
        return {
            "skin_tone_colors": {
                SkinTone.VERY_FAIR: {
                    "best": ["soft pink", "peach", "light coral", "berry", "rose"],
                    "avoid": ["orange", "bright red", "warm brown", "golden yellow"]
                },
                SkinTone.FAIR: {
                    "best": ["rose", "coral", "soft red", "pink", "berry", "plum"],
                    "avoid": ["orange-red", "warm orange", "golden brown"]
                },
                SkinTone.LIGHT: {
                    "best": ["coral", "peach", "rose", "berry", "soft red", "pink"],
                    "avoid": ["very pale colors", "ash tones"]
                },
                SkinTone.LIGHT_MEDIUM: {
                    "best": ["coral", "warm pink", "berry", "red", "orange-red", "brown"],
                    "avoid": ["very pale colors", "ash colors"]
                },
                SkinTone.MEDIUM: {
                    "best": ["warm red", "coral", "berry", "brown", "orange", "warm pink"],
                    "avoid": ["very pale colors", "cool undertones"]
                },
                SkinTone.MEDIUM_DEEP: {
                    "best": ["deep red", "berry", "brown", "orange", "warm colors"],
                    "avoid": ["pale colors", "cool undertones", "ash tones"]
                },
                SkinTone.DEEP: {
                    "best": ["deep red", "burgundy", "brown", "orange", "warm colors"],
                    "avoid": ["pale colors", "cool pastels"]
                },
                SkinTone.VERY_DEEP: {
                    "best": ["deep colors", "rich red", "burgundy", "warm brown", "orange"],
                    "avoid": ["pale colors", "light pastels", "cool tones"]
                }
            },
            "seasonal_colors": {
                SeasonalType.SPRING_LIGHT: ["peach", "coral", "warm pink", "golden yellow", "mint green"],
                SeasonalType.SPRING_WARM: ["orange", "warm red", "golden yellow", "warm green", "coral"],
                SeasonalType.SPRING_CLEAR: ["bright colors", "clear red", "bright pink", "clear blue"],
                SeasonalType.SUMMER_LIGHT: ["soft colors", "lavender", "powder blue", "soft pink", "sage green"],
                SeasonalType.SUMMER_COOL: ["cool colors", "blue", "purple", "cool pink", "gray"],
                SeasonalType.SUMMER_SOFT: ["muted colors", "dusty rose", "soft blue", "sage", "mauve"],
                SeasonalType.AUTUMN_WARM: ["warm colors", "orange", "rust", "golden brown", "olive"],
                SeasonalType.AUTUMN_DEEP: ["deep colors", "burgundy", "deep orange", "brown", "forest green"],
                SeasonalType.AUTUMN_SOFT: ["muted warm colors", "camel", "soft rust", "olive", "dusty orange"],
                SeasonalType.WINTER_COOL: ["cool colors", "true red", "navy", "black", "white", "cool pink"],
                SeasonalType.WINTER_DEEP: ["deep colors", "burgundy", "emerald", "deep purple", "black"],
                SeasonalType.WINTER_CLEAR: ["clear colors", "bright red", "royal blue", "emerald", "fuchsia"]
            }
        }
    
    def categorize_product(self, product_name: str, description: str = "") -> Dict[str, Any]:
        """
        Categorize a product based on its name and description.
        
        Args:
            product_name: Name of the product
            description: Product description
            
        Returns:
            Dict with categorization information
        """
        product_text = f"{product_name} {description}".lower()
        
        # Determine if it's makeup or fashion
        product_type = self._determine_product_type(product_text)
        
        if product_type == "makeup":
            category = self._categorize_makeup_product(product_text)
        else:
            category = self._categorize_fashion_product(product_text)
        
        return {
            "product_type": product_type,
            "main_category": category.get("main"),
            "subcategory": category.get("sub"),
            "specific_type": category.get("specific"),
            "tags": category.get("tags", [])
        }
    
    def _determine_product_type(self, product_text: str) -> str:
        """Determine if product is makeup or fashion."""
        makeup_keywords = [
            "foundation", "concealer", "lipstick", "mascara", "eyeshadow", "blush",
            "bronzer", "highlighter", "primer", "powder", "makeup", "cosmetic",
            "beauty", "skincare", "serum", "moisturizer", "cleanser"
        ]
        
        fashion_keywords = [
            "shirt", "pants", "dress", "jacket", "shoes", "bag", "jeans", "skirt",
            "top", "sweater", "coat", "boots", "sneakers", "blazer", "hoodie",
            "accessories", "jewelry", "watch", "belt", "scarf", "hat"
        ]
        
        makeup_score = sum(1 for keyword in makeup_keywords if keyword in product_text)
        fashion_score = sum(1 for keyword in fashion_keywords if keyword in product_text)
        
        return "makeup" if makeup_score > fashion_score else "fashion"
    
    def _categorize_makeup_product(self, product_text: str) -> Dict[str, Any]:
        """Categorize makeup products."""
        for main_cat, subcats in self.makeup_categories.items():
            for sub_cat, items in subcats.items():
                for item in items:
                    if item.lower() in product_text:
                        return {
                            "main": main_cat,
                            "sub": sub_cat,
                            "specific": item,
                            "tags": self._extract_makeup_tags(product_text)
                        }
        
        return {"main": "other", "sub": "unknown", "specific": "unknown", "tags": []}
    
    def _categorize_fashion_product(self, product_text: str) -> Dict[str, Any]:
        """Categorize fashion products."""
        for main_cat, subcats in self.fashion_categories.items():
            for sub_cat, items in subcats.items():
                for item in items:
                    if item.lower() in product_text:
                        return {
                            "main": main_cat,
                            "sub": sub_cat,
                            "specific": item,
                            "tags": self._extract_fashion_tags(product_text)
                        }
        
        return {"main": "other", "sub": "unknown", "specific": "unknown", "tags": []}
    
    def _extract_makeup_tags(self, product_text: str) -> List[str]:
        """Extract relevant tags from makeup product text."""
        tags = []
        
        # Finish types
        if any(word in product_text for word in ["matte", "matt"]):
            tags.append("matte")
        if any(word in product_text for word in ["shimmer", "shimmery", "glitter"]):
            tags.append("shimmer")
        if any(word in product_text for word in ["satin", "cream", "creamy"]):
            tags.append("satin")
        if any(word in product_text for word in ["dewy", "luminous", "radiant"]):
            tags.append("dewy")
        
        # Special properties
        if any(word in product_text for word in ["waterproof", "water-resistant"]):
            tags.append("waterproof")
        if any(word in product_text for word in ["long-lasting", "long wear", "24hr"]):
            tags.append("long-lasting")
        if any(word in product_text for word in ["cruelty-free", "cruelty free"]):
            tags.append("cruelty-free")
        if any(word in product_text for word in ["vegan"]):
            tags.append("vegan")
        if any(word in product_text for word in ["organic", "natural"]):
            tags.append("organic")
        if any(word in product_text for word in ["hypoallergenic"]):
            tags.append("hypoallergenic")
        
        # Coverage
        if any(word in product_text for word in ["full coverage", "high coverage"]):
            tags.append("full-coverage")
        if any(word in product_text for word in ["medium coverage"]):
            tags.append("medium-coverage")
        if any(word in product_text for word in ["light coverage", "sheer"]):
            tags.append("light-coverage")
        
        return tags
    
    def _extract_fashion_tags(self, product_text: str) -> List[str]:
        """Extract relevant tags from fashion product text."""
        tags = []
        
        # Style
        if any(word in product_text for word in ["casual", "everyday"]):
            tags.append("casual")
        if any(word in product_text for word in ["formal", "dress", "business"]):
            tags.append("formal")
        if any(word in product_text for word in ["athletic", "sport", "workout", "gym"]):
            tags.append("athletic")
        if any(word in product_text for word in ["vintage", "retro"]):
            tags.append("vintage")
        
        # Occasion
        if any(word in product_text for word in ["party", "evening", "cocktail"]):
            tags.append("party")
        if any(word in product_text for word in ["work", "office", "professional"]):
            tags.append("work")
        if any(word in product_text for word in ["summer", "beach", "vacation"]):
            tags.append("summer")
        if any(word in product_text for word in ["winter", "warm", "cozy"]):
            tags.append("winter")
        
        # Material
        if any(word in product_text for word in ["cotton", "organic cotton"]):
            tags.append("cotton")
        if any(word in product_text for word in ["denim", "jean"]):
            tags.append("denim")
        if any(word in product_text for word in ["leather", "genuine leather"]):
            tags.append("leather")
        if any(word in product_text for word in ["silk", "satin"]):
            tags.append("silk")
        if any(word in product_text for word in ["wool", "cashmere"]):
            tags.append("wool")
        
        return tags
    
    def get_color_recommendations(self, skin_tone: SkinTone, seasonal_type: Optional[SeasonalType] = None) -> Dict[str, List[str]]:
        """
        Get color recommendations based on skin tone and seasonal type.
        
        Args:
            skin_tone: User's skin tone
            seasonal_type: Optional seasonal color type
            
        Returns:
            Dict with recommended and colors to avoid
        """
        recommendations = {
            "recommended": [],
            "avoid": [],
            "seasonal_colors": []
        }
        
        # Get skin tone recommendations
        if skin_tone in self.color_mappings["skin_tone_colors"]:
            skin_colors = self.color_mappings["skin_tone_colors"][skin_tone]
            recommendations["recommended"] = skin_colors.get("best", [])
            recommendations["avoid"] = skin_colors.get("avoid", [])
        
        # Add seasonal colors if provided
        if seasonal_type and seasonal_type in self.color_mappings["seasonal_colors"]:
            recommendations["seasonal_colors"] = self.color_mappings["seasonal_colors"][seasonal_type]
        
        return recommendations
    
    def filter_products(self, products_df: pd.DataFrame, filters: ProductFilter) -> pd.DataFrame:
        """
        Filter products based on multiple criteria.
        
        Args:
            products_df: DataFrame with product data
            filters: ProductFilter object with filtering criteria
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = products_df.copy()
        
        # Apply category filter
        if filters.category:
            category_keywords = self._get_category_keywords(filters.category)
            if 'product' in filtered_df.columns:
                mask = filtered_df['product'].str.lower().str.contains(
                    '|'.join(category_keywords), case=False, na=False
                )
                filtered_df = filtered_df[mask]
        
        # Apply brand filter
        if filters.brand:
            if 'brand' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['brand'].isin(filters.brand)]
        
        # Apply price filter
        if filters.price_min is not None or filters.price_max is not None:
            if 'price' in filtered_df.columns:
                # Convert price to numeric, handling various formats
                filtered_df['price_numeric'] = filtered_df['price'].apply(self._extract_price)
                
                if filters.price_min is not None:
                    filtered_df = filtered_df[filtered_df['price_numeric'] >= filters.price_min]
                if filters.price_max is not None:
                    filtered_df = filtered_df[filtered_df['price_numeric'] <= filters.price_max]
        
        # Apply skin tone filter
        if filters.skin_tone:
            if 'mst' in filtered_df.columns:
                # Convert skin tone to Monk scale if needed
                monk_mapping = self._skin_tone_to_monk(filters.skin_tone)
                filtered_df = filtered_df[filtered_df['mst'].isin(monk_mapping)]
        
        # Apply color filter
        if filters.color:
            color_recommendations = self.get_color_recommendations(
                filters.skin_tone or SkinTone.MEDIUM, 
                filters.seasonal_type
            )
            # Filter based on recommended colors
            if 'hex' in filtered_df.columns or 'color' in filtered_df.columns:
                # Implementation would depend on how colors are stored
                pass
        
        return filtered_df
    
    def _get_category_keywords(self, category: ProductCategory) -> List[str]:
        """Get keywords for a product category."""
        category_map = {
            ProductCategory.FOUNDATION: ["foundation", "base", "bb cream", "cc cream"],
            ProductCategory.LIPSTICK: ["lipstick", "lip color", "liquid lipstick"],
            ProductCategory.EYESHADOW: ["eyeshadow", "eye shadow", "eyeshadow palette"],
            ProductCategory.MASCARA: ["mascara", "lash", "eyelash"],
            ProductCategory.TOPS: ["shirt", "top", "blouse", "t-shirt", "tank"],
            ProductCategory.BOTTOMS: ["pants", "jeans", "trousers", "shorts", "skirt"],
            ProductCategory.DRESSES: ["dress", "gown", "sundress"],
            # Add more mappings as needed
        }
        return category_map.get(category, [category.value])
    
    def _extract_price(self, price_str: str) -> float:
        """Extract numeric price from string."""
        if pd.isna(price_str) or price_str == "":
            return 0.0
        
        # Remove currency symbols and extract numbers
        price_clean = re.sub(r'[^\d.,]', '', str(price_str))
        
        try:
            # Handle different decimal separators
            if ',' in price_clean and '.' in price_clean:
                # Assume comma is thousands separator
                price_clean = price_clean.replace(',', '')
            elif ',' in price_clean:
                # Could be decimal separator in some locales
                if len(price_clean.split(',')[-1]) <= 2:
                    price_clean = price_clean.replace(',', '.')
                else:
                    price_clean = price_clean.replace(',', '')
            
            return float(price_clean)
        except (ValueError, AttributeError):
            return 0.0
    
    def _skin_tone_to_monk(self, skin_tone: SkinTone) -> List[str]:
        """Convert skin tone enum to Monk scale values."""
        mapping = {
            SkinTone.VERY_FAIR: ["Monk01", "Monk02"],
            SkinTone.FAIR: ["Monk02", "Monk03"],
            SkinTone.LIGHT: ["Monk03", "Monk04"],
            SkinTone.LIGHT_MEDIUM: ["Monk04", "Monk05"],
            SkinTone.MEDIUM: ["Monk05", "Monk06"],
            SkinTone.MEDIUM_DEEP: ["Monk06", "Monk07"],
            SkinTone.DEEP: ["Monk07", "Monk08"],
            SkinTone.VERY_DEEP: ["Monk08", "Monk09", "Monk10"]
        }
        return mapping.get(skin_tone, [])
    
    def get_product_recommendations(self, 
                                  user_profile: Dict[str, Any], 
                                  products_df: pd.DataFrame,
                                  recommendation_type: str = "similar") -> List[Dict[str, Any]]:
        """
        Get personalized product recommendations.
        
        Args:
            user_profile: User preferences and characteristics
            products_df: Available products
            recommendation_type: Type of recommendation algorithm
            
        Returns:
            List of recommended products
        """
        recommendations = []
        
        # Extract user preferences
        skin_tone = user_profile.get('skin_tone')
        seasonal_type = user_profile.get('seasonal_type')
        preferred_brands = user_profile.get('preferred_brands', [])
        budget_range = user_profile.get('budget_range', (0, 2000))  # Increased budget range
        
        # Get color recommendations
        if skin_tone:
            color_rec = self.get_color_recommendations(
                SkinTone(skin_tone) if isinstance(skin_tone, str) else skin_tone,
                SeasonalType(seasonal_type) if seasonal_type and isinstance(seasonal_type, str) else seasonal_type
            )
            
            # Use more lenient filtering to show more products
            filters = ProductFilter(
                brand=preferred_brands if preferred_brands else None,
                price_min=budget_range[0],
                price_max=budget_range[1],
                skin_tone=SkinTone(skin_tone) if isinstance(skin_tone, str) else skin_tone
            )
            
            filtered_products = self.filter_products(products_df, filters)
            
            # If we have too few products, relax the filters
            if len(filtered_products) < 50:
                relaxed_filters = ProductFilter(
                    price_min=0,
                    price_max=budget_range[1] * 2,  # Double the budget range
                    skin_tone=SkinTone(skin_tone) if isinstance(skin_tone, str) else skin_tone
                )
                filtered_products = self.filter_products(products_df, relaxed_filters)
            
            # Score and rank products
            scored_products = self._score_products(filtered_products, user_profile, color_rec)
            
            # Return more recommendations
            recommendations = scored_products.head(50).to_dict('records')
        
        return recommendations
    
    def _score_products(self, products_df: pd.DataFrame, user_profile: Dict[str, Any], color_rec: Dict[str, List[str]]) -> pd.DataFrame:
        """Score products based on user preferences."""
        products_df = products_df.copy()
        products_df['recommendation_score'] = 0.0
        
        # Score based on color match
        if 'hex' in products_df.columns:
            # Implementation would depend on color matching algorithm
            pass
        
        # Score based on brand preference
        if 'brand' in products_df.columns and user_profile.get('preferred_brands'):
            brand_bonus = products_df['brand'].isin(user_profile['preferred_brands']).astype(int) * 10
            products_df['recommendation_score'] += brand_bonus
        
        # Score based on price preference
        if 'price' in products_df.columns:
            products_df['price_numeric'] = products_df['price'].apply(self._extract_price)
            budget_range = user_profile.get('budget_range', (0, 1000))
            
            # Higher score for products within budget
            within_budget = (
                (products_df['price_numeric'] >= budget_range[0]) & 
                (products_df['price_numeric'] <= budget_range[1])
            ).astype(int) * 15
            products_df['recommendation_score'] += within_budget
        
        # Sort by score
        return products_df.sort_values('recommendation_score', ascending=False)


# Global product service instance
_product_service = None


def get_product_service() -> ProductService:
    """Get the global product service instance."""
    global _product_service
    if _product_service is None:
        _product_service = ProductService()
    return _product_service
