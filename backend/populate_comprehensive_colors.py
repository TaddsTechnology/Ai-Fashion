#!/usr/bin/env python3
"""
Script to populate the comprehensive_colors table with intelligent analysis
of color compatibility with Monk skin tones.
"""

import pandas as pd
import numpy as np
from webcolors import hex_to_rgb
import os
import sys
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add the prods_fastapi directory to the path
sys.path.append(str(Path(__file__).parent / 'prods_fastapi'))

from database import ComprehensiveColors, Base, DATABASE_URL

def rgb_to_hsv(r, g, b):
    """Convert RGB to HSV color space"""
    r, g, b = r/255.0, g/255.0, b/255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val
    
    # Hue
    if diff == 0:
        h = 0
    elif max_val == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_val == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    # Saturation
    s = 0 if max_val == 0 else diff / max_val
    
    # Value
    v = max_val
    
    return h, s, v

def analyze_color_properties(hex_code):
    """Analyze color properties for compatibility with skin tones"""
    try:
        # Remove # if present
        hex_code = hex_code.replace('#', '')
        
        # Convert to RGB
        r, g, b = hex_to_rgb(f"#{hex_code}")
        
        # Convert to HSV for better analysis
        h, s, v = rgb_to_hsv(r, g, b)
        
        # Calculate brightness
        brightness = np.mean([r, g, b])
        
        # Determine color family
        color_family = determine_color_family(h, s, v)
        
        # Determine brightness level
        if brightness >= 200:
            brightness_level = "light"
        elif brightness >= 100:
            brightness_level = "medium"
        else:
            brightness_level = "dark"
        
        # Determine undertone
        undertone = determine_undertone(h, s, v, r, g, b)
        
        return {
            'color_family': color_family,
            'brightness_level': brightness_level,
            'undertone': undertone,
            'hue': h,
            'saturation': s,
            'value': v,
            'rgb': (r, g, b)
        }
    except Exception as e:
        print(f"Error analyzing color {hex_code}: {e}")
        return {
            'color_family': 'unknown',
            'brightness_level': 'medium',
            'undertone': 'neutral',
            'hue': 0,
            'saturation': 0,
            'value': 0.5,
            'rgb': (128, 128, 128)
        }

def determine_color_family(h, s, v):
    """Determine color family based on hue"""
    if s < 0.1:  # Very low saturation = neutral
        return "neutral"
    elif 0 <= h < 15 or 345 <= h <= 360:
        return "red"
    elif 15 <= h < 45:
        return "orange"
    elif 45 <= h < 75:
        return "yellow"
    elif 75 <= h < 150:
        return "green"
    elif 150 <= h < 210:
        return "cyan"
    elif 210 <= h < 270:
        return "blue"
    elif 270 <= h < 330:
        return "purple"
    elif 330 <= h < 345:
        return "pink"
    else:
        return "neutral"

def determine_undertone(h, s, v, r, g, b):
    """Determine color undertone (cool, warm, or neutral)"""
    # For very low saturation colors, check RGB ratios
    if s < 0.15:
        if r > g and r > b:
            return "warm"
        elif b > r and b > g:
            return "cool"
        else:
            return "neutral"
    
    # For saturated colors, use hue
    if 30 <= h <= 150:  # Yellows and greens tend to be warm
        return "warm"
    elif 150 <= h <= 270:  # Cyans and blues tend to be cool
        return "cool"
    elif 270 <= h <= 330:  # Purples can be cool
        return "cool"
    elif 330 <= h <= 30:   # Reds and oranges can be warm
        return "warm"
    else:
        return "neutral"

