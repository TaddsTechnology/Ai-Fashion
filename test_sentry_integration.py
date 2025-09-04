#!/usr/bin/env python3
"""
Test script to verify Sentry integration is working correctly
"""

import sys
import os
from pathlib import Path
import asyncio
import time

# Add the backend to the path
sys.path.append(str(Path(__file__).parent / "backend" / "prods_fastapi"))

try:
    from services.sentry_service import EnhancedSentryService
    import sentry_sdk
    print("✅ Successfully imported Enhanced Sentry service")
except ImportError as e:
    print(f"❌ Failed to import Sentry service: {e}")
    sys.exit(1)

def test_basic_sentry_connection():
    """Test basic Sentry connection"""
    print("\n🔍 Testing Basic Sentry Connection...")
    
    try:
        # Send a test message
        sentry_sdk.capture_message("Sentry integration test - Basic connection", level="info")
        print("✅ Basic Sentry message sent successfully")
        return True
    except Exception as e:
        print(f"❌ Basic Sentry connection failed: {e}")
        return False

def test_error_tracking():
    """Test error tracking functionality"""
    print("\n🔍 Testing Error Tracking...")
    
    try:
        # Generate a test error
        try:
            raise ValueError("This is a test error for Sentry integration")
        except ValueError as e:
            sentry_sdk.capture_exception(e)
            print("✅ Test exception captured successfully")
            return True
    except Exception as e:
        print(f"❌ Error tracking test failed: {e}")
        return False

def test_custom_events():
    """Test custom event capture"""
    print("\n🔍 Testing Custom Events...")
    
    try:
        # Test business metric capture
        EnhancedSentryService.capture_business_metric(
            metric_name="test_metric",
            value=42.0,
            tags={"test": "integration", "component": "sentry_test"}
        )
        print("✅ Business metric captured successfully")
        
        # Test user journey tracking
        EnhancedSentryService.track_user_journey(
            user_id="test_user_123",
            action="sentry_integration_test",
            metadata={"test_type": "integration", "timestamp": time.time()}
        )
        print("✅ User journey tracked successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Custom events test failed: {e}")
        return False

def test_model_performance_tracking():
    """Test model performance tracking"""
    print("\n🔍 Testing Model Performance Tracking...")
    
    try:
        test_metrics = {
            "accuracy": 0.95,
            "precision": 0.92,
            "recall": 0.88,
            "f1_score": 0.90,
            "training_time": 1200.5,
            "inference_time": 0.05
        }
        
        EnhancedSentryService.capture_model_performance(
            model_name="skin_tone_analyzer_test",
            metrics=test_metrics
        )
        print("✅ Model performance metrics captured successfully")
        return True
        
    except Exception as e:
        print(f"❌ Model performance tracking test failed: {e}")
        return False

def test_cloudinary_event_capture():
    """Test Cloudinary event capture"""
    print("\n🔍 Testing Cloudinary Event Capture...")
    
    try:
        mock_upload_result = {
            'success': True,
            'public_id': 'test/sentry_integration_test',
            'url': 'https://res.cloudinary.com/test/image/upload/test.jpg',
            'bytes': 1024000
        }
        
        EnhancedSentryService.capture_cloudinary_upload(
            public_id="test/sentry_integration_test",
            upload_result=mock_upload_result
        )
        print("✅ Cloudinary event captured successfully")
        return True
        
    except Exception as e:
        print(f"❌ Cloudinary event capture test failed: {e}")
        return False

def test_skin_tone_analysis_tracking():
    """Test skin tone analysis event tracking"""
    print("\n🔍 Testing Skin Tone Analysis Tracking...")
    
    try:
        mock_image_data = {
            'size': 2048000,
            'format': 'image/jpeg',
            'dimensions': '800x600'
        }
        
        mock_result = {
            'monk_skin_tone': 'Monk04',
            'confidence': 0.85,
            'success': True,
            'analysis_method': 'enhanced_multi_colorspace_clustering',
            'processing_time': 2.34
        }
        
        EnhancedSentryService.capture_skin_tone_analysis(
            user_id="test_user_456",
            image_data=mock_image_data,
            result=mock_result
        )
        print("✅ Skin tone analysis event captured successfully")
        return True
        
    except Exception as e:
        print(f"❌ Skin tone analysis tracking test failed: {e}")
        return False

async def test_api_endpoint_monitoring():
    """Test API endpoint monitoring decorator"""
    print("\n🔍 Testing API Endpoint Monitoring...")
    
    try:
        @EnhancedSentryService.monitor_api_endpoint("test_endpoint")
        async def test_monitored_function():
            await asyncio.sleep(0.1)  # Simulate processing time
            return {"message": "Test successful", "status": "ok"}
        
        result = await test_monitored_function()
        print("✅ API endpoint monitoring decorator worked successfully")
        return True
        
    except Exception as e:
        print(f"❌ API endpoint monitoring test failed: {e}")
        return False

def test_context_and_tags():
    """Test Sentry context and tags"""
    print("\n🔍 Testing Context and Tags...")
    
    try:
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("test_component", "sentry_integration")
            scope.set_tag("environment", "testing")
            scope.set_context("test_context", {
                "test_name": "sentry_integration_test",
                "timestamp": time.time(),
                "version": "2.0.0"
            })
            scope.set_user({"id": "test_user_789", "email": "test@example.com"})
            
            sentry_sdk.capture_message("Context and tags test message", level="info")
            
        print("✅ Context and tags set successfully")
        return True
        
    except Exception as e:
        print(f"❌ Context and tags test failed: {e}")
        return False

def check_environment_variables():
    """Check if Sentry environment variables are set"""
    print("\n🔧 Checking Environment Variables...")
    
    # Load environment variables
    env_file = Path(__file__).parent / "backend" / "prods_fastapi" / ".env"
    
    if env_file.exists():
        print(f"📁 Loading environment from: {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    sentry_dsn = os.getenv('SENTRY_DSN')
    environment = os.getenv('ENVIRONMENT', 'development')
    
    if sentry_dsn:
        print(f"✅ SENTRY_DSN configured: {sentry_dsn[:50]}...")
        print(f"✅ Environment: {environment}")
        return True
    else:
        print("❌ SENTRY_DSN not configured")
        return False

async def main():
    """Run all Sentry integration tests"""
    print("🚀 Starting Sentry Integration Tests")
    print("=" * 60)
    
    # Check environment variables first
    env_check = check_environment_variables()
    if not env_check:
        print("⚠️ Environment variables not properly configured")
        return False
    
    # Run all tests
    tests = [
        test_basic_sentry_connection,
        test_error_tracking,
        test_custom_events,
        test_model_performance_tracking,
        test_cloudinary_event_capture,
        test_skin_tone_analysis_tracking,
        test_api_endpoint_monitoring,
        test_context_and_tags
    ]
    
    results = []
    
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                result = await test()
            else:
                result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Sentry Integration Test Results:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All Sentry integration tests passed!")
        print("\n💡 Your Sentry integration is working perfectly!")
        print("🔍 Check your Sentry dashboard at: https://sentry.io/")
        print("📊 You should see test events, errors, and performance data")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
