#!/usr/bin/env python3

import requests
import json
import os
from pathlib import Path
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    # Create a small red square image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_health_endpoint():
    """Test the health endpoint first"""
    try:
        response = requests.get('https://devfashion.onrender.com/health', timeout=30)
        print(f"✅ Health endpoint status: {response.status_code}")
        print(f"📄 Health response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze-skin-tone endpoint"""
    try:
        # Create test image
        test_image = create_test_image()
        
        # Prepare the request
        files = {'file': ('test.jpg', test_image, 'image/jpeg')}
        url = 'https://devfashion.onrender.com/analyze-skin-tone'
        
        print(f"📤 Sending request to: {url}")
        print(f"📁 File size: {len(test_image.getvalue())} bytes")
        
        # Send request
        response = requests.post(url, files=files, timeout=60)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")
        print(f"📄 Response content length: {len(response.content)}")
        
        # Check response content
        if response.content:
            try:
                json_response = response.json()
                print(f"✅ Valid JSON response:")
                print(json.dumps(json_response, indent=2))
                return True
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text[:500]}...")
                return False
        else:
            print(f"❌ Empty response body")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🧪 Testing AI Fashion Backend Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("❌ Health endpoint failed, skipping analyze endpoint test")
        return
    
    # Test analyze endpoint
    print("\n2. Testing analyze-skin-tone endpoint...")
    analyze_ok = test_analyze_endpoint()
    
    if analyze_ok:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Analyze endpoint test failed")

if __name__ == "__main__":
    main()
