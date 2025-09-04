import json
import os
from typing import Dict, List, Any

def load_color_data():
    """
    Load color data from the JSON files in the datasets directory.
    Returns a dictionary with color mappings and seasonal color palettes.
    """
    # Define the paths to the color data files
    color_1_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'datasets', 'color 1.json')
    color_2_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'datasets', 'color 2.txt')
    
    # Initialize the color data dictionary
    color_data = {
        "color_mapping": {},
        "seasonal_palettes": {},
        "monk_hex_codes": {}
    }
    
    # Load color 1.json if it exists
    try:
        if os.path.exists(color_1_path):
            with open(color_1_path, 'r') as f:
                color_1_data = json.load(f)
                
            # Process color suggestions
            if color_1_data and isinstance(color_1_data, list) and len(color_1_data) > 0:
                for suggestion in color_1_data[0].get("color_suggestions", []):
                    skin_tone = suggestion.get("skin_tone", "")
                    suitable_colors = suggestion.get("suitable_colors", "").split(", ")
                    
                    # Add to seasonal palettes
                    if skin_tone:
                        color_data["seasonal_palettes"][skin_tone] = suitable_colors
                        
                        # Add to color mapping
                        for color in suitable_colors:
                            # Simple mapping - could be enhanced with more specific mappings
                            color_data["color_mapping"][color] = color
    except Exception as e:
        print(f"Error loading color 1.json: {e}")
    
    # Load color 2.txt if it exists
    try:
        if os.path.exists(color_2_path):
            with open(color_2_path, 'r') as f:
                color_2_data = json.load(f)
                
            # Process hex codes for different skin tones
            if "colors" in color_2_data:
                for color_entry in color_2_data["colors"]:
                    skin_tone = color_entry.get("suitable_skin_tone", "")
                    hex_codes = color_entry.get("hex_code", [])
                    
                    if skin_tone and hex_codes:
                        # Store hex codes by skin tone
                        color_data["monk_hex_codes"][skin_tone] = hex_codes
    except Exception as e:
        print(f"Error loading color 2.txt: {e}")
    
    return color_data

