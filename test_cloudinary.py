#!/usr/bin/env python3
"""
Test Cloudinary connection and functionality
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the backend to the path so we can import our services
sys.path.append(str(Path(__file__).parent / "backend" / "prods_fastapi"))

try:
    from services.cloudinary_service import cloudinary_service
    import cloudinary
    import cloudinary.api
    print("✅ Successfully imported Cloudinary service")
except ImportError as e:
    print(f"❌ Failed to import Cloudinary service: {e}")
    sys.exit(1)

async def test_cloudinary_connection():
    """Test basic Cloudinary connection"""
    print("\n🔍 Testing Cloudinary Connection...")
    
    try:
        # Test API connection by getting account details
        result = cloudinary.api.ping()
        print(f"✅ Cloudinary connection successful!")
        print(f"   Status: {result.get('status', 'Unknown')}")
        
        # Get account usage info
        usage = cloudinary.api.usage()
        print(f"✅ Account usage retrieved:")
        print(f"   Resources: {usage.get('resources', 0)}")
        print(f"   Credits used: {usage.get('credits', 0)}")
        print(f"   Bandwidth used: {usage.get('bandwidth', 0)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Cloudinary connection failed: {e}")
        return False

async def test_image_upload():
    """Test image upload functionality"""
    print("\n📤 Testing Image Upload...")
    
    try:
        # Create a simple test image (1x1 pixel PNG)
        import base64
        from io import BytesIO
        from PIL import Image
        
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Test upload
        result = await cloudinary_service.upload_image(
            image_data=img_bytes.getvalue(),
            folder='user_uploads',
            tags=['test', 'ai-fashion'],
            public_id='test_upload_' + str(int(asyncio.get_event_loop().time()))
        )
        
        if result['success']:
            print(f"✅ Image upload successful!")
            print(f"   Public ID: {result['public_id']}")
            print(f"   URL: {result['url']}")
            print(f"   Size: {result.get('width')}x{result.get('height')}")
            
            # Test getting optimized URL
            optimized_url = cloudinary_service.get_optimized_url(
                result['public_id'],
                width=300,
                height=300
            )
            print(f"   Optimized URL: {optimized_url}")
            
            # Clean up - delete the test image
            delete_result = await cloudinary_service.delete_image(result['public_id'])
            if delete_result['success']:
                print(f"✅ Test image cleaned up successfully")
            
            return True
        else:
            print(f"❌ Image upload failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Image upload test failed: {e}")
        return False

async def test_folder_structure():
    """Test folder organization"""
    print("\n📁 Testing Folder Structure...")
    
    try:
        # List images in the ai_fashion folder
        result = await cloudinary_service.list_images(
            folder='ai_fashion',
            max_results=5
        )
        
        if result['success']:
            print(f"✅ Folder listing successful!")
            print(f"   Total images: {result.get('total_count', 0)}")
            
            if result['images']:
                print("   Recent images:")
                for img in result['images'][:3]:
                    print(f"     - {img['public_id']} ({img.get('format', 'unknown')})")
            else:
                print("   No images found in folder (this is normal for new accounts)")
                
            return True
        else:
            print(f"❌ Folder listing failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Folder structure test failed: {e}")
        return False

async def main():
    """Run all Cloudinary tests"""
    print("🚀 Starting Cloudinary Integration Tests")
    print("=" * 50)
    
    # Check environment variables
    print("🔧 Checking Configuration...")
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY') 
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ Missing Cloudinary environment variables!")
        print(f"   CLOUDINARY_CLOUD_NAME: {'✅' if cloud_name else '❌'}")
        print(f"   CLOUDINARY_API_KEY: {'✅' if api_key else '❌'}")
        print(f"   CLOUDINARY_API_SECRET: {'✅' if api_secret else '❌'}")
        return False
    
    print(f"✅ Configuration loaded:")
    print(f"   Cloud Name: {cloud_name}")
    print(f"   API Key: {api_key[:6]}...")
    print(f"   API Secret: {api_secret[:6]}...")
    
    # Run tests
    tests = [
        test_cloudinary_connection,
        test_image_upload,
        test_folder_structure
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All tests passed! Cloudinary is ready to use!")
        print("\n💡 Next steps:")
        print("   1. Create an upload preset in Cloudinary dashboard")
        print("   2. Test image uploads from your frontend")
        print("   3. Verify skin tone analysis with optimized images")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Load environment variables
    from pathlib import Path
    env_file = Path(__file__).parent / "backend" / "prods_fastapi" / ".env"
    
    if env_file.exists():
        print(f"📁 Loading environment from: {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Run the tests
    asyncio.run(main())
