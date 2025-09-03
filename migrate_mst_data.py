#!/usr/bin/env python3
"""
MST Master Palette Data Migration Script
Migrates data from mst_master_palette_all.json to PostgreSQL database
"""

import json
import os
import sys
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import execute_values
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def create_mst_palette_table(conn):
    """Create the MST master palette table"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS mst_master_palette (
        id SERIAL PRIMARY KEY,
        mst_id INTEGER UNIQUE NOT NULL,
        seasonal_type JSONB,
        common_undertones JSONB,
        base_palette JSONB,
        accent_palette JSONB,
        avoid_palette JSONB,
        neutrals_light JSONB,
        neutrals_dark JSONB,
        metals JSONB,
        denim_wash JSONB,
        prints_patterns TEXT,
        contrast_rules TEXT,
        pairing_rules TEXT,
        occasion_palettes JSONB,
        examples JSONB,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create index for faster lookups
    CREATE INDEX IF NOT EXISTS idx_mst_palette_mst_id ON mst_master_palette(mst_id);
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info("MST master palette table created successfully")
    except Exception as e:
        logger.error(f"Failed to create table: {e}")
        conn.rollback()
        raise

def load_mst_data():
    """Load MST data from JSON file"""
    json_path = os.path.join("backend", "datasets", "mst_master_palette_all.json")
    
    if not os.path.exists(json_path):
        # Try alternative paths
        alternative_paths = [
            "backend/datasets/mst_master_palette_all.json",
            "datasets/mst_master_palette_all.json",
            "mst_master_palette_all.json"
        ]
        
        for path in alternative_paths:
            if os.path.exists(path):
                json_path = path
                break
        else:
            raise FileNotFoundError("Could not find mst_master_palette_all.json file")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logger.info(f"Loaded {len(data)} MST palette records from {json_path}")
            return data
    except Exception as e:
        logger.error(f"Failed to load MST data: {e}")
        raise

def insert_mst_data(conn, mst_data):
    """Insert MST data into database"""
    insert_sql = """
    INSERT INTO mst_master_palette (
        mst_id, seasonal_type, common_undertones, base_palette, accent_palette,
        avoid_palette, neutrals_light, neutrals_dark, metals, denim_wash,
        prints_patterns, contrast_rules, pairing_rules, occasion_palettes,
        examples, notes
    ) VALUES (
        %(mst_id)s, %(seasonal_type)s, %(common_undertones)s, %(base_palette)s,
        %(accent_palette)s, %(avoid_palette)s, %(neutrals_light)s, %(neutrals_dark)s,
        %(metals)s, %(denim_wash)s, %(prints_patterns)s, %(contrast_rules)s,
        %(pairing_rules)s, %(occasion_palettes)s, %(examples)s, %(notes)s
    )
    ON CONFLICT (mst_id) DO UPDATE SET
        seasonal_type = EXCLUDED.seasonal_type,
        common_undertones = EXCLUDED.common_undertones,
        base_palette = EXCLUDED.base_palette,
        accent_palette = EXCLUDED.accent_palette,
        avoid_palette = EXCLUDED.avoid_palette,
        neutrals_light = EXCLUDED.neutrals_light,
        neutrals_dark = EXCLUDED.neutrals_dark,
        metals = EXCLUDED.metals,
        denim_wash = EXCLUDED.denim_wash,
        prints_patterns = EXCLUDED.prints_patterns,
        contrast_rules = EXCLUDED.contrast_rules,
        pairing_rules = EXCLUDED.pairing_rules,
        occasion_palettes = EXCLUDED.occasion_palettes,
        examples = EXCLUDED.examples,
        notes = EXCLUDED.notes,
        updated_at = CURRENT_TIMESTAMP;
    """
    
    try:
        with conn.cursor() as cursor:
            for record in mst_data:
                # Prepare the data for insertion
                insert_data = {
                    'mst_id': record['mst_id'],
                    'seasonal_type': json.dumps(record.get('seasonal_type', [])),
                    'common_undertones': json.dumps(record.get('common_undertones', [])),
                    'base_palette': json.dumps(record.get('base_palette', [])),
                    'accent_palette': json.dumps(record.get('accent_palette', [])),
                    'avoid_palette': json.dumps(record.get('avoid_palette', [])),
                    'neutrals_light': json.dumps(record.get('neutrals_light', [])),
                    'neutrals_dark': json.dumps(record.get('neutrals_dark', [])),
                    'metals': json.dumps(record.get('metals', [])),
                    'denim_wash': json.dumps(record.get('denim_wash', [])),
                    'prints_patterns': record.get('prints_patterns', ''),
                    'contrast_rules': record.get('contrast_rules', ''),
                    'pairing_rules': record.get('pairing_rules', ''),
                    'occasion_palettes': json.dumps(record.get('occasion_palettes', {})),
                    'examples': json.dumps(record.get('examples', [])),
                    'notes': record.get('notes', '')
                }
                
                cursor.execute(insert_sql, insert_data)
                logger.info(f"Inserted/Updated MST-{record['mst_id']}")
            
            conn.commit()
            logger.info(f"Successfully inserted {len(mst_data)} MST palette records")
            
    except Exception as e:
        logger.error(f"Failed to insert MST data: {e}")
        conn.rollback()
        raise

def verify_data(conn):
    """Verify the inserted data"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM mst_master_palette;")
            count = cursor.fetchone()[0]
            logger.info(f"Total records in mst_master_palette table: {count}")
            
            cursor.execute("""
                SELECT mst_id, 
                       jsonb_array_length(seasonal_type) as seasonal_types,
                       jsonb_array_length(base_palette) as base_colors,
                       jsonb_array_length(accent_palette) as accent_colors
                FROM mst_master_palette 
                ORDER BY mst_id;
            """)
            
            records = cursor.fetchall()
            logger.info("MST ID | Seasonal Types | Base Colors | Accent Colors")
            logger.info("-" * 55)
            for record in records:
                mst_id, seasonal_types, base_colors, accent_colors = record
                logger.info(f"MST-{mst_id:2d} | {seasonal_types:13d} | {base_colors:10d} | {accent_colors:12d}")
                
    except Exception as e:
        logger.error(f"Failed to verify data: {e}")

