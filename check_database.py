#!/usr/bin/env python3
"""
Script to explore Neon database structure and test connection
"""
import os
import psycopg2
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json

# New Neon database URL
DATABASE_URL = "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def test_connection():
    """Test basic database connection"""
    try:
        print("🔍 Testing database connection...")
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"📊 PostgreSQL Version: {version}")
            return engine
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def explore_database_structure(engine):
    """Explore the database structure - tables, columns, etc."""
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        print(f"\n📋 Database Tables ({len(table_names)} total):")
        print("=" * 50)
        
        if not table_names:
            print("❌ No tables found in database")
            return {}
        
        table_info = {}
        
        for table_name in table_names:
            print(f"\n🔸 Table: {table_name}")
            
            # Get column info
            columns = inspector.get_columns(table_name)
            print("   Columns:")
            
            table_info[table_name] = {
                'columns': [],
                'sample_data': None,
                'row_count': 0
            }
            
            for col in columns:
                col_info = f"   - {col['name']}: {col['type']}"
                if not col['nullable']:
                    col_info += " (NOT NULL)"
                if col.get('default'):
                    col_info += f" DEFAULT {col['default']}"
                print(col_info)
                
                table_info[table_name]['columns'].append({
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'default': col.get('default')
                })
        
        return table_info
        
    except Exception as e:
        print(f"❌ Error exploring database: {e}")
        return {}

def get_table_data(engine, table_info):
    """Get sample data from each table"""
    try:
        print(f"\n📊 Sample Data from Tables:")
        print("=" * 50)
        
        for table_name, info in table_info.items():
            try:
                print(f"\n🔹 {table_name}:")
                
                # Get row count
                with engine.connect() as conn:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    row_count = count_result.fetchone()[0]
                    info['row_count'] = row_count
                    print(f"   Total rows: {row_count}")
                    
                    if row_count > 0:
                        # Get sample data (first 5 rows)
                        sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                        df = pd.read_sql(sample_query, engine)
                        print(f"   Sample data (first 5 rows):")
                        print(df.to_string(index=False))
                        info['sample_data'] = df.to_dict('records')
                    else:
                        print("   ⚠️ Table is empty")
                        
            except Exception as e:
                print(f"   ❌ Error reading {table_name}: {e}")
        
        return table_info
        
    except Exception as e:
        print(f"❌ Error getting table data: {e}")
        return table_info

def check_ai_fashion_specific_tables(engine):
    """Check for AI Fashion specific tables and data"""
    print(f"\n🎨 Checking for AI Fashion specific data:")
    print("=" * 50)
    
    # Tables we expect for AI Fashion
    expected_tables = [
        'skin_tone_mappings',
        'color_palettes', 
        'comprehensive_colors',
        'colors',
        'color_suggestions',
        'makeup_products',
        'outfit_products'
    ]
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    for table in expected_tables:
        if table in existing_tables:
            print(f"✅ {table} - EXISTS")
            try:
                with engine.connect() as conn:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    print(f"   └── {count} records")
            except Exception as e:
                print(f"   └── Error counting: {e}")
        else:
            print(f"❌ {table} - MISSING")

