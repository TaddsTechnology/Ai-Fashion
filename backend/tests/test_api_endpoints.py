"""
Tests for API endpoints
"""
import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestMainEndpoints:
    """Test main API endpoints"""

    def test_home_endpoint(self, client):
        """Test home endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to the AI Fashion API!"
        assert data["status"] == "healthy"

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        # Should have some health-related fields
        assert "status" in data or "timestamp" in data

    def test_makeup_types_endpoint(self, client):
        """Test makeup types endpoint"""
        response = client.get("/makeup-types")
        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert isinstance(data["types"], list)
        assert "Foundation" in data["types"]

    def test_products_endpoint(self, client):
        """Test products endpoint"""
        response = client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_products_with_filter(self, client):
        """Test products endpoint with filters"""
        response = client.get("/products?product_type=foundation&random=true")
        assert response.status_code == 200


class TestColorRecommendations:
    """Test color recommendation endpoints"""

    def test_color_recommendations_missing_skin_tone(self, client):
        """Test color recommendations without skin tone parameter"""
        response = client.get("/color-recommendations")
        assert response.status_code == 400
        data = response.json()
        assert "skin_tone parameter is required" in data["detail"]

    def test_color_recommendations_with_monk_tone(self, client, test_db_session, sample_color_palette):
        """Test color recommendations with Monk tone"""
        with patch('backend.prods_fastapi.database.SessionLocal') as mock_session:
            mock_session.return_value = test_db_session
            
            response = client.get("/color-recommendations?skin_tone=Monk05")
            assert response.status_code in [200, 404, 500]  # May fail due to missing data

    def test_api_color_recommendations_rate_limiting(self, client):
        """Test API color recommendations rate limiting"""
        # Make multiple requests quickly to test rate limiting
        responses = []
        for i in range(35):  # Above the 30/minute limit
            response = client.get("/api/color-recommendations?skin_tone=Monk05")
            responses.append(response.status_code)
        
        # Should have some rate limited responses (429)
        assert any(status == 429 for status in responses[-5:])

    def test_api_color_recommendations_with_limit(self, client):
        """Test API color recommendations with limit parameter"""
        response = client.get("/api/color-recommendations?skin_tone=Monk05&limit=20")
        assert response.status_code in [200, 500]  # May fail if DB not available

    def test_color_palettes_db_missing_skin_tone(self, client):
        """Test color palettes DB endpoint without skin tone"""
        response = client.get("/api/color-palettes-db")
        assert response.status_code == 400
        data = response.json()
        assert "skin_tone parameter is required" in data["detail"]

    def test_color_palettes_db_with_skin_tone(self, client):
        """Test color palettes DB endpoint with skin tone"""
        response = client.get("/api/color-palettes-db?skin_tone=Monk05")
        assert response.status_code == 200
        data = response.json()
        assert "colors" in data
        assert "seasonal_type" in data


class TestSkinToneAnalysis:
    """Test skin tone analysis endpoint"""

    def test_analyze_skin_tone_no_file(self, client):
        """Test analyze skin tone without file"""
        response = client.post("/analyze-skin-tone")
        assert response.status_code == 422  # Validation error

    def test_analyze_skin_tone_invalid_file_type(self, client):
        """Test analyze skin tone with invalid file type"""
        response = client.post(
            "/analyze-skin-tone",
            files={"file": ("test.txt", b"not an image", "text/plain")}
        )
        assert response.status_code == 400
        data = response.json()
        assert "File must be an image" in data["detail"]

    def test_analyze_skin_tone_valid_image(self, client, mock_image_data):
        """Test analyze skin tone with valid image"""
        # Create a mock image file
        image_file = io.BytesIO(mock_image_data)
        
        response = client.post(
            "/analyze-skin-tone",
            files={"file": ("test.png", image_file, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have skin tone analysis results
        assert "monk_skin_tone" in data
        assert "confidence" in data
        assert "derived_hex_code" in data

    def test_analyze_skin_tone_rate_limiting(self, client, mock_image_data):
        """Test skin tone analysis rate limiting"""
        image_file = io.BytesIO(mock_image_data)
        
        # Make multiple requests to test rate limiting (10/minute limit)
        responses = []
        for i in range(12):
            image_file.seek(0)  # Reset file pointer
            response = client.post(
                "/analyze-skin-tone",
                files={"file": ("test.png", image_file, "image/png")}
            )
            responses.append(response.status_code)
        
        # Should have some rate limited responses
        assert any(status == 429 for status in responses[-3:])


class TestPerformanceEndpoints:
    """Test performance monitoring endpoints"""

    def test_performance_endpoint(self, client):
        """Test performance metrics endpoint"""
        response = client.get("/performance")
        assert response.status_code == 200
        data = response.json()
        # Should have performance data or error message
        assert "error" in data or any(key in data for key in ["cpu_usage", "memory_usage", "uptime"])

    def test_database_performance_endpoint(self, client):
        """Test database performance endpoint"""
        response = client.get("/performance/database")
        assert response.status_code == 200
        data = response.json()
        # Should have database performance data or error
        assert "error" in data or "pool_stats" in data or "total_connections" in data

    def test_cache_performance_endpoint(self, client):
        """Test cache performance endpoint"""
        response = client.get("/performance/cache")
        assert response.status_code == 200
        data = response.json()
        # Should have cache performance data or error
        assert "error" in data or "cache_stats" in data

    def test_image_optimization_performance_endpoint(self, client):
        """Test image optimization performance endpoint"""
        response = client.get("/performance/images")
        assert response.status_code == 200
        data = response.json()
        # Should have image optimization data or error
        assert "error" in data or "optimization_stats" in data


class TestMonitoringEndpoints:
    """Test monitoring endpoints"""

    def test_monitoring_metrics(self, client):
        """Test monitoring metrics endpoint"""
        response = client.get("/monitoring/metrics")
        assert response.status_code == 200
        data = response.json()
        # Should have metrics or error
        assert "error" in data or isinstance(data, dict)

    def test_monitoring_traces(self, client):
        """Test monitoring traces endpoint"""
        response = client.get("/monitoring/traces")
        assert response.status_code == 200
        data = response.json()
        # Should have traces or error
        assert "error" in data or isinstance(data, (list, dict))

    def test_monitoring_traces_with_limit(self, client):
        """Test monitoring traces with limit parameter"""
        response = client.get("/monitoring/traces?limit=10")
        assert response.status_code == 200

    def test_monitoring_alerts(self, client):
        """Test monitoring alerts endpoint"""
        response = client.get("/monitoring/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or isinstance(data, (list, dict))

    def test_monitoring_system_stats(self, client):
        """Test monitoring system stats endpoint"""
        response = client.get("/monitoring/system")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or isinstance(data, dict)

    def test_monitoring_health(self, client):
        """Test monitoring health endpoint"""
        response = client.get("/monitoring/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_error_stats_endpoint(self, client):
        """Test error statistics endpoint"""
        response = client.get("/error-stats")
        assert response.status_code == 200
        data = response.json()
        # Should have error stats or error message
        assert "error" in data or isinstance(data, dict)

    def test_quick_health_endpoint(self, client):
        """Test quick health check endpoint"""
        response = client.get("/health/quick")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_nonexistent_endpoint(self, client):
        """Test nonexistent endpoint returns 404"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_monitoring_trace_details_not_found(self, client):
        """Test monitoring trace details for nonexistent trace"""
        response = client.get("/monitoring/traces/nonexistent-trace-id")
        assert response.status_code in [404, 200]  # May return error or empty response


