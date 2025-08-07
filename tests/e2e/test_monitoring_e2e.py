"""
End-to-end tests for monitoring and observability features
Tests monitoring functionality on deployed infrastructure
"""

import json
import os
import time

import pytest
import requests


class TestDeployedMonitoring:
    """Test monitoring features on deployed API"""

    def test_deployed_health_endpoint(self, deployed_api_url):
        """Test health endpoint on deployed API"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        response = requests.get(f"{deployed_api_url}/health")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        data = response.json()

        # Verify health response structure
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "request_id" in data
        assert "checks" in data

        # Verify environment is not development
        assert data["environment"] != "development"

        # Verify checks are all OK
        checks = data["checks"]
        for check_name, check_status in checks.items():
            assert check_status == "ok", f"Health check {check_name} failed"

    def test_deployed_monitoring_headers(self, deployed_api_url):
        """Test monitoring headers on deployed API"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        endpoints = ["/hello", "/echo?msg=monitoring_test", "/health"]

        for endpoint in endpoints:
            response = requests.get(f"{deployed_api_url}{endpoint}")

            assert response.status_code == 200

            # Verify monitoring headers
            assert "X-Request-ID" in response.headers
            assert "X-Response-Time" in response.headers

            # Verify response time is reasonable for deployed API
            response_time = float(response.headers["X-Response-Time"])
            assert 0 <= response_time <= 30000  # 30 seconds max for cold starts

            # Verify request ID in response body
            data = response.json()
            assert data["request_id"] == response.headers["X-Request-ID"]

    def test_deployed_custom_request_id(self, deployed_api_url):
        """Test custom request ID handling on deployed API"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        custom_id = f"e2e-test-{int(time.time())}"
        headers = {"X-Request-ID": custom_id}

        response = requests.get(f"{deployed_api_url}/hello", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

        data = response.json()
        assert data["request_id"] == custom_id

    def test_deployed_error_monitoring(self, deployed_api_url):
        """Test error monitoring on deployed API"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        # Test 400 error
        response = requests.get(f"{deployed_api_url}/echo")  # Missing msg parameter

        assert response.status_code == 400
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = response.json()
        assert data["error"] == "Parameter 'msg' is required"
        assert data["request_id"] == response.headers["X-Request-ID"]

        # Test 404 error
        response = requests.get(f"{deployed_api_url}/nonexistent")

        assert response.status_code == 404
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

        data = response.json()
        assert data["error"] == "Endpoint not found"
        assert data["request_id"] == response.headers["X-Request-ID"]


class TestDeployedPerformance:
    """Test performance monitoring on deployed API"""

    def test_deployed_response_times(self, deployed_api_url):
        """Test response times are within acceptable limits"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        endpoints = ["/hello", "/echo?msg=performance_test", "/health"]
        response_times = []

        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{deployed_api_url}{endpoint}")
            end_time = time.time()

            assert response.status_code == 200

            actual_time = (end_time - start_time) * 1000  # Convert to ms
            header_time = float(response.headers["X-Response-Time"])

            response_times.append(
                {
                    "endpoint": endpoint,
                    "actual_time": actual_time,
                    "header_time": header_time,
                }
            )

        # Log response times for analysis
        print("\nResponse Times:")
        for rt in response_times:
            print(
                f"  {rt['endpoint']}: {rt['actual_time']:.2f}ms (header: {rt['header_time']:.2f}ms)"
            )

        # Verify reasonable response times (allowing for cold starts)
        for rt in response_times:
            assert (
                rt["actual_time"] <= 30000
            ), f"Response time too high for {rt['endpoint']}: {rt['actual_time']}ms"
            assert rt["header_time"] > 0, f"Invalid header time for {rt['endpoint']}"

    def test_deployed_concurrent_requests(self, deployed_api_url):
        """Test concurrent request handling on deployed API"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        import concurrent.futures

        def make_request(i):
            custom_id = f"concurrent-{i}-{int(time.time())}"
            headers = {"X-Request-ID": custom_id}

            response = requests.get(f"{deployed_api_url}/hello", headers=headers)

            return {
                "status_code": response.status_code,
                "request_id": response.headers.get("X-Request-ID"),
                "response_time": float(response.headers.get("X-Response-Time", 0)),
                "expected_id": custom_id,
            }

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # Verify all requests succeeded
        for result in results:
            assert result["status_code"] == 200
            assert result["request_id"] == result["expected_id"]
            assert result["response_time"] > 0

        # Verify request IDs are unique
        request_ids = [result["request_id"] for result in results]
        assert len(set(request_ids)) == len(request_ids)