def get_color_mapping():
    """
    Get a comprehensive color mapping dictionary with extensive color knowledge.
    """
    # Comprehensive color mapping based on color theory and fashion
    color_mapping = {
        # REDS - Various shades and tones
        "Red": "Red",
        "Crimson": "Red",
        "Scarlet": "Red",
        "Cardinal": "Red",
        "Cherry": "Red",
        "Ruby": "Red",
        "Burgundy": "Burgundy",
        "Wine": "Burgundy",
        "Maroon": "Maroon",
        "Brick Red": "Red",
        "Fire Engine Red": "Red",
        "Rose": "Pink",
        "Coral Red": "Coral",
        "Tomato": "Red",
        "Strawberry": "Red",
        "Poppy": "Red",
        "Vermillion": "Red",
        "Indian Red": "Red",
        "Chestnut Red": "Red",
        "Mahogany": "Red",
        "Cool Red": "Red",
        "True Red": "Red",
        "Cool Ruby": "Red",
        "Deep Claret": "Burgundy",
        "Garnet": "Red",
        "Blood Red": "Red",
        "Barn Red": "Red",
        "Candy Apple Red": "Red",
        "Carmine": "Red",
        "Cerise": "Pink",
        "Cinnabar": "Red",
        
        # PINKS - From soft to vibrant
        "Pink": "Pink",
        "Rose Pink": "Pink",
        "Blush": "Pink",
        "Baby Pink": "Pink",
        "Soft Pink": "Pink",
        "Hot Pink": "Pink",
        "Fuchsia Pink": "Magenta",
        "Magenta": "Magenta",
        "Deep Pink": "Pink",
        "Dusty Rose": "Pink",
        "Mauve": "Pink",
        "Salmon": "Pink",
        "Coral": "Coral",
        "Peach": "Peach",
        "Apricot": "Peach",
        "Shell Pink": "Pink",
        "Cotton Candy": "Pink",
        "Bubblegum": "Pink",
        "Flamingo": "Pink",
        "Tickle Me Pink": "Pink",
        "Cool Pink": "Pink",
        "Ice Pink": "Pink",
        "Soft Fuchsia": "Magenta",
        "Bright Coral": "Coral",
        "Warm Coral": "Coral",
        "Rose Gold": "Pink",
        "Millennial Pink": "Pink",
        "Dusty Pink": "Pink",
        "Powder Pink": "Pink",
        "Carnation": "Pink",
        "Amaranth": "Pink",
        
        # ORANGES - Warm and energetic
        "Orange": "Orange",
        "Tangerine": "Orange",
        "Peach": "Peach",
        "Coral": "Coral",
        "Burnt Orange": "Orange",
        "Rust": "Orange",
        "Terracotta": "Orange",
        "Pumpkin": "Orange",
        "Carrot": "Orange",
        "Mandarin": "Orange",
        "Persimmon": "Orange",
        "Papaya": "Orange",
        "Cantaloupe": "Orange",
        "Orange Red": "Orange",
        "Dark Orange": "Orange",
        "Sunset Orange": "Orange",
        "Amber": "Orange",
        "Honey": "Orange",
        "Marigold": "Orange",
        "Tiger Orange": "Orange",
        "Safety Orange": "Orange",
        "International Orange": "Orange",
        "Vivid Orange": "Orange",
        "Cadmium Orange": "Orange",
        "Atomic Tangerine": "Orange",
        "Neon Orange": "Orange",
        "Burnt Sienna": "Orange",
        "Raw Sienna": "Orange",
        "Ochre": "Orange",
        
        # YELLOWS - Bright and cheerful
        "Yellow": "Yellow",
        "Lemon": "Yellow",
        "Canary": "Yellow",
        "Golden Yellow": "Yellow",
        "Mustard": "Yellow",
        "Butter": "Yellow",
        "Cream": "Cream",
        "Ivory": "Cream",
        "Vanilla": "Cream",
        "Blonde": "Yellow",
        "Champagne": "Yellow",
        "Sunshine": "Yellow",
        "Banana": "Yellow",
        "Daffodil": "Yellow",
        "Goldenrod": "Yellow",
        "Saffron": "Yellow",
        "Clear Yellow": "Yellow",
        "Acid Yellow": "Yellow",
        "Neon Yellow": "Yellow",
        "Electric Yellow": "Yellow",
        "Bright Yellow": "Yellow",
        "School Bus Yellow": "Yellow",
        "Taxi Cab Yellow": "Yellow",
        "Sunflower": "Yellow",
        "Corn": "Yellow",
        "Wheat": "Yellow",
        "Straw": "Yellow",
        "Khaki": "Khaki",
        "Beige": "Beige",
        "Sand": "Beige",
        
        # GREENS - Natural and fresh
        "Green": "Green",
        "Forest Green": "Green",
        "Emerald": "Green",
        "Jade": "Green",
        "Mint": "Mint Green",
        "Lime": "Green",
        "Sage": "Green",
        "Olive": "Olive",
        "Moss": "Green",
        "Pine": "Green",
        "Hunter Green": "Green",
        "Kelly Green": "Green",
        "Spring Green": "Green",
        "Seafoam": "Green",
        "Mint Green": "Mint Green",
        "Apple Green": "Green",
        "Chartreuse": "Green",
        "Neon Green": "Green",
        "Electric Green": "Green",
        "Lime Green": "Green",
        "Bright Green": "Green",
        "Grass Green": "Green",
        "Leaf Green": "Green",
        "Jungle Green": "Green",
        "Bottle Green": "Green",
        "Olive Green": "Olive",
        "Dark Olive Green": "Olive",
        "Sage Green": "Green",
        "Soft Green": "Green",
        "Moss Green": "Green",
        "Avocado": "Green",
        "Pistachio": "Green",
        "Celadon": "Green",
        "Malachite": "Green",
        "Viridian": "Green",
        "Verdigris": "Green",
        "Parakeet": "Green",
        "Shamrock": "Green",
        "Clover": "Green",
        "Fern": "Green",
        "Oakmoss": "Green",
        
        # BLUES - Cool and calming
        "Blue": "Blue",
        "Navy": "Navy Blue",
        "Royal Blue": "Blue",
        "Sky Blue": "Blue",
        "Baby Blue": "Blue",
        "Powder Blue": "Light Blue",
        "Steel Blue": "Blue",
        "Denim": "Blue",
        "Periwinkle": "Blue",
        "Cornflower": "Blue",
        "Sapphire": "Blue",
        "Cobalt": "Blue",
        "Indigo": "Purple",
        "Midnight Blue": "Navy Blue",
        "Ocean Blue": "Blue",
        "Turquoise": "Turquoise Blue",
        "Teal": "Teal",
        "Aqua": "Aqua",
        "Cyan": "Cyan",
        "Robin Egg Blue": "Blue",
        "Alice Blue": "Blue",
        "Powder Blue": "Blue",
        "Light Blue": "Light Blue",
        "Ice Blue": "Blue",
        "Frost Blue": "Blue",
        "Clear Blue": "Blue",
        "Rich Blue": "Blue",
        "Deep Blue": "Blue",
        "Electric Blue": "Blue",
        "Neon Blue": "Blue",
        "Bright Blue": "Blue",
        "True Blue": "Blue",
        "Cerulean": "Blue",
        "Azure": "Blue",
        "Slate Blue": "Blue",
        "Steel Blue": "Blue",
        "Cadet Blue": "Blue",
        "Peacock Blue": "Blue",
        "Prussian Blue": "Blue",
        "Egyptian Blue": "Blue",
        "Ultramarine": "Blue",
        "Lapis Lazuli": "Blue",
        "Navy Blue": "Navy Blue",
        "Bright Navy": "Navy Blue",
        "Cobalt Blue": "Blue",
        "Warm Turquoise": "Turquoise Blue",
        "Deep Teal": "Teal",
        "Petrol Blue": "Blue",
        
        # PURPLES - Regal and mysterious
        "Purple": "Purple",
        "Violet": "Purple",
        "Lavender": "Purple",
        "Lilac": "Purple",
        "Plum": "Purple",
        "Eggplant": "Purple",
        "Amethyst": "Purple",
        "Orchid": "Purple",
        "Magenta": "Magenta",
        "Fuchsia": "Magenta",
        "Royal Purple": "Purple",
        "Deep Purple": "Purple",
        "Dark Purple": "Purple",
        "Light Purple": "Purple",
        "Soft Purple": "Purple",
        "Bright Purple": "Purple",
        "Electric Purple": "Purple",
        "Neon Purple": "Purple",
        "Grape": "Purple",
        "Wine Purple": "Purple",
        "Burgundy Purple": "Purple",
        "Mauve": "Purple",
        "Periwinkle": "Purple",
        "Wisteria": "Purple",
        "Heliotrope": "Purple",
        "Medium Violet Red": "Magenta",
        "Dark Orchid": "Purple",
        "Soft Plum": "Purple",
        "Byzantium": "Purple",
        "Thistle": "Purple",
        "Mulberry": "Purple",
        "Aubergine": "Purple",
        "Clematis": "Purple",
        
        # NEUTRALS - Timeless and versatile
        "White": "White",
        "Black": "Black",
        "Gray": "Grey",
        "Grey": "Grey",
        "Silver": "Silver",
        "Charcoal": "Grey",
        "Ash": "Grey",
        "Slate": "Grey",
        "Stone": "Grey",
        "Pewter": "Grey",
        "Platinum": "Silver",
        "Smoke": "Grey",
        "Fog": "Grey",
        "Mist": "Grey",
        "Cloud": "Grey",
        "Pearl": "White",
        "Ivory": "Cream",
        "Cream": "Cream",
        "Bone": "Cream",
        "Eggshell": "Cream",
        "Vanilla": "Cream",
        "Linen": "Cream",
        "Champagne": "Cream",
        "Beige": "Beige",
        "Tan": "Tan",
        "Taupe": "Taupe",
        "Mushroom": "Taupe",
        "Oatmeal": "Beige",
        "Sand": "Beige",
        "Camel": "Tan",
        "Nude": "Nude",
        "Blush Nude": "Nude",
        "True White": "White",
        "Crisp White": "White",
        "Pure White": "White",
        "Snow White": "White",
        "Off White": "White",
        "Antique White": "White",
        "Light Grey Marle": "Grey",
        "Warm Beige": "Beige",
        
        # BROWNS - Earthy and warm
        "Brown": "Brown",
        "Chocolate": "Brown",
        "Coffee": "Brown",
        "Espresso": "Brown",
        "Mocha": "Brown",
        "Cocoa": "Brown",
        "Chestnut": "Brown",
        "Mahogany": "Brown",
        "Walnut": "Brown",
        "Oak": "Brown",
        "Pine": "Brown",
        "Cedar": "Brown",
        "Teak": "Brown",
        "Hickory": "Brown",
        "Maple": "Brown",
        "Cherry Wood": "Brown",
        "Saddle Brown": "Brown",
        "Leather": "Brown",
        "Cognac": "Brown",
        "Brandy": "Brown",
        "Whiskey": "Brown",
        "Bourbon": "Brown",
        "Caramel": "Brown",
        "Butterscotch": "Brown",
        "Toffee": "Brown",
        "Fudge": "Brown",
        "Gingerbread": "Brown",
        "Cinnamon": "Brown",
        "Nutmeg": "Brown",
        "Clove": "Brown",
        "Paprika": "Brown",
        "Sienna": "Brown",
        "Umber": "Brown",
        "Sepia": "Brown",
        "Raw Umber": "Brown",
        "Burnt Umber": "Brown",
        "Van Dyke Brown": "Brown",
        
        # TEALS AND AQUAS - Between blue and green
        "Teal": "Teal",
        "Aqua": "Aqua",
        "Aquamarine": "Aqua",
        "Turquoise": "Turquoise Blue",
        "Cyan": "Cyan",
        "Seafoam Green": "Green",
        "Mint Aqua": "Aqua",
        "Jade Green": "Green",
        "Emerald Teal": "Teal",
        "Ocean Teal": "Teal",
        "Deep Aqua": "Aqua",
        "Light Aqua": "Aqua",
        "Tropical Teal": "Teal",
        "Caribbean Blue": "Blue",
        "Lagoon": "Teal",
        "Sea Green": "Green",
        "Light Sea Green": "Green",
        "Medium Sea Green": "Green",
        "Dark Sea Green": "Green",
        
        # METALLICS - Luxurious accents
        "Gold": "Gold",
        "Silver": "Silver",
        "Bronze": "Bronze",
        "Copper": "Copper",
        "Brass": "Gold",
        "Pewter": "Silver",
        "Platinum": "Silver",
        "Rose Gold": "Rose Gold",
        "White Gold": "Silver",
        "Yellow Gold": "Gold",
        "Antique Gold": "Gold",
        "Brushed Gold": "Gold",
        "Matte Gold": "Gold",
        "Shiny Gold": "Gold",
        "Light Gold": "Gold",
        "Deep Gold": "Gold",
        "Metallic Silver": "Silver",
        "Chrome": "Silver",
        "Gunmetal": "Grey",
        "Steel": "Silver",
        "Iron": "Grey",
        "Titanium": "Silver",
        "Mercury": "Silver",
        
        # PASTELS - Soft and delicate
        "Pastel Pink": "Pink",
        "Pastel Blue": "Blue",
        "Pastel Green": "Green",
        "Pastel Yellow": "Yellow",
        "Pastel Purple": "Purple",
        "Pastel Orange": "Orange",
        "Baby Pink": "Pink",
        "Baby Blue": "Blue",
        "Mint Cream": "Mint Green",
        "Lavender Blush": "Pink",
        "Honeydew": "Green",
        "Azure Mist": "Blue",
        "Lemon Chiffon": "Yellow",
        "Peach Puff": "Peach",
        "Misty Rose": "Pink",
        "Alice Blue": "Blue",
        "Ghost White": "White",
        "Seashell": "Pink",
        "Old Lace": "Cream",
        "Floral White": "White",
        "Cornsilk": "Yellow",
        "Blanched Almond": "Cream",
        "Bisque": "Cream",
        "Papaya Whip": "Cream",
        "Moccasin": "Tan",
        "Navajo White": "Cream",
        "Peach Puff": "Peach",
        "Misty Rose": "Pink",
        "Lavender Blush": "Pink",
        "Linen": "Cream",
        "Antique White": "White",
        "Papaya Whip": "Cream",
        "Blanched Almond": "Cream",
        "Bisque": "Cream",
        "Peach Puff": "Peach",
        "Navajo White": "Cream",
        "Moccasin": "Tan",
        "Cornsilk": "Yellow",
        "Ivory": "Cream",
        "Lemon Chiffon": "Yellow",
        "Seashell": "Pink",
        "Honeydew": "Green",
        "Mint Cream": "Mint Green",
        "Azure": "Blue",
        "Alice Blue": "Blue",
        "Ghost White": "White",
        "White Smoke": "White",
        "Seashell": "Pink",
        "Beige": "Beige",
        "Old Lace": "Cream",
        "Floral White": "White",
        "Ivory": "Cream",
        "Antique White": "White",
        "Linen": "Cream",
        "Lavender Blush": "Pink",
        "Misty Rose": "Pink"
    }
    
    # Try to load additional mappings from the color data files
    try:
        color_data = load_color_data()
        if "color_mapping" in color_data and color_data["color_mapping"]:
            # Merge the loaded color mapping with the base mapping
            color_mapping.update(color_data["color_mapping"])
    except Exception as e:
        print(f"Error getting color mapping: {e}")
    
    return color_mapping

def get_seasonal_palettes():
    """
    Get seasonal color palettes from the color data files.
    """
    try:
        color_data = load_color_data()
        return color_data.get("seasonal_palettes", {})
    except Exception as e:
        print(f"Error getting seasonal palettes: {e}")
        return {}

def get_monk_hex_codes():
    """
    Get Monk skin tone hex codes from the color data files.
    """
    try:
        color_data = load_color_data()
        return color_data.get("monk_hex_codes", {})
    except Exception as e:
        print(f"Error getting Monk hex codes: {e}")
        return {}

# Example of how to use these functions:
if __name__ == "__main__":
    # Load all color data
    all_color_data = load_color_data()
    print("Color data loaded successfully.")
    
    # Get color mapping
    mapping = get_color_mapping()
    print(f"Color mapping contains {len(mapping)} entries.")
    
    # Get seasonal palettes
    palettes = get_seasonal_palettes()
    print(f"Loaded {len(palettes)} seasonal palettes.")
    
    # Get Monk hex codes
    hex_codes = get_monk_hex_codes()
    print(f"Loaded hex codes for {len(hex_codes)} skin tones.") 