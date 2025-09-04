#!/usr/bin/env python3
"""
Script to populate comprehensive_colors table with correct syntax
"""
from sqlalchemy import create_engine, text
import json

# New Neon database URL
DATABASE_URL = "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def populate_comprehensive_colors():
    """Insert comprehensive colors data"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Sample comprehensive colors
        sample_colors = [
            ('#000080', 'Navy Blue', 'blue', 'dark', '["Monk03", "Monk04", "Monk05", "Monk06"]'),
            ('#228B22', 'Forest Green', 'green', 'medium', '["Monk02", "Monk03", "Monk04", "Monk05"]'),
            ('#800020', 'Burgundy', 'red', 'dark', '["Monk04", "Monk05", "Monk06", "Monk07"]'),
            ('#36454F', 'Charcoal Gray', 'neutral', 'dark', '["Monk01", "Monk02", "Monk03", "Monk04", "Monk05"]'),
            ('#F5F5DC', 'Cream White', 'neutral', 'light', '["Monk06", "Monk07", "Monk08", "Monk09", "Monk10"]'),
            ('#FFB6C1', 'Soft Pink', 'pink', 'light', '["Monk01", "Monk02", "Monk03"]'),
            ('#663399', 'Royal Purple', 'purple', 'medium', '["Monk03", "Monk04", "Monk05"]'),
            ('#50C878', 'Emerald Green', 'green', 'medium', '["Monk04", "Monk05", "Monk06"]'),
            ('#FF6600', 'Deep Orange', 'orange', 'medium', '["Monk02", "Monk03", "Monk04"]'),
            ('#8B4513', 'Chocolate Brown', 'brown', 'dark', '["Monk05", "Monk06", "Monk07"]'),
            ('#008080', 'Teal', 'blue', 'medium', '["Monk03", "Monk04", "Monk05", "Monk06"]'),
            ('#DC143C', 'Crimson Red', 'red', 'medium', '["Monk04", "Monk05", "Monk06"]'),
            ('#FFD700', 'Golden Yellow', 'yellow', 'bright', '["Monk02", "Monk03", "Monk04"]'),
            ('#FF7F50', 'Coral', 'orange', 'medium', '["Monk01", "Monk02", "Monk03"]'),
            ('#9932CC', 'Dark Orchid', 'purple', 'dark', '["Monk05", "Monk06", "Monk07", "Monk08"]'),
            ('#2E8B57', 'Sea Green', 'green', 'medium', '["Monk03", "Monk04", "Monk05"]'),
            ('#4682B4', 'Steel Blue', 'blue', 'medium', '["Monk02", "Monk03", "Monk04", "Monk05"]'),
            ('#D2691E', 'Chocolate', 'brown', 'medium', '["Monk04", "Monk05", "Monk06"]'),
            ('#CD5C5C', 'Indian Red', 'red', 'medium', '["Monk05", "Monk06", "Monk07"]'),
            ('#F0E68C', 'Khaki', 'yellow', 'light', '["Monk04", "Monk05", "Monk06"]]')
        ]
        
        with engine.connect() as conn:
            # Check if table has data
            count_result = conn.execute(text("SELECT COUNT(*) FROM comprehensive_colors"))
            count = count_result.fetchone()[0]
            
            if count == 0:
                print("🎨 Populating comprehensive_colors table...")
                
                for hex_code, color_name, family, brightness, monk_tones_json in sample_colors:
                    conn.execute(text("""
                        INSERT INTO comprehensive_colors (hex_code, color_name, color_family, brightness_level, monk_tones)
                        VALUES (:hex, :name, :family, :brightness, :monk_tones::json)
                    """), {
                        'hex': hex_code,
                        'name': color_name,
                        'family': family,
                        'brightness': brightness,
                        'monk_tones': monk_tones_json
                    })
                
                conn.commit()
                print(f"✅ Inserted {len(sample_colors)} colors into comprehensive_colors")
                
                # Verify insertion
                count_result = conn.execute(text("SELECT COUNT(*) FROM comprehensive_colors"))
                new_count = count_result.fetchone()[0]
                print(f"📊 Total records in comprehensive_colors: {new_count}")
            else:
                print(f"ℹ️  comprehensive_colors already has {count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating colors: {e}")
        return False

def test_queries():
    """Test some common queries"""
    try:
        engine = create_engine(DATABASE_URL)
        
        print("\n🧪 Testing database queries:")
        print("=" * 40)
        
        with engine.connect() as conn:
            # Test skin tone mappings
            result = conn.execute(text("SELECT monk_tone, seasonal_type FROM skin_tone_mappings WHERE monk_tone = 'Monk03'"))
            row = result.fetchone()
            if row:
                print(f"✅ Monk03 maps to: {row[1]}")
            
            # Test comprehensive colors for Monk03
            result = conn.execute(text("""
                SELECT color_name, hex_code FROM comprehensive_colors 
                WHERE monk_tones::text LIKE '%Monk03%' LIMIT 5
            """))
            colors = result.fetchall()
            print(f"🎨 Colors for Monk03:")
            for color in colors:
                print(f"   - {color[0]}: {color[1]}")
            
            # Test color palettes
            result = conn.execute(text("SELECT skin_tone FROM color_palettes LIMIT 5"))
            palettes = result.fetchall()
            print(f"🎯 Available color palettes:")
            for palette in palettes:
                print(f"   - {palette[0]}")
        
        print("✅ All queries working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing queries: {e}")
        return False

if __name__ == "__main__":
    print("🎨 AI Fashion Database Population Script")
    print("=" * 50)
    
    if populate_comprehensive_colors():
        test_queries()
    else:
        print("❌ Failed to populate database")
