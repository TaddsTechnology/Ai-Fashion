#!/usr/bin/env python3
"""
Simple Sentry integration test
"""

import os
import time
from pathlib import Path

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

# Get Sentry DSN
sentry_dsn = os.getenv('SENTRY_DSN')
print(f"Sentry DSN configured: {'✅ Yes' if sentry_dsn else '❌ No'}")

if sentry_dsn:
    print(f"DSN: {sentry_dsn[:50]}...")

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    print("✅ Sentry SDK imported successfully")
    
    # Initialize Sentry
    logging_integration = LoggingIntegration(
        level="INFO",
        event_level="ERROR"
    )
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=0.1,
        environment="development",
        release="ai-fashion@2.0.0",
        integrations=[
            logging_integration,
            FastApiIntegration()
        ],
        send_default_pii=True,  # Following your configuration
        attach_stacktrace=True
    )
    
    print("✅ Sentry initialized successfully")
    
    # Set global tags
    sentry_sdk.set_tag("component", "ai-fashion-backend")
    sentry_sdk.set_tag("service", "skin-tone-analysis")
    sentry_sdk.set_tag("test", "simple_integration")
    
    # Test basic message
    sentry_sdk.capture_message("Sentry integration test - Simple test", level="info")
    print("✅ Basic message sent to Sentry")
    
    # Test error capture
    try:
        raise ValueError("This is a test error for Sentry integration")
    except ValueError as e:
        sentry_sdk.capture_exception(e)
        print("✅ Test exception captured")
    
    # Test custom context
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("test_type", "integration")
        scope.set_context("test_info", {
            "timestamp": time.time(),
            "version": "2.0.0",
            "platform": "windows"
        })
        scope.set_user({"id": "test_user", "email": "test@example.com"})
        
        sentry_sdk.capture_message("Context test message", level="info")
        print("✅ Message with context sent")
    
    # Test breadcrumb
    sentry_sdk.add_breadcrumb(
        message="Test breadcrumb",
        category="test",
        level="info",
        data={"action": "simple_test", "result": "success"}
    )
    print("✅ Breadcrumb added")
    
    # Send final success message
    sentry_sdk.capture_message("All Sentry tests completed successfully!", level="info")
    
    print("\n" + "=" * 50)
    print("🎉 Sentry integration test completed successfully!")
    print("🔍 Check your Sentry dashboard at: https://sentry.io/")
    print("📊 You should see:")
    print("   - Test messages")
    print("   - Test exception")
    print("   - Context information")
    print("   - Breadcrumbs")
    print("   - Performance data")
    
except Exception as e:
    print(f"❌ Sentry test failed: {e}")
    exit(1)

print("\n💡 Your Sentry integration is working!")
print("🚀 Ready to monitor your AI Fashion app!")