def create_database_functions(conn):
    """Create helper functions for easier data access"""
    functions_sql = """
    -- Function to get MST palette by ID
    CREATE OR REPLACE FUNCTION get_mst_palette(mst_id_param INTEGER)
    RETURNS TABLE(
        mst_id INTEGER,
        seasonal_type JSONB,
        base_palette JSONB,
        accent_palette JSONB,
        avoid_palette JSONB,
        occasion_palettes JSONB,
        styling_advice JSONB
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            mp.mst_id,
            mp.seasonal_type,
            mp.base_palette,
            mp.accent_palette,
            mp.avoid_palette,
            mp.occasion_palettes,
            jsonb_build_object(
                'metals', mp.metals,
                'denim_wash', mp.denim_wash,
                'prints_patterns', mp.prints_patterns,
                'contrast_rules', mp.contrast_rules,
                'pairing_rules', mp.pairing_rules
            ) as styling_advice
        FROM mst_master_palette mp
        WHERE mp.mst_id = mst_id_param;
    END;
    $$ LANGUAGE plpgsql;

    -- Function to get colors by occasion
    CREATE OR REPLACE FUNCTION get_mst_occasion_colors(mst_id_param INTEGER, occasion_param TEXT)
    RETURNS JSONB AS $$
    DECLARE
        result JSONB;
    BEGIN
        SELECT occasion_palettes->occasion_param
        INTO result
        FROM mst_master_palette
        WHERE mst_id = mst_id_param;
        
        RETURN COALESCE(result, '[]'::jsonb);
    END;
    $$ LANGUAGE plpgsql;
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(functions_sql)
            conn.commit()
            logger.info("Database helper functions created successfully")
    except Exception as e:
        logger.error(f"Failed to create functions: {e}")
        conn.rollback()

def main():
    """Main migration function"""
    logger.info("Starting MST Master Palette data migration...")
    
    try:
        # Connect to database
        logger.info("Connecting to PostgreSQL database...")
        conn = connect_to_database()
        
        # Create table
        logger.info("Creating MST master palette table...")
        create_mst_palette_table(conn)
        
        # Load data
        logger.info("Loading MST data from JSON file...")
        mst_data = load_mst_data()
        
        # Insert data
        logger.info("Inserting MST data into database...")
        insert_mst_data(conn, mst_data)
        
        # Create helper functions
        logger.info("Creating database helper functions...")
        create_database_functions(conn)
        
        # Verify data
        logger.info("Verifying inserted data...")
        verify_data(conn)
        
        logger.info("✅ MST Master Palette data migration completed successfully!")
        
        # Show usage examples
        print("\n" + "="*60)
        print("🎯 USAGE EXAMPLES:")
        print("="*60)
        print("1. Get palette for MST-3:")
        print("   SELECT * FROM get_mst_palette(3);")
        print("\n2. Get work colors for MST-5:")
        print("   SELECT get_mst_occasion_colors(5, 'work');")
        print("\n3. Get all MST IDs and seasonal types:")
        print("   SELECT mst_id, seasonal_type FROM mst_master_palette ORDER BY mst_id;")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Database connection closed")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
