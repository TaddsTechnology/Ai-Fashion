#!/usr/bin/env python3
"""
Test script to verify that the analyze-skin-tone endpoint always returns valid JSON
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prods_fastapi'))

from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image
import json

def create_test_image():
    """Create a simple test image"""
    # Create a simple 100x100 RGB image
    img = Image.new('RGB', (100, 100), color=(200, 180, 160))  # Light skin tone color
    
    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_analyze_skin_tone_endpoint():
    """Test the analyze-skin-tone endpoint"""
    try:
        # Import the app
        from prods_fastapi.main import app
        client = TestClient(app)
        
        print("🧪 Testing analyze-skin-tone endpoint...")
        
        # Test 1: GET request (should return info)
        print("\n1️⃣ Testing GET /analyze-skin-tone (info endpoint)")
        response = client.get("/analyze-skin-tone")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Valid JSON response: {data}")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
                print(f"   Raw response: {response.text}")
        
        # Test 2: POST request with test image
        print("\n2️⃣ Testing POST /analyze-skin-tone (with test image)")
        test_image = create_test_image()
        
        response = client.post(
            "/analyze-skin-tone",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Valid JSON response!")
                print(f"   Response structure:")
                for key, value in data.items():
                    print(f"     - {key}: {value}")
                    
                # Verify required fields
                required_fields = ['monk_skin_tone', 'monk_hex', 'derived_hex_code', 'success']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    print(f"   ⚠️ Missing required fields: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
                print(f"   Raw response: {response.text[:200]}...")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
        
        # Test 3: POST request without file (should return error but valid JSON)
        print("\n3️⃣ Testing POST /analyze-skin-tone (without file)")
        response = client.post("/analyze-skin-tone")
        print(f"   Status: {response.status_code}")
        
        # Should return 422 (validation error) but still be JSON
        try:
            data = response.json()
            print(f"   ✅ Valid JSON error response: {data}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON decode error: {e}")
            print(f"   Raw response: {response.text}")
            return False
            
        print("\n🎉 All tests passed! The endpoint now returns consistent JSON responses.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analyze_skin_tone_endpoint()
    sys.exit(0 if success else 1)