class TestDeployedHealthChecks:
    """Test health check functionality on deployed API"""

    def test_deployed_health_check_consistency(self, deployed_api_url):
        """Test health check consistency on deployed API"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        responses = []

        # Make multiple health check requests
        for i in range(5):
            response = requests.get(f"{deployed_api_url}/health")
            assert response.status_code == 200

            data = response.json()
            responses.append(data)

            time.sleep(0.5)  # Small delay between requests

        # Verify consistent health status
        for data in responses:
            assert data["status"] == "healthy"
            assert data["version"] == "1.0.0"

            # Verify all checks are OK
            for check_name, check_status in data["checks"].items():
                assert check_status == "ok"

        # Verify uptime is increasing (if available)
        uptimes = [data.get("uptime_seconds", 0) for data in responses]
        if all(uptime > 0 for uptime in uptimes):
            # Uptime should be non-decreasing
            for i in range(1, len(uptimes)):
                assert uptimes[i] >= uptimes[i - 1], "Uptime should not decrease"

    def test_deployed_health_check_metrics(self, deployed_api_url):
        """Test health check includes system metrics on deployed API"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        response = requests.get(f"{deployed_api_url}/health")

        assert response.status_code == 200

        data = response.json()

        # Check if metrics are available
        if "metrics" in data:
            metrics = data["metrics"]

            # If system metrics are available, verify they're reasonable
            if "memory_usage_mb" in metrics:
                assert metrics["memory_usage_mb"] > 0
                assert metrics["memory_usage_mb"] < 1000  # Should be less than 1GB

            if "cpu_percent" in metrics:
                assert 0 <= metrics["cpu_percent"] <= 100

            if "open_files" in metrics:
                assert metrics["open_files"] >= 0


class TestDeployedLogging:
    """Test logging functionality on deployed API (indirect tests)"""

    def test_deployed_structured_responses(self, deployed_api_url):
        """Test that deployed API returns properly structured responses"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        endpoints_and_expected = [
            ("/hello", {"message": "Hello World", "version": "1.0.0"}),
            ("/echo?msg=test", {"message": "test", "echo": True}),
            ("/health", {"status": "healthy", "version": "1.0.0"}),
        ]

        for endpoint, expected_fields in endpoints_and_expected:
            response = requests.get(f"{deployed_api_url}{endpoint}")

            assert response.status_code == 200

            data = response.json()

            # Verify expected fields are present
            for field, expected_value in expected_fields.items():
                assert field in data
                if expected_value is not None:
                    assert data[field] == expected_value

            # Verify common monitoring fields
            assert "timestamp" in data
            assert "request_id" in data

            # Verify timestamp format
            timestamp = data["timestamp"]
            assert timestamp.endswith("Z")  # Should be UTC
            assert "T" in timestamp  # Should be ISO format

    def test_deployed_error_response_structure(self, deployed_api_url):
        """Test that deployed API returns properly structured error responses"""
        if not deployed_api_url:
            pytest.skip("No deployed API URL provided")

        error_cases = [
            ("/echo", 400, "Parameter 'msg' is required"),
            ("/nonexistent", 404, "Endpoint not found"),
        ]

        for endpoint, expected_status, expected_error in error_cases:
            response = requests.get(f"{deployed_api_url}{endpoint}")

            assert response.status_code == expected_status

            data = response.json()

            # Verify error response structure
            assert "error" in data
            assert "status_code" in data
            assert "timestamp" in data
            assert "request_id" in data

            assert data["error"] == expected_error
            assert data["status_code"] == expected_status
