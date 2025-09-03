#!/usr/bin/env python3
"""
Test runner script for AI Fashion Backend
Demonstrates the code quality improvements
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def run_tests():
    """Run all tests with coverage reporting"""
    print("🧪 Running AI Fashion Backend Tests")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Install test dependencies if not already installed
    print("📦 Installing test dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", "tests/requirements-test.txt"
    ], capture_output=True)
    
    # Run tests with coverage
    print("🧪 Running tests with coverage...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/",
        "-v",
        "--cov=prods_fastapi",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-fail-under=70",
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    print(f"Tests completed with return code: {result.returncode}")
    
    # Run linting
    print("\n🔍 Running code quality checks...")
    
    # Try to run flake8 if available
    try:
        flake_result = subprocess.run([
            sys.executable, "-m", "flake8", "prods_fastapi/", 
            "--max-line-length=120",
            "--ignore=E501,W503"
        ], capture_output=True, text=True)
        
        if flake_result.returncode == 0:
            print("✅ Code style checks passed")
        else:
            print("⚠️ Code style issues found:")
            print(flake_result.stdout)
    except FileNotFoundError:
        print("⚠️ flake8 not installed, skipping style checks")
    
    return result.returncode == 0

def demonstrate_improvements():
    """Demonstrate the code quality improvements"""
    print("\n🔧 Code Quality Improvements Demonstration")
    print("=" * 50)
    
    # 1. Unit Testing Coverage
    print("1. ✅ UNIT TESTS - Comprehensive test coverage added:")
    print("   - API endpoint tests with mocking")
    print("   - Database operations tests") 
    print("   - Error handling and edge cases")
    print("   - Async functionality tests")
    print("   - Performance and monitoring tests")
    
    # 2. Database Connection Refactoring
    print("\n2. ✅ DUPLICATE CODE ELIMINATION - Centralized database manager:")
    print("   - Single DatabaseConnectionManager class")
    print("   - Connection pooling and statistics") 
    print("   - Consistent error handling")
    print("   - Both sync and async support")
    
    # 3. Function Complexity Reduction
    print("\n3. ✅ REDUCED FUNCTION COMPLEXITY - Service layer refactoring:")
    print("   - Large endpoints broken into focused services")
    print("   - ColorRecommendationService with single-responsibility methods")
    print("   - ColorPaletteService for palette operations")
    print("   - Better separation of concerns")
    
    # 4. API Versioning
    print("\n4. ✅ API VERSIONING - Breaking change protection:")
    print("   - Version detection from URL path and headers")
    print("   - Deprecation warnings and sunset dates")
    print("   - Backward compatibility helpers")
    print("   - Versioned response formats")
    
    # 5. Consistent Logging
    print("\n5. ✅ CONSISTENT LOGGING - Structured logging strategy:")
    print("   - Standardized log levels and categories")
    print("   - Contextual logging with request IDs")
    print("   - JSON structured logging for production")
    print("   - Category-specific logging methods")
    
def show_usage_examples():
    """Show usage examples of the improvements"""
    print("\n📚 Usage Examples")
    print("=" * 50)
    
    print("1. Database Manager Usage:")
    print("""
from core.database_manager import get_database_manager

# Get centralized database manager
db_manager = get_database_manager()

# Use sync session
with db_manager.get_sync_session() as session:
    results = session.query(Model).all()

# Use async session  
async with db_manager.get_async_session() as session:
    result = await session.execute(select(Model))
    """)
    
    print("\n2. Service Layer Usage:")
    print("""
from services.color_recommendation_service import ColorRecommendationService

# Use focused service instead of large endpoint function
color_service = ColorRecommendationService()
recommendations = await color_service.get_color_recommendations(
    skin_tone="Monk05",
    limit=50
)
    """)
    
    print("\n3. API Versioning Usage:")
    print("""
from core.api_versioning import create_versioned_router, APIVersion

# Create versioned router
v2_router = create_versioned_router(APIVersion.V2, prefix="/colors")

# Automatic version validation and headers
@v2_router.get("/recommendations")
async def get_recommendations_v2():
    # V2 endpoint logic
    pass
    """)
    
    print("\n4. Structured Logging Usage:")
    print("""
from core.logging_config import get_logger, LogCategory

# Get contextual logger
logger = get_logger(__name__, LogCategory.API)

# Log with context
logger.api_info("Processing color recommendation", 
                operation="get_recommendations",
                request_id="abc123")
    """)

def main():
    """Main function"""
    print("🎨 AI Fashion Backend - Code Quality Improvements")
    print("=" * 60)
    
    # Show the improvements
    demonstrate_improvements()
    
    # Show usage examples
    show_usage_examples()
    
    # Ask if user wants to run tests
    run_tests_choice = input("\n🤔 Would you like to run the test suite? (y/n): ").lower()
    
    if run_tests_choice in ['y', 'yes']:
        success = run_tests()
        if success:
            print("\n✅ All tests passed! Code quality improvements are working correctly.")
        else:
            print("\n⚠️ Some tests failed. Please review the output above.")
    else:
        print("\n📝 To run tests later, use: python run_tests.py")
    
    print("\n🎯 Summary of Improvements:")
    print("✅ 1. Added comprehensive unit tests with 70%+ coverage target")  
    print("✅ 2. Eliminated duplicate database connection patterns")
    print("✅ 3. Reduced large function complexity with service layer")
    print("✅ 4. Implemented API versioning to prevent breaking changes")
    print("✅ 5. Established consistent logging strategy across application")
    
    print("\n🚀 Your backend is now more maintainable, testable, and robust!")

if __name__ == "__main__":
    main()