def create_missing_tables(engine):
    """Create missing AI Fashion tables if needed"""
    print(f"\n🛠️ Creating missing AI Fashion tables:")
    print("=" * 50)
    
    create_statements = {
        'skin_tone_mappings': """
            CREATE TABLE IF NOT EXISTS skin_tone_mappings (
                id SERIAL PRIMARY KEY,
                monk_tone VARCHAR(10) NOT NULL,
                hex_code VARCHAR(7) NOT NULL,
                seasonal_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        'color_palettes': """
            CREATE TABLE IF NOT EXISTS color_palettes (
                id SERIAL PRIMARY KEY,
                skin_tone VARCHAR(50) NOT NULL,
                flattering_colors JSONB,
                colors_to_avoid JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        'comprehensive_colors': """
            CREATE TABLE IF NOT EXISTS comprehensive_colors (
                id SERIAL PRIMARY KEY,
                hex_code VARCHAR(7) NOT NULL,
                color_name VARCHAR(100) NOT NULL,
                color_family VARCHAR(50),
                brightness_level VARCHAR(20),
                monk_tones JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        'colors': """
            CREATE TABLE IF NOT EXISTS colors (
                id SERIAL PRIMARY KEY,
                hex_code VARCHAR(7) NOT NULL,
                color_name VARCHAR(100) NOT NULL,
                seasonal_palette VARCHAR(50),
                category VARCHAR(20) DEFAULT 'recommended',
                suitable_skin_tone VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
    }
    
    try:
        with engine.connect() as conn:
            for table_name, create_sql in create_statements.items():
                try:
                    conn.execute(text(create_sql))
                    conn.commit()
                    print(f"✅ Created/verified table: {table_name}")
                except Exception as e:
                    print(f"❌ Error creating {table_name}: {e}")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

def insert_sample_data(engine):
    """Insert sample data if tables are empty"""
    print(f"\n📦 Inserting sample data:")
    print("=" * 50)
    
    try:
        with engine.connect() as conn:
            # Sample skin tone mappings
            monk_data = [
                ('Monk01', '#f6ede4', 'Light Spring'),
                ('Monk02', '#f3e7db', 'Light Spring'),
                ('Monk03', '#f7ead0', 'Clear Spring'),
                ('Monk04', '#eadaba', 'Warm Spring'),
                ('Monk05', '#d7bd96', 'Soft Autumn'),
                ('Monk06', '#a07e56', 'Warm Autumn'),
                ('Monk07', '#825c43', 'Deep Autumn'),
                ('Monk08', '#604134', 'Deep Winter'),
                ('Monk09', '#3a312a', 'Cool Winter'),
                ('Monk10', '#292420', 'Clear Winter')
            ]
            
            # Check if skin_tone_mappings has data
            count_result = conn.execute(text("SELECT COUNT(*) FROM skin_tone_mappings"))
            if count_result.fetchone()[0] == 0:
                print("📝 Inserting Monk skin tone mappings...")
                for monk_tone, hex_code, seasonal in monk_data:
                    conn.execute(text("""
                        INSERT INTO skin_tone_mappings (monk_tone, hex_code, seasonal_type)
                        VALUES (:monk_tone, :hex_code, :seasonal)
                    """), {
                        'monk_tone': monk_tone,
                        'hex_code': hex_code,
                        'seasonal': seasonal
                    })
                conn.commit()
                print("✅ Inserted Monk skin tone mappings")
            
            # Sample comprehensive colors
            sample_colors = [
                ('#000080', 'Navy Blue', 'blue', 'dark', '["Monk03", "Monk04", "Monk05"]'),
                ('#228B22', 'Forest Green', 'green', 'medium', '["Monk02", "Monk03", "Monk04"]'),
                ('#800020', 'Burgundy', 'red', 'dark', '["Monk04", "Monk05", "Monk06"]'),
                ('#36454F', 'Charcoal Gray', 'neutral', 'dark', '["Monk01", "Monk02", "Monk03", "Monk04", "Monk05"]'),
                ('#F5F5DC', 'Cream White', 'neutral', 'light', '["Monk06", "Monk07", "Monk08", "Monk09", "Monk10"]'),
                ('#FFB6C1', 'Soft Pink', 'pink', 'light', '["Monk01", "Monk02", "Monk03"]'),
                ('#663399', 'Royal Purple', 'purple', 'medium', '["Monk03", "Monk04", "Monk05"]'),
                ('#50C878', 'Emerald Green', 'green', 'medium', '["Monk04", "Monk05", "Monk06"]'),
                ('#FF6600', 'Deep Orange', 'orange', 'medium', '["Monk02", "Monk03", "Monk04"]'),
                ('#8B4513', 'Chocolate Brown', 'brown', 'dark', '["Monk05", "Monk06", "Monk07"]')
            ]
            
            # Check if comprehensive_colors has data
            count_result = conn.execute(text("SELECT COUNT(*) FROM comprehensive_colors"))
            if count_result.fetchone()[0] == 0:
                print("🎨 Inserting sample color data...")
                for hex_code, color_name, family, brightness, monk_tones in sample_colors:
                    conn.execute(text("""
                        INSERT INTO comprehensive_colors (hex_code, color_name, color_family, brightness_level, monk_tones)
                        VALUES (:hex, :name, :family, :brightness, :monk_tones::jsonb)
                    """), {
                        'hex': hex_code,
                        'name': color_name,
                        'family': family,
                        'brightness': brightness,
                        'monk_tones': monk_tones
                    })
                conn.commit()
                print("✅ Inserted sample color data")
            
            print("🎉 Sample data insertion complete!")
            
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")

def main():
    """Main function to explore the database"""
    print("🔍 AI Fashion Database Explorer")
    print("=" * 50)
    
    # Test connection
    engine = test_connection()
    if not engine:
        return
    
    # Explore current structure
    table_info = explore_database_structure(engine)
    
    # Get sample data
    table_info = get_table_data(engine, table_info)
    
    # Check for AI Fashion specific tables
    check_ai_fashion_specific_tables(engine)
    
    # Create missing tables
    create_missing_tables(engine)
    
    # Insert sample data if needed
    insert_sample_data(engine)
    
    # Final summary
    print(f"\n📊 Database Summary:")
    print("=" * 30)
    print(f"Database: neondb")
    print(f"Host: ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech")
    print(f"Connection: ✅ Working with SSL")
    print(f"Tables found: {len(table_info)}")
    
    total_rows = sum(info.get('row_count', 0) for info in table_info.values())
    print(f"Total records: {total_rows}")
    
    # Save detailed info to file
    try:
        with open('database_info.json', 'w') as f:
            json.dump(table_info, f, indent=2, default=str)
        print(f"💾 Detailed info saved to database_info.json")
    except Exception as e:
        print(f"❌ Could not save info file: {e}")
    
    print(f"\n🎯 Next steps:")
    print(f"1. Update backend to use new DATABASE_URL")
    print(f"2. Test API endpoints with new database")
    print(f"3. Deploy to HuggingFace with updated connection")

if __name__ == "__main__":
    main()
