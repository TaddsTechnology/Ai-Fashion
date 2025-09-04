from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from typing import Optional

# Database URL - Use environment variable with external database default
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://fashion_jvy9_user:0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh@dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com/fashion_jvy9"
)

# Create SQLAlchemy engine (force synchronous driver)
if DATABASE_URL.startswith('postgresql+asyncpg://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Database Models
class ColorPalette(Base):
    __tablename__ = "color_palettes"
    
    id = Column(Integer, primary_key=True, index=True)
    skin_tone = Column(String, index=True, nullable=False)
    flattering_colors = Column(JSON, nullable=False)  # Array of {name, hex} objects
    colors_to_avoid = Column(JSON, nullable=True)    # Array of {name, hex} objects
    description = Column(Text, nullable=True)

class SkinToneMapping(Base):
    __tablename__ = "skin_tone_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    monk_tone = Column(String, index=True, nullable=False)  # e.g., "Monk01", "Monk02"
    seasonal_type = Column(String, nullable=False)          # e.g., "Clear Winter", "Warm Spring"
    hex_code = Column(String, nullable=False)               # Hex color code

class ColorHexData(Base):
    __tablename__ = "color_hex_data"
    
    id = Column(Integer, primary_key=True, index=True)
    seasonal_type = Column(String, index=True, nullable=False)
    hex_codes = Column(JSON, nullable=False)  # Array of hex codes
    data_source = Column(String, nullable=True)  # Source of the data

class ColorSuggestions(Base):
    __tablename__ = "color_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    skin_tone = Column(String, index=True, nullable=False)
    suitable_colors_text = Column(Text, nullable=False)  # Comma-separated color names
    data_source = Column(String, nullable=True)

class ComprehensiveColors(Base):
    __tablename__ = "comprehensive_colors"
    
    id = Column(Integer, primary_key=True, index=True)
    hex_code = Column(String, index=True, nullable=False)  # Hex color code like #FFFFFF
    color_name = Column(String, nullable=True)  # Human-readable color name
    monk_tones = Column(JSON, nullable=True)  # Array of compatible Monk tones ["Monk01", "Monk02"]
    seasonal_types = Column(JSON, nullable=True)  # Array of compatible seasonal types
    color_family = Column(String, nullable=True)  # e.g., "blue", "red", "neutral"
    brightness_level = Column(String, nullable=True)  # "light", "medium", "dark"
    undertone = Column(String, nullable=True)  # "cool", "warm", "neutral"
    data_source = Column(String, nullable=True)  # Source of the color data

# Dependency to get database session
def get_database():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create tables
def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

# Function to initialize color palette data
def init_color_palette_data():
    """Initialize color palette data in the database"""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_palettes = db.query(ColorPalette).count()
        if existing_palettes > 0:
            print(f"Color palette data already exists ({existing_palettes} records)")
            return
            
        # Color palette data to insert
        palette_data = [
            {
                "skin_tone": "Clear Winter",
                "flattering_colors": [
                    {"name": "Hot Pink", "hex": "#E3006D"},
                    {"name": "Cobalt Blue", "hex": "#0057B8"},
                    {"name": "True Red", "hex": "#CE0037"},
                    {"name": "Violet", "hex": "#963CBD"},
                    {"name": "Emerald", "hex": "#009775"},
                    {"name": "Ice Pink", "hex": "#F395C7"},
                ],
                "colors_to_avoid": [
                    {"name": "Muted Olive", "hex": "#A3AA83"},
                    {"name": "Dusty Rose", "hex": "#C4A4A7"},
                    {"name": "Terracotta", "hex": "#A6631B"},
                    {"name": "Mustard", "hex": "#B89D18"},
                ],
                "description": "Clear Winter complexions look best in pure, vivid colors with blue undertones. Avoid muted, earthy tones that can make your complexion appear dull."
            },
            {
                "skin_tone": "Cool Winter",
                "flattering_colors": [
                    {"name": "Emerald", "hex": "#009775"},
                    {"name": "Cobalt Blue", "hex": "#0082BA"},
                    {"name": "Cherry", "hex": "#CE0037"},
                    {"name": "Sapphire", "hex": "#0057B8"},
                    {"name": "Fuchsia", "hex": "#C724B1"},
                    {"name": "Cool Ruby", "hex": "#AA0061"},
                ],
                "colors_to_avoid": [
                    {"name": "Orange", "hex": "#FF8200"},
                    {"name": "Warm Gold", "hex": "#F0B323"},
                    {"name": "Peach", "hex": "#FDAA63"},
                    {"name": "Olive", "hex": "#A09958"},
                ],
                "description": "Cool Winter types look best in cool, clear colors with blue undertones. Avoid warm, earthy tones that clash with your cool complexion."
            },
            {
                "skin_tone": "Deep Winter",
                "flattering_colors": [
                    {"name": "Deep Claret", "hex": "#890C58"},
                    {"name": "Forest Green", "hex": "#00594C"},
                    {"name": "True Red", "hex": "#CE0037"},
                    {"name": "Navy", "hex": "#002D72"},
                    {"name": "Amethyst", "hex": "#84329B"},
                    {"name": "White", "hex": "#FEFEFE"},
                ],
                "colors_to_avoid": [
                    {"name": "Light Pastels", "hex": "#F1EB9C"},
                    {"name": "Peach", "hex": "#FCC89B"},
                    {"name": "Beige", "hex": "#D3BC8D"},
                    {"name": "Camel", "hex": "#CDA077"},
                ],
                "description": "Deep Winter complexions look best in deep, rich colors with cool undertones. Avoid light pastels and warm earth tones that can wash you out."
            },
            {
                "skin_tone": "Clear Spring",
                "flattering_colors": [
                    {"name": "Turquoise", "hex": "#008EAA"},
                    {"name": "Clear Yellow", "hex": "#FFCD00"},
                    {"name": "Bright Coral", "hex": "#FF8D6D"},
                    {"name": "Violet", "hex": "#963CBD"},
                    {"name": "Bright Green", "hex": "#00A499"},
                    {"name": "Watermelon", "hex": "#E40046"},
                ],
                "colors_to_avoid": [
                    {"name": "Dusty Rose", "hex": "#C4A4A7"},
                    {"name": "Mauve", "hex": "#86647A"},
                    {"name": "Taupe", "hex": "#A39382"},
                    {"name": "Muted Teal", "hex": "#507F70"},
                ],
                "description": "Clear Spring complexions look best in clear, bright colors with warm undertones. Avoid muted, dusty colors that can make your complexion appear dull."
            },
            {
                "skin_tone": "Warm Spring",
                "flattering_colors": [
                    {"name": "Warm Beige", "hex": "#FDAA63"},
                    {"name": "Golden Yellow", "hex": "#FFB81C"},
                    {"name": "Apricot", "hex": "#FF8F1C"},
                    {"name": "Coral", "hex": "#FFA38B"},
                    {"name": "Warm Green", "hex": "#74AA50"},
                    {"name": "Turquoise", "hex": "#2DCCD3"},
                ],
                "colors_to_avoid": [
                    {"name": "Black", "hex": "#131413"},
                    {"name": "Navy", "hex": "#003057"},
                    {"name": "Cool Pink", "hex": "#F395C7"},
                    {"name": "Burgundy", "hex": "#890C58"},
                ],
                "description": "Warm Spring types look best in warm, clear colors with golden undertones. Avoid cool, dark colors that can clash with your warm coloring."
            },
            {
                "skin_tone": "Light Spring",
                "flattering_colors": [
                    {"name": "Peach", "hex": "#FCC89B"},
                    {"name": "Mint", "hex": "#A5DFD3"},
                    {"name": "Coral", "hex": "#FF8D6D"},
                    {"name": "Light Yellow", "hex": "#F5E1A4"},
                    {"name": "Aqua", "hex": "#A4DBE8"},
                    {"name": "Soft Pink", "hex": "#FAAA8D"},
                ],
                "colors_to_avoid": [
                    {"name": "Black", "hex": "#131413"},
                    {"name": "Navy", "hex": "#002D72"},
                    {"name": "Burgundy", "hex": "#890C58"},
                    {"name": "Dark Brown", "hex": "#5C462B"},
                ],
                "description": "Light Spring complexions look best in light, warm colors with yellow undertones. Avoid dark, cool colors that can overwhelm your delicate coloring."
            },
            {
                "skin_tone": "Soft Summer",
                "flattering_colors": [
                    {"name": "Slate Blue", "hex": "#57728B"},
                    {"name": "Soft Plum", "hex": "#86647A"},
                    {"name": "Moss Green", "hex": "#9CAF88"},
                    {"name": "Dusty Rose", "hex": "#D592AA"},
                    {"name": "Powder Blue", "hex": "#9BB8D3"},
                    {"name": "Mauve", "hex": "#C4A4A7"},
                ],
                "colors_to_avoid": [
                    {"name": "Bright Orange", "hex": "#FF8200"},
                    {"name": "Bright Yellow", "hex": "#FCE300"},
                    {"name": "Hot Pink", "hex": "#E3006D"},
                    {"name": "Electric Blue", "hex": "#00A3E1"},
                ],
                "description": "Soft Summer types look best in soft, muted colors with cool undertones. Avoid bright, vivid colors that can overwhelm your delicate coloring."
            },
            {
                "skin_tone": "Cool Summer",
                "flattering_colors": [
                    {"name": "Clear Blue", "hex": "#0077C8"},
                    {"name": "Soft Fuchsia", "hex": "#E31C79"},
                    {"name": "Cool Pink", "hex": "#F395C7"},
                    {"name": "Lavender", "hex": "#A277A6"},
                    {"name": "Soft Teal", "hex": "#00B0B9"},
                    {"name": "Periwinkle", "hex": "#7965B2"},
                ],
                "colors_to_avoid": [
                    {"name": "Orange", "hex": "#FF8200"},
                    {"name": "Warm Yellow", "hex": "#FFCD00"},
                    {"name": "Rust", "hex": "#9D4815"},
                    {"name": "Olive", "hex": "#A09958"},
                ],
                "description": "Cool Summer complexions look best in soft, cool colors with blue undertones. Avoid warm, bright colors that can clash with your cool coloring."
            },
            {
                "skin_tone": "Light Summer",
                "flattering_colors": [
                    {"name": "Lavender", "hex": "#DD9CDF"},
                    {"name": "Powder Blue", "hex": "#9BCBEB"},
                    {"name": "Dusty Rose", "hex": "#ECB3CB"},
                    {"name": "Soft Periwinkle", "hex": "#9595D2"},
                    {"name": "Aqua", "hex": "#71C5E8"},
                    {"name": "Soft Pink", "hex": "#F67599"},
                ],
                "colors_to_avoid": [
                    {"name": "Black", "hex": "#131413"},
                    {"name": "Orange", "hex": "#FF8200"},
                    {"name": "Bright Yellow", "hex": "#FCE300"},
                    {"name": "Burgundy", "hex": "#890C58"},
                ],
                "description": "Light Summer types look best in light, soft colors with cool undertones. Avoid dark, bright, or warm colors that can overwhelm your delicate coloring."
            },
            {
                "skin_tone": "Soft Autumn",
                "flattering_colors": [
                    {"name": "Taupe", "hex": "#DFD1A7"},
                    {"name": "Sage", "hex": "#BBC592"},
                    {"name": "Terracotta", "hex": "#C26E60"},
                    {"name": "Soft Teal", "hex": "#487A7B"},
                    {"name": "Camel", "hex": "#CDA788"},
                    {"name": "Salmon", "hex": "#DB864E"},
                ],
                "colors_to_avoid": [
                    {"name": "Black", "hex": "#131413"},
                    {"name": "Electric Blue", "hex": "#00A3E1"},
                    {"name": "Hot Pink", "hex": "#E3006D"},
                    {"name": "Bright White", "hex": "#FEFEFE"},
                ],
                "description": "Soft Autumn types look best in soft, warm, muted colors with golden undertones. Avoid bright, cool colors that can clash with your warm, muted coloring."
            },
            {
                "skin_tone": "Warm Autumn",
                "flattering_colors": [
                    {"name": "Mustard", "hex": "#B89D18"},
                    {"name": "Rust", "hex": "#9D4815"},
                    {"name": "Olive", "hex": "#A09958"},
                    {"name": "Burnt Orange", "hex": "#C4622D"},
                    {"name": "Teal", "hex": "#00778B"},
                    {"name": "Forest Green", "hex": "#205C40"},
                ],
                "colors_to_avoid": [
                    {"name": "Black", "hex": "#131413"},
                    {"name": "Cool Pink", "hex": "#F395C7"},
                    {"name": "Electric Blue", "hex": "#00A3E1"},
                    {"name": "Fuchsia", "hex": "#C724B1"},
                ],
                "description": "Warm Autumn complexions look best in warm, rich, earthy colors with golden undertones. Avoid cool, bright colors that can clash with your warm coloring."
            },
            {
                "skin_tone": "Deep Autumn",
                "flattering_colors": [
                    {"name": "Burgundy", "hex": "#890C58"},
                    {"name": "Chocolate", "hex": "#5C462B"},
                    {"name": "Deep Teal", "hex": "#00594C"},
                    {"name": "Rust", "hex": "#9D4815"},
                    {"name": "Olive", "hex": "#5E7E29"},
                    {"name": "Terracotta", "hex": "#A6631B"},
                ],
                "colors_to_avoid": [
                    {"name": "Pastels", "hex": "#F1EB9C"},
                    {"name": "Light Pink", "hex": "#F395C7"},
                    {"name": "Baby Blue", "hex": "#99D6EA"},
                    {"name": "Mint", "hex": "#A5DFD3"},
                ],
                "description": "Deep Autumn types look best in deep, warm, rich colors with golden undertones. Avoid light pastels and cool colors that can wash you out."
            }
        ]
        
        # Insert data
        for palette in palette_data:
            db_palette = ColorPalette(**palette)
            db.add(db_palette)
        
        db.commit()
        print(f"Successfully inserted {len(palette_data)} color palette records")
        
        # Initialize skin tone mappings
        monk_mappings = [
            {"monk_tone": "Monk01", "seasonal_type": "Light Spring", "hex_code": "#f6ede4"},
            {"monk_tone": "Monk02", "seasonal_type": "Light Spring", "hex_code": "#f3e7db"},
            {"monk_tone": "Monk03", "seasonal_type": "Clear Spring", "hex_code": "#f7ead0"},
            {"monk_tone": "Monk04", "seasonal_type": "Warm Spring", "hex_code": "#eadaba"},
            {"monk_tone": "Monk05", "seasonal_type": "Soft Autumn", "hex_code": "#d7bd96"},
            {"monk_tone": "Monk06", "seasonal_type": "Warm Autumn", "hex_code": "#a07e56"},
            {"monk_tone": "Monk07", "seasonal_type": "Deep Autumn", "hex_code": "#825c43"},
            {"monk_tone": "Monk08", "seasonal_type": "Deep Winter", "hex_code": "#604134"},
            {"monk_tone": "Monk09", "seasonal_type": "Cool Winter", "hex_code": "#3a312a"},
            {"monk_tone": "Monk10", "seasonal_type": "Clear Winter", "hex_code": "#292420"},
        ]
        
        for mapping in monk_mappings:
            db_mapping = SkinToneMapping(**mapping)
            db.add(db_mapping)
        
        db.commit()
        print(f"Successfully inserted {len(monk_mappings)} skin tone mapping records")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing color palette data: {e}")
        raise
    finally:
        db.close()
