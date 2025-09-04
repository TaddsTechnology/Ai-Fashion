#!/usr/bin/env python3
"""
Debug script to test skin tone analysis and understand why it's always returning Monk 7
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import find_closest_monk_tone_improved, MONK_SKIN_TONES
import numpy as np
from webcolors import hex_to_rgb, rgb_to_hex

def test_skin_tone_analysis():
    """Test the skin tone analysis with different RGB values"""
    
    print("=== Monk Skin Tone Analysis Debug ===\n")
    
    # Test cases with different RGB values
    test_cases = [
        ("Very Light", [250, 240, 230]),  # Should be Monk 1-2
        ("Light", [235, 220, 200]),       # Should be Monk 3-4
        ("Medium Light", [210, 190, 160]), # Should be Monk 4-5
        ("Medium", [180, 150, 120]),      # Should be Monk 5-6
        ("Medium Dark", [130, 92, 67]),   # This is exactly Monk 7
        ("Dark", [96, 65, 52]),           # Should be Monk 8
        ("Very Dark", [41, 36, 32]),      # Should be Monk 10
    ]
    
    print("Testing different RGB values:\n")
    
    for description, rgb_values in test_cases:
        print(f"Testing {description}: RGB{tuple(rgb_values)}")
        
        # Convert to numpy array
        rgb_array = np.array(rgb_values, dtype=np.float64)
        
        # Analyze skin tone
        result = find_closest_monk_tone_improved(rgb_array)
        
        print(f"  Result: {result['monk_name']} ({result['monk_id']})")
        print(f"  Hex: {result['monk_hex']} -> Derived: {result['derived_hex']}")
        print()
    
    # Test with exact Monk tone RGB values
    print("Testing with exact Monk tone RGB values:\n")
    
    for monk_name, monk_hex in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(monk_hex), dtype=np.float64)
        result = find_closest_monk_tone_improved(monk_rgb)
        
        expected_match = monk_name == result['monk_name']
        status = "✓" if expected_match else "✗"
        
        print(f"{status} {monk_name}: RGB{tuple(monk_rgb.astype(int))} -> {result['monk_name']}")
        if not expected_match:
            print(f"    Expected: {monk_name}, Got: {result['monk_name']}")
    
    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    test_skin_tone_analysis()