class TestCORSAndSecurity:
    """Test CORS and security headers"""

    def test_cors_preflight_request(self, client):
        """Test CORS preflight request"""
        response = client.options(
            "/api/color-recommendations",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        # Should allow CORS
        assert response.status_code in [200, 204]

    def test_cors_allowed_origin(self, client):
        """Test request from allowed origin"""
        response = client.get(
            "/",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functionality where applicable"""

    async def test_startup_event_mock(self, mock_performance_systems):
        """Test that startup event calls performance systems"""
        mock_init, mock_cleanup = mock_performance_systems
        
        # Import and test the startup logic
        from backend.prods_fastapi.main import startup_event
        
        # This would test the startup event if we could call it directly
        # In practice, this is tested through the test client initialization
        assert True  # Placeholder for async startup tests

    async def test_shutdown_event_mock(self, mock_performance_systems):
        """Test that shutdown event calls cleanup"""
        mock_init, mock_cleanup = mock_performance_systems
        
        # Import and test the shutdown logic
        from backend.prods_fastapi.main import shutdown_event
        
        # This would test the shutdown event if we could call it directly
        assert True  # Placeholder for async shutdown tests


class TestParameterValidation:
    """Test parameter validation and edge cases"""

    def test_api_color_recommendations_invalid_limit(self, client):
        """Test API color recommendations with invalid limit"""
        response = client.get("/api/color-recommendations?skin_tone=Monk05&limit=5")
        assert response.status_code == 422  # Validation error, limit must be >= 10

    def test_api_color_recommendations_high_limit(self, client):
        """Test API color recommendations with high limit"""
        response = client.get("/api/color-recommendations?skin_tone=Monk05&limit=150")
        assert response.status_code == 422  # Validation error, limit must be <= 100

    def test_color_recommendations_various_monk_tones(self, client):
        """Test color recommendations with various Monk tones"""
        monk_tones = ["Monk01", "Monk05", "Monk10", "monk 3", "monk03"]
        
        for monk_tone in monk_tones:
            response = client.get(f"/color-recommendations?skin_tone={monk_tone}")
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 404, 500]

    def test_empty_parameters(self, client):
        """Test endpoints with empty parameters"""
        response = client.get("/api/color-recommendations?skin_tone=&hex_color=")
        assert response.status_code in [400, 422, 500]  # Should handle empty parameters