def determine_monk_compatibility(color_props):
    """Determine which Monk skin tones this color is compatible with"""
    compatible_monks = []
    
    brightness = color_props['brightness_level']
    undertone = color_props['undertone']
    color_family = color_props['color_family']
    saturation = color_props['saturation']
    value = color_props['value']
    
    # Light skin tones (Monk 1-3) - prefer softer, lighter colors
    if brightness in ['light', 'medium'] and (saturation < 0.8 or value > 0.6):
        if color_family in ['blue', 'purple', 'pink', 'neutral', 'green'] and undertone in ['cool', 'neutral']:
            compatible_monks.extend(['Monk01', 'Monk02', 'Monk03'])
        elif color_family in ['yellow', 'orange', 'red'] and undertone == 'warm' and saturation < 0.7:
            compatible_monks.extend(['Monk01', 'Monk02', 'Monk03'])
    
    # Light-medium skin tones (Monk 3-5) - can handle more variety
    if brightness in ['light', 'medium']:
        if color_family in ['blue', 'green', 'purple', 'neutral']:
            compatible_monks.extend(['Monk03', 'Monk04', 'Monk05'])
        elif color_family in ['red', 'orange', 'yellow'] and undertone == 'warm':
            compatible_monks.extend(['Monk03', 'Monk04', 'Monk05'])
        elif color_family == 'pink' and undertone in ['cool', 'neutral']:
            compatible_monks.extend(['Monk03', 'Monk04', 'Monk05'])
    
    # Medium skin tones (Monk 4-7) - most versatile
    if brightness in ['medium', 'dark'] or saturation > 0.3:
        compatible_monks.extend(['Monk04', 'Monk05', 'Monk06', 'Monk07'])
    
    # Medium-dark skin tones (Monk 6-8) - can handle richer colors
    if brightness in ['medium', 'dark'] and (saturation > 0.4 or value < 0.8):
        compatible_monks.extend(['Monk06', 'Monk07', 'Monk08'])
    
    # Dark skin tones (Monk 8-10) - prefer rich, saturated colors
    if brightness in ['medium', 'dark'] and saturation > 0.3:
        if color_family in ['red', 'orange', 'yellow', 'green', 'blue', 'purple']:
            compatible_monks.extend(['Monk08', 'Monk09', 'Monk10'])
        elif color_family == 'neutral' and value < 0.9:  # Not too light neutrals
            compatible_monks.extend(['Monk08', 'Monk09', 'Monk10'])
    
    # Remove duplicates and return
    return list(set(compatible_monks))

def determine_seasonal_compatibility(color_props):
    """Determine which seasonal types this color is compatible with"""
    compatible_seasons = []
    
    brightness = color_props['brightness_level']
    undertone = color_props['undertone']
    color_family = color_props['color_family']
    saturation = color_props['saturation']
    value = color_props['value']
    
    # Light seasons prefer lighter, clearer colors
    if brightness == 'light' and saturation > 0.3:
        if undertone == 'cool':
            compatible_seasons.extend(['Light Summer', 'Cool Summer'])
        elif undertone == 'warm':
            compatible_seasons.extend(['Light Spring', 'Warm Spring'])
        else:
            compatible_seasons.extend(['Light Spring', 'Light Summer'])
    
    # Clear seasons prefer bright, saturated colors
    if saturation > 0.6 and value > 0.4:
        if undertone == 'cool':
            compatible_seasons.extend(['Clear Winter', 'Cool Winter'])
        elif undertone == 'warm':
            compatible_seasons.extend(['Clear Spring', 'Warm Spring'])
        else:
            compatible_seasons.extend(['Clear Winter', 'Clear Spring'])
    
    # Soft seasons prefer muted colors
    if saturation < 0.5 and brightness in ['light', 'medium']:
        if undertone == 'cool':
            compatible_seasons.extend(['Soft Summer', 'Cool Summer'])
        elif undertone == 'warm':
            compatible_seasons.extend(['Soft Autumn', 'Warm Autumn'])
        else:
            compatible_seasons.extend(['Soft Summer', 'Soft Autumn'])
    
    # Deep seasons prefer dark, rich colors
    if brightness in ['medium', 'dark'] and (saturation > 0.4 or value < 0.6):
        if undertone == 'cool':
            compatible_seasons.extend(['Deep Winter', 'Cool Winter'])
        elif undertone == 'warm':
            compatible_seasons.extend(['Deep Autumn', 'Warm Autumn'])
        else:
            compatible_seasons.extend(['Deep Winter', 'Deep Autumn'])
    
    # Warm seasons
    if undertone == 'warm' and color_family in ['red', 'orange', 'yellow', 'green']:
        compatible_seasons.extend(['Warm Spring', 'Warm Autumn'])
    
    # Cool seasons
    if undertone == 'cool' and color_family in ['blue', 'purple', 'pink', 'green']:
        compatible_seasons.extend(['Cool Winter', 'Cool Summer'])
    
    return list(set(compatible_seasons))

