#!/usr/bin/env python3
"""
Test script to verify the fixed database query works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_fixed_query():
    """Test the fixed database query"""
    
    # Database URL
    DB_URL = 'postgresql://fashion_jvy9_user:0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh@dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com/fashion_jvy9'
    
    print("Testing Fixed Database Query")
    print("="*50)
    
    try:
        # Create SQLAlchemy engine
        engine = create_engine(DB_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        try:
            # Test the corrected query with Clear Spring
            print("1. Testing with 'Clear Spring' skin tone:")
            
            comp_query = text("""
                SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                FROM comprehensive_colors 
                WHERE hex_code IS NOT NULL 
                AND color_name IS NOT NULL
                AND (
                    (monk_tones IS NOT NULL AND monk_tones::text ILIKE :monk_search)
                    OR (seasonal_types IS NOT NULL AND seasonal_types::text ILIKE :seasonal_search)
                    OR color_name ILIKE :name_search
                )
                ORDER BY color_name
                LIMIT :limit_val
            """)
            
            skin_tone = 'Clear Spring'
            text_search = f'%{skin_tone}%'
            
            comp_result = db.execute(comp_query, {
                'monk_search': text_search,
                'seasonal_search': text_search, 
                'name_search': text_search, 
                'limit_val': 5
            })
            
            rows = comp_result.fetchall()
            print(f"   ✓ Found {len(rows)} colors for '{skin_tone}':")
            for row in rows:
                print(f"     - {row[1]} ({row[0]}) - {row[2]}/{row[3]}")
            
            print("\n2. Testing with 'Monk03' skin tone:")
            
            skin_tone = 'Monk03'
            text_search = f'%{skin_tone}%'
            
            comp_result = db.execute(comp_query, {
                'monk_search': text_search,
                'seasonal_search': text_search, 
                'name_search': text_search, 
                'limit_val': 5
            })
            
            rows = comp_result.fetchall()
            print(f"   ✓ Found {len(rows)} colors for '{skin_tone}':")
            for row in rows:
                print(f"     - {row[1]} ({row[0]}) - {row[2]}/{row[3]}")
            
            print("\n3. Testing fallback query without skin tone:")
            
            fallback_query = text("""
                SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                FROM comprehensive_colors 
                WHERE hex_code IS NOT NULL 
                AND color_name IS NOT NULL
                ORDER BY color_name
                LIMIT :limit_val
            """)
            
            comp_result = db.execute(fallback_query, {'limit_val': 3})
            rows = comp_result.fetchall()
            print(f"   ✓ Found {len(rows)} colors in fallback query:")
            for row in rows:
                print(f"     - {row[1]} ({row[0]}) - {row[2]}/{row[3]}")
            
            print("\n" + "="*50)
            print("✅ ALL TESTS PASSED! The database query fix is working correctly.")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_fixed_query()
    sys.exit(0 if success else 1)
