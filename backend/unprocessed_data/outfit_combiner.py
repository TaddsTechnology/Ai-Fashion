import json
import random
from typing import List, Dict, Any
from collections import defaultdict
import re

class OutfitCombiner:
    def __init__(self):
        self.all_products = []
        self.products_by_category = defaultdict(list)
        self.products_by_type = defaultdict(list)
        self.products_by_color = defaultdict(list)
        
    def load_data(self, file_paths: List[str]):
        """Load and combine data from multiple JSON files"""
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # Extract products from each file
                    for item in data:
                        if 'products' in item:
                            self.all_products.extend(item['products'])
                            print(f"Loaded {len(item['products'])} products from {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        # Organize products by categories
        self._organize_products()
        print(f"Total products loaded: {len(self.all_products)}")
        
    def _organize_products(self):
        """Organize products by different categories for easy filtering"""
        for product in self.all_products:
            # By master category
            master_cat = product.get('master_category', '').lower()
            self.products_by_category[master_cat].append(product)
            
            # By product type
            product_type = product.get('product_type', '').lower()
            self.products_by_type[product_type].append(product)
            
            # By color
            color = product.get('base_colour', '').lower()
            self.products_by_color[color].append(product)
    
    def get_stats(self):
        """Get statistics about the combined dataset"""
        stats = {
            'total_products': len(self.all_products),
            'categories': dict([(k, len(v)) for k, v in self.products_by_category.items()]),
            'product_types': dict([(k, len(v)) for k, v in self.products_by_type.items()]),
            'colors': dict([(k, len(v)) for k, v in self.products_by_color.items()]),
            'brands': {}
        }
        
        # Count by brands
        brand_count = defaultdict(int)
        for product in self.all_products:
            brand = product.get('brand', 'Unknown')
            brand_count[brand] += 1
        stats['brands'] = dict(brand_count)
        
        return stats
    
    def create_outfit_combination(self, style_type="casual", color_preference=None, budget_max=None):
        """Create a complete outfit combination"""
        outfit = {}
        
        # Define outfit components for different styles
        if style_type == "casual":
            required_items = ['top', 'bottom', 'accessories']
        elif style_type == "formal":
            required_items = ['dress', 'accessories'] # or top + bottom
        elif style_type == "party":
            required_items = ['dress', 'accessories'] # or stylish top + bottom
        else:
            required_items = ['top', 'bottom', 'accessories']
        
        # Get tops (including t-shirts, tops, blouses, etc.)
        tops = []
        for type_key in ['top', 't-shirt', 'blouse', 'shirt', 'crop top', 'bodysuit']:
            tops.extend(self.products_by_type.get(type_key, []))
        
        # Get bottoms (jeans, pants, skirts, etc.)
        bottoms = []
        for type_key in ['jeans', 'pants', 'trousers', 'legging', 'shorts']:
            bottoms.extend(self.products_by_type.get(type_key, []))
        
        # Get dresses
        dresses = self.products_by_type.get('dress', [])
        
        # Get accessories (bags, jewelry, etc.)
        accessories = []
        for type_key in ['bag', 'nails', 'jewelry']:
            accessories.extend(self.products_by_type.get(type_key, []))
        
        # Apply color filter if specified
        if color_preference:
            color_pref_lower = color_preference.lower()
            tops = [item for item in tops if color_pref_lower in item.get('base_colour', '').lower()]
            bottoms = [item for item in bottoms if color_pref_lower in item.get('base_colour', '').lower()]
            dresses = [item for item in dresses if color_pref_lower in item.get('base_colour', '').lower()]
        
        # Create outfit based on style
        if style_type == "formal" or style_type == "party":
            if dresses:
                outfit['dress'] = random.choice(dresses)
            else:
                # Fallback to top + bottom
                if tops:
                    outfit['top'] = random.choice(tops)
                if bottoms:
                    outfit['bottom'] = random.choice(bottoms)
        else:
            # Casual outfit
            if tops:
                outfit['top'] = random.choice(tops)
            if bottoms:
                outfit['bottom'] = random.choice(bottoms)
        
        # Add accessories
        if accessories:
            outfit['accessory'] = random.choice(accessories)
        
        # Calculate total price and check budget
        total_price = sum(item.get('price', 0) for item in outfit.values())
        if budget_max and total_price > budget_max:
            return self._create_budget_outfit(budget_max, style_type, color_preference)
        
        outfit['total_price'] = total_price
        return outfit
    
    def _create_budget_outfit(self, budget_max, style_type, color_preference):
        """Create an outfit within budget constraints"""
        # Get affordable items
        affordable_items = [item for item in self.all_products if item.get('price', 0) <= budget_max]
        
        outfit = {}
        remaining_budget = budget_max
        
        # Prioritize essential items
        essential_types = ['dress'] if style_type in ['formal', 'party'] else ['top', 'jeans']
        
        for item_type in essential_types:
            suitable_items = [item for item in affordable_items 
                            if item.get('product_type', '').lower() == item_type 
                            and item.get('price', 0) <= remaining_budget]
            
            if suitable_items:
                if color_preference:
                    color_filtered = [item for item in suitable_items 
                                    if color_preference.lower() in item.get('base_colour', '').lower()]
                    if color_filtered:
                        suitable_items = color_filtered
                
                chosen_item = random.choice(suitable_items)
                outfit[item_type] = chosen_item
                remaining_budget -= chosen_item.get('price', 0)
        
        outfit['total_price'] = budget_max - remaining_budget
        return outfit
    
    def recommend_outfit(self, gender=None, occasion=None, dominant_color=None):
        """Provide outfit recommendations based on preferences"""
        recommendations = []
        
        # Filter products based on gender
        gender_filtered = self.all_products
        if gender:
            gender_filtered = [product for product in self.all_products if gender.lower() in product.get('gender', '').lower()]
        
        # Further filter based on occasion
        occasion_filtered = gender_filtered
        if occasion:
            # For simplicity, map occasion to general style types
            occasion_map = {
                'casual': ['jeans', 't-shirt', 'top'],
                'formal': ['dress', 'blouse'],
                'sport': ['sports', 'activewear'],
                'party': ['party', 'dress', 'glamorous']
            }

            if occasion in occasion_map:
                types = occasion_map[occasion]
                occasion_filtered = [product for product in gender_filtered if any(re.search(t, product.get('product_type', '').lower()) for t in types)]

        # Further refine by dominant color if specified
        color_filtered = occasion_filtered
        if dominant_color:
            color_filtered = [product for product in occasion_filtered if dominant_color.lower() in product.get('base_colour', '').lower()]

        # Select recommended products
        recommendations.extend(random.sample(color_filtered, min(5, len(color_filtered))))

        return recommendations

    def color_harmony_score(self, color1, color2):
        """Calculate color harmony score between two colors"""
        # Define color families for better matching
        color_families = {
            'neutral': ['black', 'white', 'grey', 'beige', 'brown', 'camel', 'chocolate'],
            'warm': ['red', 'orange', 'yellow', 'pink', 'maroon', 'burgundy'],
            'cool': ['blue', 'green', 'purple', 'violet', 'navy'],
            'earth': ['brown', 'tan', 'khaki', 'olive', 'rust']
        }
        
        # Find families for both colors
        color1_family = None
        color2_family = None
        
        for family, colors in color_families.items():
            if any(c in color1.lower() for c in colors):
                color1_family = family
            if any(c in color2.lower() for c in colors):
                color2_family = family
        
        # Calculate harmony score
        if color1_family == color2_family:
            return 0.9  # Same family - high harmony
        elif 'neutral' in [color1_family, color2_family]:
            return 0.8  # Neutral with any color - good harmony
        elif color1_family and color2_family:
            return 0.6  # Different families - moderate harmony
        else:
            return 0.4  # Unknown colors - low harmony

    def style_compatibility_score(self, item1, item2):
        """Calculate style compatibility between two items"""
        # Define style compatibility matrix
        casual_items = ['jeans', 't-shirt', 'top', 'sneakers', 'hoodie']
        formal_items = ['dress', 'blouse', 'suit', 'blazer', 'heels']
        sport_items = ['sports bra', 'legging', 'activewear', 'sneakers']
        
        item1_type = item1.get('product_type', '').lower()
        item2_type = item2.get('product_type', '').lower()
        
        # Check if both items are in the same style category
        if (any(style in item1_type for style in casual_items) and 
            any(style in item2_type for style in casual_items)):
            return 0.9
        elif (any(style in item1_type for style in formal_items) and 
              any(style in item2_type for style in formal_items)):
            return 0.9
        elif (any(style in item1_type for style in sport_items) and 
              any(style in item2_type for style in sport_items)):
            return 0.9
        else:
            return 0.5  # Mixed styles - moderate compatibility

    def smart_outfit_recommendations(self, user_preferences=None, max_recommendations=3):
        """Generate smart outfit recommendations based on various factors"""
        if not user_preferences:
            user_preferences = {}
        
        recommendations = []
        
        # Get user preferences
        preferred_colors = user_preferences.get('colors', [])
        preferred_brands = user_preferences.get('brands', [])
        budget_max = user_preferences.get('budget_max', None)
        occasion = user_preferences.get('occasion', 'casual')
        gender = user_preferences.get('gender', None)
        
        # Generate multiple outfit combinations
        for i in range(max_recommendations * 3):  # Generate more to filter best ones
            outfit = self.create_outfit_combination(
                style_type=occasion,
                color_preference=random.choice(preferred_colors) if preferred_colors else None,
                budget_max=budget_max
            )
            
            if outfit and len(outfit) > 1:  # Valid outfit with multiple items
                # Calculate outfit score
                score = self._calculate_outfit_score(outfit, user_preferences)
                outfit['recommendation_score'] = score
                recommendations.append(outfit)
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        return recommendations[:max_recommendations]
    
    def _calculate_outfit_score(self, outfit, user_preferences):
        """Calculate a score for an outfit based on various factors"""
        score = 0.0
        items = [item for key, item in outfit.items() if key != 'total_price' and key != 'recommendation_score']
        
        if len(items) < 2:
            return 0.0
        
        # Color harmony score
        color_scores = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                color1 = items[i].get('base_colour', '')
                color2 = items[j].get('base_colour', '')
                color_scores.append(self.color_harmony_score(color1, color2))
        
        if color_scores:
            score += sum(color_scores) / len(color_scores) * 0.4
        
        # Style compatibility score
        style_scores = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                style_scores.append(self.style_compatibility_score(items[i], items[j]))
        
        if style_scores:
            score += sum(style_scores) / len(style_scores) * 0.3
        
        # Brand preference score
        preferred_brands = user_preferences.get('brands', [])
        if preferred_brands:
            brand_matches = sum(1 for item in items if item.get('brand') in preferred_brands)
            score += (brand_matches / len(items)) * 0.2
        
        # Price factor (lower prices get higher scores within budget)
        budget_max = user_preferences.get('budget_max', float('inf'))
        total_price = outfit.get('total_price', 0)
        if total_price <= budget_max:
            price_score = max(0, 1 - (total_price / budget_max)) if budget_max > 0 else 0.5
            score += price_score * 0.1
        
        return score
    
    def display_recommendations(self, recommendations):
        """Display outfit recommendations in a formatted way"""
        print("\n" + "="*60)
        print("SMART OUTFIT RECOMMENDATIONS")
        print("="*60)
        
        for i, outfit in enumerate(recommendations, 1):
            print(f"\n--- RECOMMENDATION #{i} (Score: {outfit.get('recommendation_score', 0):.2f}) ---")
            
            for item_type, item in outfit.items():
                if item_type in ['total_price', 'recommendation_score']:
                    continue
                    
                print(f"\n{item_type.upper()}:")
                print(f"  Name: {item.get('product_name', 'N/A')}")
                print(f"  Brand: {item.get('brand', 'N/A')}")
                print(f"  Color: {item.get('base_colour', 'N/A')}")
                print(f"  Price: ${item.get('price', 0)}")
            
            print(f"\nTOTAL PRICE: ${outfit.get('total_price', 0)}")
            print("-" * 40)
        
        print("="*60)
    
    def get_trending_items(self, limit=10):
        """Get trending items based on certain criteria"""
        # For simplicity, we'll consider items with specific keywords as trending
        trending_keywords = ['bodycon', 'crop', 'oversized', 'vintage', 'mesh', 'ruched']
        
        trending_items = []
        for product in self.all_products:
            product_name = product.get('product_name', '').lower()
            if any(keyword in product_name for keyword in trending_keywords):
                trending_items.append(product)
        
        return trending_items[:limit]
    
    def display_trending_items(self, trending_items):
        """Display trending items"""
        print("\n" + "="*50)
        print("TRENDING ITEMS")
        print("="*50)
        
        for item in trending_items:
            print(f"\n{item.get('product_name', 'N/A')}")
            print(f"  Brand: {item.get('brand', 'N/A')}")
            print(f"  Color: {item.get('base_colour', 'N/A')}")
            print(f"  Price: ${item.get('price', 0)}")
            print(f"  Type: {item.get('product_type', 'N/A')}")
        
        print("="*50)

    def display_outfit(self, outfit: Dict[str, Any]):
        """Display outfit details in a formatted way"""
        print("\n" + "="*50)
        print("OUTFIT COMBINATION")
        print("="*50)
        
        for item_type, item in outfit.items():
            if item_type == 'total_price':
                continue
                
            print(f"\n{item_type.upper()}:")
            print(f"  Name: {item.get('product_name', 'N/A')}")
            print(f"  Brand: {item.get('brand', 'N/A')}")
            print(f"  Color: {item.get('base_colour', 'N/A')}")
            print(f"  Price: ${item.get('price', 0)}")
            print(f"  Image: {item.get('image_url', 'N/A')}")
        
        print(f"\nTOTAL PRICE: ${outfit.get('total_price', 0)}")
        print("="*50)
    
    def get_products_by_filter(self, category=None, product_type=None, color=None, brand=None, max_price=None):
        """Get products based on various filters"""
        filtered_products = self.all_products
        
        if category:
            filtered_products = [p for p in filtered_products 
                               if category.lower() in p.get('master_category', '').lower()]
        
        if product_type:
            filtered_products = [p for p in filtered_products 
                               if product_type.lower() in p.get('product_type', '').lower()]
        
        if color:
            filtered_products = [p for p in filtered_products 
                               if color.lower() in p.get('base_colour', '').lower()]
        
        if brand:
            filtered_products = [p for p in filtered_products 
                               if brand.lower() in p.get('brand', '').lower()]
        
        if max_price:
            filtered_products = [p for p in filtered_products 
                               if p.get('price', 0) <= max_price]
        
        return filtered_products
    
    def save_combined_data(self, output_file: str):
        """Save combined data to a new JSON file"""
        combined_data = {
            'total_products': len(self.all_products),
            'products': self.all_products,
            'stats': self.get_stats()
        }
        
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(combined_data, file, indent=2, ensure_ascii=False)
        
        print(f"Combined data saved to {output_file}")

# Example usage
if __name__ == "__main__":
    # Initialize the combiner
    combiner = OutfitCombiner()
    
    # Load data from both files
    file_paths = [
        "3 combine products.json",
        "savana outfit.json"
    ]
    
    combiner.load_data(file_paths)
    
    # Display statistics
    stats = combiner.get_stats()
    print("\n=== DATASET STATISTICS ===")
    print(f"Total Products: {stats['total_products']}")
    print(f"Categories: {list(stats['categories'].keys())}")
    print(f"Brands: {list(stats['brands'].keys())}")
    print(f"Available Colors: {list(stats['colors'].keys())[:10]}...")  # Show first 10 colors
    
    # Create sample outfit combinations
    print("\n=== SAMPLE OUTFIT COMBINATIONS ===")
    
    # Casual outfit
    casual_outfit = combiner.create_outfit_combination("casual")
    combiner.display_outfit(casual_outfit)
    
    # Formal outfit in black
    formal_outfit = combiner.create_outfit_combination("formal", color_preference="black")
    combiner.display_outfit(formal_outfit)
    
    # Budget outfit under $100
    budget_outfit = combiner.create_outfit_combination("casual", budget_max=100)
    combiner.display_outfit(budget_outfit)
    
    # Save combined data
    combiner.save_combined_data("combined_outfits.json")
    
    # RECOMMENDATION SYSTEM EXAMPLES
    print("\n=== SMART OUTFIT RECOMMENDATIONS ===")
    
    # Example user preferences
    user_preferences = {
        'colors': ['black', 'white'],
        'brands': ['Littlebox India'],
        'budget_max': 2000,
        'occasion': 'formal',
        'gender': 'women'
    }
    
    smart_recommendations = combiner.smart_outfit_recommendations(user_preferences, max_recommendations=3)
    combiner.display_recommendations(smart_recommendations)
    
    # Basic recommendations
    print("\n=== BASIC RECOMMENDATIONS ===")
    basic_recommendations = combiner.recommend_outfit(gender="women", occasion="casual", dominant_color="black")
    
    print(f"Found {len(basic_recommendations)} recommended items:")
    for i, item in enumerate(basic_recommendations[:3], 1):
        print(f"\n{i}. {item.get('product_name', 'N/A')}")
        print(f"   Brand: {item.get('brand', 'N/A')}")
        print(f"   Color: {item.get('base_colour', 'N/A')}")
        print(f"   Price: ${item.get('price', 0)}")
    
    # Trending items
    print("\n=== TRENDING ITEMS ===")
    trending_items = combiner.get_trending_items(limit=5)
    combiner.display_trending_items(trending_items)
    
    # Example filtering
    print("\n=== FILTERING EXAMPLES ===")
    black_dresses = combiner.get_products_by_filter(product_type="dress", color="black")
    print(f"Found {len(black_dresses)} black dresses")
    
    savana_products = combiner.get_products_by_filter(brand="Savana")
    print(f"Found {len(savana_products)} Savana products")
