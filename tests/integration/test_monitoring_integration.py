"""
Integration tests for monitoring and observability features
Tests the complete monitoring stack including health checks and logging
"""

import json
import pytest
import requests
import time
from unittest.mock import patch


class TestHealthEndpointIntegration:
    """Integration tests for health endpoint"""

    def test_health_endpoint_response_structure(self, local_server_url):
        """Test health endpoint returns proper structure"""
        response = requests.get(f"{local_server_url}/health")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        data = response.json()

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

    def test_health_endpoint_headers(self, local_server_url):
        """Test health endpoint includes monitoring headers"""
        response = requests.get(f"{local_server_url}/health")

        assert response.status_code == 200

        # Verify monitoring headers
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        # Verify response time is reasonable
        response_time = float(response.headers["X-Response-Time"])
        assert 0 <= response_time <= 5000  # Should be less than 5 seconds

    def test_health_endpoint_consistency(self, local_server_url):
        """Test health endpoint returns consistent results"""
        responses = []

        # Make multiple requests
        for _ in range(3):
            response = requests.get(f"{local_server_url}/health")
            assert response.status_code == 200
            responses.append(response.json())
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

    def test_hello_endpoint_monitoring_headers(self, local_server_url):
        """Test hello endpoint includes monitoring headers"""
        response = requests.get(f"{local_server_url}/hello")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = response.json()
        assert data["request_id"] == response.headers["X-Request-ID"]

    def test_echo_endpoint_monitoring_headers(self, local_server_url):
        """Test echo endpoint includes monitoring headers"""
        response = requests.get(f"{local_server_url}/echo?msg=test")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = response.json()
        assert data["request_id"] == response.headers["X-Request-ID"]

    def test_error_response_monitoring_headers(self, local_server_url):
        """Test error responses include monitoring headers"""
        response = requests.get(f"{local_server_url}/echo")  # Missing msg parameter

        assert response.status_code == 400
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = response.json()
        assert data["request_id"] == response.headers["X-Request-ID"]

    def test_404_response_monitoring_headers(self, local_server_url):
        """Test 404 responses include monitoring headers"""
        response = requests.get(f"{local_server_url}/nonexistent")

        assert response.status_code == 404
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = response.json()
        assert data["request_id"] == response.headers["X-Request-ID"]


class TestCustomRequestId:
    """Test custom request ID handling"""

    def test_custom_request_id_propagation(self, local_server_url):
        """Test custom request ID is propagated through the system"""
        custom_id = "integration-test-12345"
        headers = {"X-Request-ID": custom_id}

        response = requests.get(f"{local_server_url}/hello", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

        data = response.json()
        assert data["request_id"] == custom_id

    def test_custom_request_id_health_endpoint(self, local_server_url):
        """Test custom request ID works with health endpoint"""
        custom_id = "health-check-67890"
        headers = {"X-Request-ID": custom_id}

        response = requests.get(f"{local_server_url}/health", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

        data = response.json()
        assert data["request_id"] == custom_id

    def test_custom_request_id_error_cases(self, local_server_url):
        """Test custom request ID is preserved in error cases"""
        custom_id = "error-test-99999"
        headers = {"X-Request-ID": custom_id}

        response = requests.get(
            f"{local_server_url}/echo", headers=headers
        )  # Missing msg

        assert response.status_code == 400
        assert response.headers["X-Request-ID"] == custom_id

        data = response.json()
        assert data["request_id"] == custom_id


class TestPerformanceMonitoring:
    """Test performance monitoring capabilities"""

    def test_response_time_measurement(self, local_server_url):
        """Test response time is measured and reasonable"""
        start_time = time.time()
        response = requests.get(f"{local_server_url}/hello")
        end_time = time.time()

        assert response.status_code == 200

        # Get response time from header
        header_time = float(response.headers["X-Response-Time"])
        actual_time = (end_time - start_time) * 1000  # Convert to ms

        # Header time should be reasonable compared to actual time
        # Allow for some overhead but should be in the same ballpark
        assert header_time <= actual_time * 2  # Allow 2x overhead for processing
        assert header_time > 0

    def test_concurrent_requests_monitoring(self, local_server_url):
        """Test monitoring works correctly with concurrent requests"""
        import concurrent.futures
        import threading

        def make_request(endpoint):
            response = requests.get(f"{local_server_url}{endpoint}")
            return {
                "status_code": response.status_code,
                "request_id": response.headers.get("X-Request-ID"),
                "response_time": response.headers.get("X-Response-Time"),
            }

        endpoints = ["/hello", "/health", "/echo?msg=concurrent"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(make_request, endpoint) for endpoint in endpoints
            ]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

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

    def test_health_check_under_load(self, local_server_url):
        """Test health check remains responsive under load"""
        # Make multiple rapid requests to health endpoint
        responses = []

        for i in range(10):
            response = requests.get(f"{local_server_url}/health")
            responses.append(response)

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_health_check_after_errors(self, local_server_url):
        """Test health check works correctly after application errors"""
        # Generate some errors first
        for _ in range(3):
            requests.get(f"{local_server_url}/nonexistent")  # 404 errors
            requests.get(f"{local_server_url}/echo")  # 400 errors

        # Health check should still work
        response = requests.get(f"{local_server_url}/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
