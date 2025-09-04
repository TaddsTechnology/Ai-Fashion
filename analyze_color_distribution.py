#!/usr/bin/env python3
"""
Analyze why fewer colors are returned despite 1087+ total colors in database
"""

import psycopg2
import json

# Database configuration
DB_CONFIG = {
    'host': 'dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com',
    'database': 'fashion_jvy9',
    'user': 'fashion_jvy9_user',
    'password': '0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh',
    'port': '5432',
    'sslmode': 'require'
}

def analyze_database_distribution():
    """Analyze how colors are distributed across tables and why fewer are returned"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 ANALYZING COLOR DISTRIBUTION IN DATABASE")
        print("=" * 60)
        
        # 1. Total counts per table
        tables = ['colors', 'color_palettes', 'skin_tone_mappings', 'comprehensive_colors', 'color_suggestions', 'color_hex_data']
        total_records = 0
        
        print("\n📊 TOTAL RECORDS PER TABLE:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"  {table}: {count} records")
        
        print(f"\n🔢 TOTAL DATABASE RECORDS: {total_records}")
        
        # 2. How color_palettes work (the main source for recommendations)
        print(f"\n🎨 COLOR_PALETTES TABLE ANALYSIS:")
        cursor.execute("SELECT skin_tone, flattering_colors FROM color_palettes;")
        palettes = cursor.fetchall()
        
        total_palette_colors = 0
        for palette in palettes:
            skin_tone = palette[0]
            colors = palette[1] if isinstance(palette[1], list) else json.loads(palette[1] or '[]')
            color_count = len(colors)
            total_palette_colors += color_count
            print(f"  {skin_tone}: {color_count} flattering colors")
        
        print(f"\n📈 TOTAL COLORS IN ALL PALETTES: {total_palette_colors}")
        
        # 3. Why fewer colors are returned - the logic
        print(f"\n🤔 WHY FEWER COLORS ARE RETURNED:")
        print("=" * 40)
        
        print("🔄 CURRENT API LOGIC:")
        print("  1️⃣ User has Monk05 → Maps to 'Soft Autumn'")
        print("  2️⃣ API queries: SELECT flattering_colors FROM color_palettes WHERE skin_tone = 'Soft Autumn'")
        print("  3️⃣ Returns ONLY colors for that specific seasonal type")
        print("  4️⃣ Limited to 12 colors max in the code: colors[:12]")
        
        # 4. Example for Monk05
        print(f"\n📝 EXAMPLE - MONK05 ANALYSIS:")
        cursor.execute("""
            SELECT stm.seasonal_type, cp.flattering_colors
            FROM skin_tone_mappings stm
            JOIN color_palettes cp ON stm.seasonal_type = cp.skin_tone
            WHERE stm.monk_tone = 'Monk05'
        """)
        
        result = cursor.fetchone()
        if result:
            seasonal_type = result[0]
            colors = result[1] if isinstance(result[1], list) else json.loads(result[1] or '[]')
            print(f"  Monk05 → {seasonal_type}")
            print(f"  Available colors for {seasonal_type}: {len(colors)}")
            print(f"  API returns: {min(len(colors), 12)} colors (limited in code)")
        
        # 5. How to get more colors
        print(f"\n💡 HOW TO GET MORE COLORS:")
        print("=" * 30)
        
        print("🔧 OPTION 1 - Remove the limit:")
        print("  Change: colors = flattering_colors[:12]")
        print("  To:     colors = flattering_colors  # Return all colors")
        
        print(f"\n🔧 OPTION 2 - Query multiple tables:")
        print("  • Get colors from color_palettes (seasonal-specific)")
        print("  • ALSO get colors from comprehensive_colors (275 records)")
        print("  • ALSO get colors from 'colors' table (723 records)")
        print("  • Combine and return more variety")
        
        print(f"\n🔧 OPTION 3 - Query by Monk tone directly:")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM comprehensive_colors 
            WHERE monk_tones::text LIKE '%Monk05%'
        """)
        monk_specific = cursor.fetchone()[0]
        print(f"  Colors for Monk05 in comprehensive_colors: {monk_specific}")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM colors 
            WHERE seasonal_palette = 'Soft Autumn' 
            AND category = 'recommended'
        """)
        seasonal_specific = cursor.fetchone()[0]
        print(f"  Recommended colors for Soft Autumn in colors table: {seasonal_specific}")
        
        # 6. The real breakdown
        print(f"\n📋 REAL BREAKDOWN OF 1087 RECORDS:")
        print("=" * 40)
        print(f"  • colors table: 723 records (all seasonal types)")
        print(f"  • comprehensive_colors: 275 records (advanced matching)")
        print(f"  • color_palettes: 12 records (seasonal summaries)")
        print(f"  • skin_tone_mappings: 10 records (Monk mappings)")
        print(f"  • color_suggestions: 47 records (general suggestions)")
        print(f"  • color_hex_data: 20 records (hex data)")
        print(f"\n  📌 CURRENT API ONLY USES: color_palettes (12 records)")
        print(f"  📌 EACH PALETTE HAS: 6-14 colors per seasonal type")
        print(f"  📌 CODE LIMIT: Maximum 12 colors returned")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎯 SOLUTION:")
        print("To get more colors, modify the API to query multiple tables")
        print("and remove or increase the 12-color limit!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_database_distribution()
