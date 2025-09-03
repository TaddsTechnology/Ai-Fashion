#!/usr/bin/env python3
"""
Test script for MST Database Service Integration
"""

from mst_database_service import get_mst_color_recommendations, get_comprehensive_recommendations, get_all_mst_ids

def test_integration():
    print('=== Testing MST Database Service Integration ===')
    try:
        # Test 1: Get all available MST IDs
        print('\n1. Testing get_all_mst_ids():')
        all_ids = get_all_mst_ids()
        print(f'Available MST IDs: {all_ids[:5]}... ({len(all_ids)} total)')
        
        # Test 2: Get basic recommendations for first ID
        if all_ids:
            test_id = all_ids[0]
            print(f'\n2. Testing get_mst_color_recommendations() for {test_id}:')
            result = get_mst_color_recommendations(test_id, 'casual', 5)
            if 'error' not in result:
                print(f'Success: Found {len(result.get("colors_that_suit", []))} colors')
            else:
                print(f'Error: {result["error"]}')
            
            # Test 3: Get comprehensive recommendations  
            print(f'\n3. Testing get_comprehensive_recommendations() for {test_id}:')
            comp_result = get_comprehensive_recommendations(test_id, 'work', 3)
            if 'error' not in comp_result:
                print(f'Success: Comprehensive data available')
                print(f'   - Colors: {len(comp_result.get("colors_that_suit", []))}')
                print(f'   - Styling advice available: {"styling_advice" in comp_result}')
            else:
                print(f'Error: {comp_result["error"]}')
        
        print('\n=== Integration Test Complete ===')
        
    except Exception as e:
        print(f'Error during testing: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_integration()
