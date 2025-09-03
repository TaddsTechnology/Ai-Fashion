#!/usr/bin/env python3
"""
Simple Cloudinary connection test
"""
import os
import cloudinary
import cloudinary.api
import cloudinary.uploader
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / "backend" / "prods_fastapi" / ".env"
    
    if env_file.exists():
        print(f"📁 Loading environment from: {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    else:
        print(f"❌ Environment file not found: {env_file}")

def test_cloudinary():
    """Test Cloudinary connection and functionality"""
    print("🚀 Testing Cloudinary Connection")
    print("=" * 50)
    
    # Load environment variables
    load_env()
    
    # Get credentials
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    print("🔧 Checking Configuration...")
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
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    
    print("\n🔍 Testing API Connection...")
    try:
        # Test API connection
        result = cloudinary.api.ping()
        print(f"✅ Cloudinary connection successful!")
        print(f"   Status: {result.get('status', 'Unknown')}")
        
        # Get account usage
        usage = cloudinary.api.usage()
        print(f"✅ Account usage retrieved:")
        print(f"   Resources: {usage.get('resources', 0)}")
        print(f"   Credits used: {usage.get('credits', 0)}")
        print(f"   Bandwidth used: {usage.get('bandwidth', 0)} bytes")
        
    except Exception as e:
        print(f"❌ Cloudinary connection failed: {e}")
        return False
    
    print("\n📤 Testing Image Upload...")
    try:
        # Create a simple test image
        from PIL import Image
        from io import BytesIO
        import time
        
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Upload test image
        public_id = f"test_upload_{int(time.time())}"
        upload_result = cloudinary.uploader.upload(
            img_bytes.getvalue(),
            folder="ai_fashion/test",
            public_id=public_id,
            tags=["test", "ai-fashion"]
        )
        
        print(f"✅ Image upload successful!")
        print(f"   Public ID: {upload_result['public_id']}")
        print(f"   URL: {upload_result['secure_url']}")
        print(f"   Size: {upload_result['width']}x{upload_result['height']}")
        
        # Test URL transformation
        from cloudinary import CloudinaryImage
        optimized_url = CloudinaryImage(upload_result['public_id']).build_url(
            width=300, height=300, crop='fill', quality='auto:good'
        )
        print(f"   Optimized URL: {optimized_url}")
        
        # Clean up - delete test image
        delete_result = cloudinary.uploader.destroy(upload_result['public_id'])
        if delete_result['result'] == 'ok':
            print(f"✅ Test image cleaned up successfully")
        
    except Exception as e:
        print(f"❌ Image upload test failed: {e}")
        return False
    
    print("\n📁 Testing Folder Listing...")
    try:
        # List images in ai_fashion folder using API resources
        resources_result = cloudinary.api.resources(
            type='upload',
            prefix='ai_fashion/',
            max_results=5
        )
        
        print(f"✅ Folder listing successful!")
        print(f"   Total images: {len(resources_result.get('resources', []))}")
        
        if resources_result.get('resources'):
            print("   Recent images:")
            for img in resources_result['resources'][:3]:
                print(f"     - {img['public_id']} ({img.get('format', 'unknown')})")
        else:
            print("   No images found in folder (this is normal for new accounts)")
            
    except Exception as e:
        print(f"❌ Folder listing test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Cloudinary is ready to use!")
    print("\n💡 Next steps:")
    print("   1. Create an upload preset named 'ai_fashion' in Cloudinary dashboard")
    print("   2. Set the upload preset to 'Unsigned' for frontend uploads")
    print("   3. Configure folder structure: ai_fashion/uploads, ai_fashion/processed, etc.")
    print("   4. Test image uploads from your React frontend")
    
    return True

if __name__ == "__main__":
    success = test_cloudinary()
    exit(0 if success else 1)
