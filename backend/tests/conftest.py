"""
Test configuration and fixtures for AI Fashion Backend tests
"""
import pytest
import asyncio
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_db():
    """Create a test database"""
    from backend.prods_fastapi.database import Base, engine
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db_session(test_db):
    """Create a test database session"""
    from backend.prods_fastapi.database import SessionLocal
    
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def client():
    """Create FastAPI test client"""
    from backend.prods_fastapi.main import app
    
    # Mock external dependencies
    with patch('backend.prods_fastapi.main.cloudinary_service') as mock_cloudinary, \
         patch('backend.prods_fastapi.main.enhanced_analyzer') as mock_analyzer:
        
        # Configure mocks
        mock_cloudinary.upload_image.return_value = {
            'success': True, 
            'url': 'https://test.com/image.jpg',
            'public_id': 'test_image'
        }
        
        mock_analyzer.analyze_skin_tone.return_value = {
            'success': True,
            'monk_skin_tone': 'Monk05',
            'confidence': 0.8,
            'derived_hex_code': '#d7bd96'
        }
        
        client = TestClient(app)
        yield client

@pytest.fixture
def mock_redis():
    """Mock Redis for testing"""
    with patch('redis.Redis') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_color_palette():
    """Sample color palette data for testing"""
    return {
        "skin_tone": "Test Winter",
        "flattering_colors": [
            {"name": "Test Blue", "hex": "#0057B8"},
            {"name": "Test Red", "hex": "#CE0037"}
        ],
        "colors_to_avoid": [
            {"name": "Test Orange", "hex": "#FF8200"}
        ],
        "description": "Test color palette"
    }

@pytest.fixture
def sample_monk_mapping():
    """Sample Monk tone mapping for testing"""
    return {
        "monk_tone": "Monk99",
        "seasonal_type": "Test Winter", 
        "hex_code": "#ffffff"
    }

@pytest.fixture
def mock_image_data():
    """Mock image data for testing"""
    # Create a simple test image bytes
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'

@pytest.fixture
def mock_performance_systems():
    """Mock performance systems for testing"""
    with patch('backend.prods_fastapi.main.init_performance_systems') as mock_init, \
         patch('backend.prods_fastapi.main.cleanup_performance_systems') as mock_cleanup:
        yield mock_init, mock_cleanup

# Test utilities
class TestUtils:
    @staticmethod
    def create_test_user_session(user_id="test_user"):
        """Create a test user session"""
        return {"user_id": user_id, "session_id": f"test_session_{user_id}"}
    
    @staticmethod
    def assert_valid_color_response(response_data):
        """Assert that a color response has valid structure"""
        assert "colors_that_suit" in response_data or "colors" in response_data
        if "colors_that_suit" in response_data:
            assert isinstance(response_data["colors_that_suit"], list)
            for color in response_data["colors_that_suit"]:
                assert "name" in color
                assert "hex" in color
                assert color["hex"].startswith("#")
    
    @staticmethod
    def assert_valid_skin_tone_response(response_data):
        """Assert that a skin tone response has valid structure"""
        assert "monk_skin_tone" in response_data
        assert "confidence" in response_data
        assert "derived_hex_code" in response_data
        assert response_data["derived_hex_code"].startswith("#")

@pytest.fixture
def test_utils():
    """Provide test utilities"""
    return TestUtils
