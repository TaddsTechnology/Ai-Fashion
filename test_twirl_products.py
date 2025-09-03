#!/usr/bin/env python3
"""
Test script to verify the new Twirl Around World products endpoint
"""
import requests
import json
import sys

def test_twirl_products_endpoint():
    """Test the /api/twirl-products endpoint"""
    try:
        print("Testing /api/twirl-products endpoint...")
        
        response = requests.get('http://localhost:8000/api/twirl-products')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data['total_items']} Twirl Around World products")
            
            # Print first few products as examples
            if data['data']:
                print("\nFirst 3 products:")
                for i, product in enumerate(data['data'][:3]):
                    print(f"  {i+1}. {product.get('product_name', 'N/A')} - {product.get('price', 'N/A')} ({product.get('brand', 'N/A')})")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the FastAPI server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_apparel_endpoint():
    """Test the /apparel endpoint to see if it includes Twirl products"""
    try:
        print("\nTesting /apparel endpoint...")
        
        response = requests.get('http://localhost:8000/apparel?page=1&limit=10')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data['total_items']} apparel products")
            
            # Check if any Twirl products are included
            twirl_products = []
            for product in data['data']:
                if 'Twirl' in product.get('Product Name', ''):
                    twirl_products.append(product)
            
            if twirl_products:
                print(f"  Found {len(twirl_products)} Twirl Around World products in apparel endpoint")
                for product in twirl_products[:2]:  # Show first 2
                    print(f"    - {product.get('Product Name', 'N/A')}")
            else:
                print("  No Twirl Around World products found in apparel endpoint")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the FastAPI server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Twirl Around World Products Integration")
    print("=" * 50)
    
    success1 = test_twirl_products_endpoint()
    success2 = test_apparel_endpoint()
    
    if success1 and success2:
        print("\n✅ All tests passed! The integration is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the server and try again.")
        sys.exit(1)
