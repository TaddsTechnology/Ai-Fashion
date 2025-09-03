#!/usr/bin/env python3
"""
Test Enhanced Color Service with Database Integration
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'prods_fastapi'))

from services.enhanced_color_service import enhanced_color_service

def test_mst_service():
    """Test the enhanced color service functionality"""
    
    print("🧪 Testing Enhanced MST Color Service")
    print("=" * 50)
    
    # Test 1: Check if data was loaded
    print(f"📊 Loaded MST data for {len(enhanced_color_service.mst_palette_data)} skin tones")
    print(f"Available MST IDs: {sorted(enhanced_color_service.mst_palette_data.keys())}")
    print()
    
    # Test 2: Get comprehensive recommendations
    print("🎨 Testing Comprehensive Recommendations:")
    print("-" * 40)
    
    test_cases = [
        ("Monk03", "work"),
        ("Monk 5", "casual"),
        ("7", "party"),
        ("Monk10", "formal")
    ]
    
    for monk_tone, occasion in test_cases:
        try:
            recommendations = enhanced_color_service.get_comprehensive_recommendations(
                monk_tone=monk_tone,
                occasion=occasion,
                limit=8
            )
            
            print(f"✅ {monk_tone} ({occasion}):")
            print(f"   - MST ID: {recommendations['mst_id']}")
            print(f"   - Seasonal Type: {', '.join(recommendations['seasonal_type'])}")
            print(f"   - Undertones: {', '.join(recommendations['common_undertones'])}")
            print(f"   - Colors: {len(recommendations['colors_that_suit'])}")
            print(f"   - First 3 colors: {[c['name'] + ' (' + c['hex'] + ')' for c in recommendations['colors_that_suit'][:3]]}")
            print(f"   - Metals: {', '.join(recommendations['styling_advice']['metals'])}")
            print()
            
        except Exception as e:
            print(f"❌ Error testing {monk_tone} ({occasion}): {e}")
            print()
    
    # Test 3: Seasonal analysis
    print("🌟 Testing Seasonal Analysis:")
    print("-" * 30)
    
    try:
        analysis = enhanced_color_service.get_seasonal_analysis("Monk05")
        print(f"✅ Monk05 Seasonal Analysis:")
        print(f"   - Seasonal Types: {', '.join(analysis['seasonal_types'])}")
        print(f"   - Undertones: {', '.join(analysis['undertones'])}")
        print(f"   - Style Guide: {analysis['style_guide']['print_patterns']}")
        print(f"   - Examples: {', '.join(analysis['color_examples'][:5])}")
        print()
        
    except Exception as e:
        print(f"❌ Error in seasonal analysis: {e}")
        print()
    
    # Test 4: Season comparison
    print("🔍 Testing Season Comparison:")
    print("-" * 30)
    
    try:
        comparison = enhanced_color_service.compare_seasons("Monk02", "Monk08")
        print(f"✅ Monk02 vs Monk08 Comparison:")
        print(f"   - Common Seasons: {', '.join(comparison['comparison']['common_seasons'])}")
        print(f"   - Common Undertones: {', '.join(comparison['comparison']['common_undertones'])}")
        print(f"   - Monk02 Unique: {', '.join(comparison['comparison']['different_seasons']['Monk02'])}")
        print(f"   - Monk08 Unique: {', '.join(comparison['comparison']['different_seasons']['Monk08'])}")
        print()
        
    except Exception as e:
        print(f"❌ Error in season comparison: {e}")
        print()
    
    # Test 5: Edge cases
    print("⚠️  Testing Edge Cases:")
    print("-" * 20)
    
    edge_cases = [
        "Monk99",  # Non-existent MST ID
        "InvalidFormat",  # Invalid format
        "0",  # Edge MST ID
    ]
    
    for case in edge_cases:
        try:
            recommendations = enhanced_color_service.get_comprehensive_recommendations(
                monk_tone=case,
                occasion="casual",
                limit=5
            )
            print(f"✅ {case} -> MST-{recommendations['mst_id']} (fallback worked)")
            
        except Exception as e:
            print(f"❌ Error with {case}: {e}")
    
    print()
    print("🎉 Testing completed!")

if __name__ == "__main__":
    test_mst_service()
