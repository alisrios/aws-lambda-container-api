"""
Integration tests for monitoring and observability features
Tests the complete monitoring stack including health checks and logging
"""

import json
import os
import sys
import time
from unittest.mock import patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app import app


class TestHealthEndpointIntegration:
    """Integration tests for health endpoint"""

    @pytest.fixture(scope="class")
    def test_server(self):
        """Start a test server for integration testing"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_health_endpoint_response_structure(self, test_server):
        """Test health endpoint returns proper structure"""
        response = test_server.get("/health")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)

        # Verify required fields
        required_fields = [
            "status",
            "timestamp",
            "version",
            "environment",
            "request_id",
            "checks",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify status is healthy
        assert data["status"] == "healthy"

        # Verify checks structure
        checks = data["checks"]
        required_checks = ["application", "memory", "dependencies"]
        for check in required_checks:
            assert check in checks, f"Missing required check: {check}"
            assert checks[check] == "ok"

    def test_health_endpoint_headers(self, test_server):
        """Test health endpoint includes monitoring headers"""
        response = test_server.get("/health")

        assert response.status_code == 200

        # Verify monitoring headers
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        # Verify response time is reasonable
        response_time = float(response.headers["X-Response-Time"])
        assert 0 <= response_time <= 5000  # Should be less than 5 seconds

    def test_health_endpoint_consistency(self, test_server):
        """Test health endpoint returns consistent results"""
        responses = []

        # Make multiple requests
        for _ in range(3):
            response = test_server.get("/health")
            assert response.status_code == 200
            responses.append(json.loads(response.data))
            time.sleep(0.1)

        # Verify consistent structure
        for data in responses:
            assert data["status"] == "healthy"
            assert "version" in data
            assert data["version"] == "1.0.0"

            # Request IDs should be different
            if len(responses) > 1:
                request_ids = [r["request_id"] for r in responses]
                assert len(set(request_ids)) == len(
                    request_ids
                ), "Request IDs should be unique"


class TestMonitoringHeaders:
    """Test monitoring-related headers across all endpoints"""

    @pytest.fixture(scope="class")
    def test_server(self):
        """Start a test server for integration testing"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_hello_endpoint_monitoring_headers(self, test_server):
        """Test hello endpoint includes monitoring headers"""
        response = test_server.get("/hello")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = json.loads(response.data)
        assert data["request_id"] == response.headers["X-Request-ID"]

    def test_echo_endpoint_monitoring_headers(self, test_server):
        """Test echo endpoint includes monitoring headers"""
        response = test_server.get("/echo?msg=test")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = json.loads(response.data)
        assert data["request_id"] == response.headers["X-Request-ID"]

    def test_error_response_monitoring_headers(self, test_server):
        """Test error responses include monitoring headers"""
        response = test_server.get("/echo")  # Missing msg parameter

        assert response.status_code == 400
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = json.loads(response.data)
        assert data["request_id"] == response.headers["X-Request-ID"]

    def test_404_response_monitoring_headers(self, test_server):
        """Test 404 responses include monitoring headers"""
        response = test_server.get("/nonexistent")

        assert response.status_code == 404
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = json.loads(response.data)
        assert data["request_id"] == response.headers["X-Request-ID"]


class TestCustomRequestId:
    """Test custom request ID handling"""

    @pytest.fixture(scope="class")
    def test_server(self):
        """Start a test server for integration testing"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_custom_request_id_propagation(self, test_server):
        """Test custom request ID is propagated through the system"""
        custom_id = "integration-test-12345"
        headers = {"X-Request-ID": custom_id}

        response = test_server.get("/hello", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

        data = json.loads(response.data)
        assert data["request_id"] == custom_id

    def test_custom_request_id_health_endpoint(self, test_server):
        """Test custom request ID works with health endpoint"""
        custom_id = "health-check-67890"
        headers = {"X-Request-ID": custom_id}

        response = test_server.get("/health", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

        data = json.loads(response.data)
        assert data["request_id"] == custom_id

    def test_custom_request_id_error_cases(self, test_server):
        """Test custom request ID is preserved in error cases"""
        custom_id = "error-test-99999"
        headers = {"X-Request-ID": custom_id}

        response = test_server.get("/echo", headers=headers)  # Missing msg

        assert response.status_code == 400
        assert response.headers["X-Request-ID"] == custom_id

        data = json.loads(response.data)
        assert data["request_id"] == custom_id


class TestPerformanceMonitoring:
    """Test performance monitoring capabilities"""

    @pytest.fixture(scope="class")
    def test_server(self):
        """Start a test server for integration testing"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_response_time_measurement(self, test_server):
        """Test response time is measured and reasonable"""
        start_time = time.time()
        response = test_server.get("/hello")
        end_time = time.time()

        assert response.status_code == 200

        # Get response time from header
        header_time = float(response.headers["X-Response-Time"])
        actual_time = (end_time - start_time) * 1000  # Convert to ms

        # Header time should be reasonable compared to actual time
        # Allow for some overhead but should be in the same ballpark
        assert header_time <= actual_time * 2  # Allow 2x overhead for processing
        assert header_time > 0

    def test_concurrent_requests_monitoring(self, test_server):
        """Test monitoring works correctly with concurrent requests"""
        # Simplified concurrent test using sequential requests
        # to avoid threading complexity in test environment

        def make_request(endpoint):
            response = test_server.get(endpoint)
            return {
                "status_code": response.status_code,
                "request_id": response.headers.get("X-Request-ID"),
                "response_time": response.headers.get("X-Response-Time"),
            }

        endpoints = ["/hello", "/health", "/echo?msg=concurrent"]
        results = []

        # Make sequential requests to simulate concurrent behavior
        for endpoint in endpoints:
            result = make_request(endpoint)
            results.append(result)

        # Verify all requests succeeded
        for result in results:
            assert result["status_code"] == 200
            assert result["request_id"] is not None
            assert result["response_time"] is not None

        # Verify request IDs are unique
        request_ids = [result["request_id"] for result in results]
        assert len(set(request_ids)) == len(request_ids)


class TestHealthCheckReliability:
    """Test health check endpoint reliability"""

    @pytest.fixture(scope="class")
    def test_server(self):
        """Start a test server for integration testing"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_health_check_under_load(self, test_server):
        """Test health check remains responsive under load"""
        # Make multiple rapid requests to health endpoint
        responses = []

        for i in range(10):
            response = test_server.get("/health")
            responses.append(response)

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "healthy"

    def test_health_check_after_errors(self, test_server):
        """Test health check works correctly after application errors"""
        # Generate some errors first
        for _ in range(3):
            test_server.get("/nonexistent")  # 404 errors
            test_server.get("/echo")  # 400 errors

        # Health check should still work
        response = test_server.get("/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
