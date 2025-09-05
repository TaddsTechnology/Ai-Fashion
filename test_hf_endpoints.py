#!/usr/bin/env python3
"""
Simple test script to verify HuggingFace backend API endpoints are working
Run this after deploying to HuggingFace to test the database-powered endpoints
"""

import requests
import json
from typing import Dict, Any

# Replace with your actual HuggingFace Space URL
HF_BASE_URL = "https://your-username-ai-fashion.hf.space"

def test_endpoint(endpoint: str, params: Dict[str, Any] = None) -> None:
    """Test a single endpoint"""
    url = f"{HF_BASE_URL}{endpoint}"
    
    try:
        print(f"\n🔍 Testing: {endpoint}")
        print(f"📍 URL: {url}")
        
        if params:
            print(f"📋 Parameters: {params}")
            response = requests.get(url, params=params)
        else:
            response = requests.get(url)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            
            # Show key information from response
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], list):
                    print(f"📦 Found {len(data['data'])} items")
                    if data['data']:
                        print(f"🏷️ Sample item keys: {list(data['data'][0].keys())}")
                
                if 'total_items' in data:
                    print(f"📊 Total items: {data['total_items']}")
                
                if 'database_source' in data:
                    print(f"🗄️ Database source: {data['database_source']}")
                
                if 'message' in data:
                    print(f"💬 Message: {data['message']}")
            
            print(f"📄 Response preview: {str(data)[:200]}...")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

def main():
    """Test all the enhanced HuggingFace endpoints"""
    
    print("🚀 Testing HuggingFace AI Fashion Backend Endpoints")
    print("=" * 60)
    
    # Test basic health check
    test_endpoint("/health")
    
    # Test database health
    test_endpoint("/health/database")
    
    # Test makeup products endpoint
    test_endpoint("/data/", {"limit": "5", "page": "1"})
    
    # Test makeup products with skin tone filter
    test_endpoint("/data/", {"limit": "3", "mst": "Monk05"})
    
    # Test apparel/outfits endpoint
    test_endpoint("/apparel", {"limit": "5", "page": "1"})
    
    # Test apparel with color filter
    test_endpoint("/apparel", {"limit": "3", "color": "Blue"})
    
    # Test color recommendations
    test_endpoint("/color-palettes-db", {"skin_tone": "Soft Autumn", "limit": "10"})
    
    # Test personalized product recommendations
    test_endpoint("/products-by-skin-analysis", {
        "monk_skin_tone": "Monk05",
        "seasonal_type": "Soft Autumn",
        "product_category": "both",
        "limit": "6"
    })
    
    # Test product search
    test_endpoint("/search-products", {"query": "foundation", "limit": "5"})
    
    print("\n" + "=" * 60)
    print("🎉 API endpoint testing complete!")
    print("\n💡 To use this script:")
    print("1. Replace HF_BASE_URL with your actual HuggingFace Space URL")
    print("2. Run: python test_hf_endpoints.py")
    print("3. Check that all endpoints return ✅ Success!")

if __name__ == "__main__":
    main()