def generate_color_name(hex_code, color_props):
    """Generate a descriptive color name"""
    family = color_props['color_family']
    brightness = color_props['brightness_level']
    undertone = color_props['undertone']
    
    # Base color names
    base_names = {
        'red': 'Red',
        'orange': 'Orange', 
        'yellow': 'Yellow',
        'green': 'Green',
        'cyan': 'Cyan',
        'blue': 'Blue',
        'purple': 'Purple',
        'pink': 'Pink',
        'neutral': 'Neutral'
    }
    
    # Brightness modifiers
    brightness_mods = {
        'light': 'Light',
        'medium': '',
        'dark': 'Deep'
    }
    
    # Undertone modifiers
    undertone_mods = {
        'cool': 'Cool',
        'warm': 'Warm',
        'neutral': ''
    }
    
    # Build name
    parts = []
    if brightness_mods[brightness]:
        parts.append(brightness_mods[brightness])
    if undertone_mods[undertone]:
        parts.append(undertone_mods[undertone])
    parts.append(base_names.get(family, 'Color'))
    
    return ' '.join(parts)

def populate_comprehensive_colors():
    """Main function to populate the comprehensive colors table"""
    
    # Create database engine and session
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(ComprehensiveColors).count()
        if existing_count > 0:
            print(f"Comprehensive colors already exist ({existing_count} records)")
            response = input("Do you want to replace them? (y/N): ")
            if response.lower() != 'y':
                return
            else:
                # Delete existing records
                db.query(ComprehensiveColors).delete()
                db.commit()
                print("Existing records deleted")
        
        # Load colors from CSV
        csv_path = Path(__file__).parent / 'processed_data' / 'color_hex_codes.csv'
        if not csv_path.exists():
            print(f"Color CSV file not found at {csv_path}")
            return
        
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} colors from CSV")
        
        # Process each color
        colors_processed = 0
        colors_added = 0
        
        for _, row in df.iterrows():
            try:
                hex_code = row['hex_code'].strip()
                if not hex_code.startswith('#'):
                    hex_code = f"#{hex_code}"
                
                # Analyze color properties
                color_props = analyze_color_properties(hex_code)
                
                # Determine compatibility
                monk_tones = determine_monk_compatibility(color_props)
                seasonal_types = determine_seasonal_compatibility(color_props)
                
                # Generate color name
                color_name = generate_color_name(hex_code, color_props)
                
                # Create database record
                color_record = ComprehensiveColors(
                    hex_code=hex_code,
                    color_name=color_name,
                    monk_tones=monk_tones,
                    seasonal_types=seasonal_types,
                    color_family=color_props['color_family'],
                    brightness_level=color_props['brightness_level'],
                    undertone=color_props['undertone'],
                    data_source='csv_analysis'
                )
                
                db.add(color_record)
                colors_added += 1
                
                colors_processed += 1
                if colors_processed % 50 == 0:
                    print(f"Processed {colors_processed} colors...")
                    
            except Exception as e:
                print(f"Error processing color {row.get('hex_code', 'unknown')}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        print(f"Successfully added {colors_added} comprehensive color records")
        
        # Print some statistics
        stats_query = db.query(ComprehensiveColors)
        total_colors = stats_query.count()
        
        print(f"\nDatabase Statistics:")
        print(f"Total colors: {total_colors}")
        
        # Count by Monk tone compatibility
        print(f"\nMonk Tone Compatibility:")
        for monk_num in range(1, 11):
            monk_id = f"Monk{monk_num:02d}"
            count = stats_query.filter(ComprehensiveColors.monk_tones.op('?')(monk_id)).count()
            print(f"  {monk_id}: {count} colors")
        
        # Count by color family
        print(f"\nColor Family Distribution:")
        families = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'pink', 'neutral']
        for family in families:
            count = stats_query.filter(ComprehensiveColors.color_family == family).count()
            print(f"  {family.title()}: {count} colors")
            
    except Exception as e:
        db.rollback()
        print(f"Error populating comprehensive colors: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_comprehensive_colors()
