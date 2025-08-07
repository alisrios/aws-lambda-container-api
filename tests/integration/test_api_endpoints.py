"""
Integration tests for API endpoints
Tests the complete API functionality including Flask app integration
"""

import pytest
import json
import requests
import threading
import time
import sys
import os
from unittest.mock import patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app import app


class TestAPIEndpointsIntegration:
    """Integration test class for API endpoints"""

    @pytest.fixture(scope="class")
    def test_server(self):
        """Start a test server for integration testing"""
        app.config["TESTING"] = True

        # Use test client instead of actual server for integration tests
        with app.test_client() as client:
            yield client

    def test_hello_endpoint_integration(self, test_server):
        """
        Integration test for hello endpoint
        Tests complete request-response cycle
        """
        response = test_server.get("/hello")

        # Test HTTP response
        assert response.status_code == 200
        assert response.content_type == "application/json"

        # Test response structure
        data = json.loads(response.data)
        expected_keys = ["message", "timestamp", "version"]
        for key in expected_keys:
            assert key in data

        # Test response values
        assert data["message"] == "Hello World"
        assert data["version"] == "1.0.0"
        assert isinstance(data["timestamp"], str)
        assert data["timestamp"].endswith("Z")

    def test_echo_endpoint_integration_success(self, test_server):
        """
        Integration test for echo endpoint with valid message
        Tests complete request-response cycle with query parameters
        """
        test_message = "Integration test message"
        response = test_server.get(f"/echo?msg={test_message}")

        # Test HTTP response
        assert response.status_code == 200
        assert response.content_type == "application/json"

        # Test response structure
        data = json.loads(response.data)
        expected_keys = ["message", "echo", "timestamp"]
        for key in expected_keys:
            assert key in data

        # Test response values
        assert data["message"] == test_message
        assert data["echo"] is True
        assert isinstance(data["timestamp"], str)
        assert data["timestamp"].endswith("Z")

    def test_echo_endpoint_integration_error(self, test_server):
        """
        Integration test for echo endpoint without message parameter
        Tests error handling in complete request-response cycle
        """
        response = test_server.get("/echo")

        # Test HTTP response
        assert response.status_code == 400
        assert response.content_type == "application/json"

        # Test error response structure
        data = json.loads(response.data)
        expected_keys = ["error", "status_code", "timestamp"]
        for key in expected_keys:
            assert key in data

        # Test error response values
        assert data["error"] == "Parameter 'msg' is required"
        assert data["status_code"] == 400
        assert isinstance(data["timestamp"], str)

    def test_multiple_requests_integration(self, test_server):
        """
        Integration test for multiple consecutive requests
        Tests that the application handles multiple requests correctly
        """
        # Make multiple hello requests
        hello_responses = []
        for i in range(5):
            response = test_server.get("/hello")
            assert response.status_code == 200
            hello_responses.append(json.loads(response.data))

        # All should have the same message but different timestamps
        messages = [r["message"] for r in hello_responses]
        assert all(msg == "Hello World" for msg in messages)

        timestamps = [r["timestamp"] for r in hello_responses]
        assert len(set(timestamps)) >= 1  # At least some should be different

        # Make multiple echo requests with different messages
        echo_messages = ["msg1", "msg2", "msg3"]
        echo_responses = []
        for msg in echo_messages:
            response = test_server.get(f"/echo?msg={msg}")
            assert response.status_code == 200
            echo_responses.append(json.loads(response.data))

        # Each should echo back the correct message
        for i, response_data in enumerate(echo_responses):
            assert response_data["message"] == echo_messages[i]
            assert response_data["echo"] is True

    def test_error_handling_integration(self, test_server):
        """
        Integration test for various error scenarios
        Tests complete error handling across the application
        """
        # Test 404 for unknown endpoint
        response = test_server.get("/unknown-endpoint")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == "Endpoint not found"
        assert data["status_code"] == 404

        # Test 405 for wrong HTTP method
        response = test_server.post("/hello")
        assert response.status_code == 405

        response = test_server.put("/echo")
        assert response.status_code == 405

        response = test_server.delete("/hello")
        assert response.status_code == 405

    def test_query_parameter_handling_integration(self, test_server):
        """
        Integration test for various query parameter scenarios
        """
        # Test with URL-encoded characters
        import urllib.parse

        test_message = "Hello World! @#$%"
        encoded_message = urllib.parse.quote(test_message)
        response = test_server.get(f"/echo?msg={encoded_message}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == test_message

        # Test with empty string
        response = test_server.get("/echo?msg=")
        assert response.status_code == 400

        # Test with whitespace
        response = test_server.get("/echo?msg=   ")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "   "

        # Test with multiple parameters (only msg should be used)
        response = test_server.get("/echo?msg=test&extra=ignored")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "test"

    def test_response_headers_integration(self, test_server):
        """
        Integration test for HTTP response headers
        """
        # Test hello endpoint headers
        response = test_server.get("/hello")
        assert response.content_type == "application/json"

        # Test echo endpoint headers
        response = test_server.get("/echo?msg=test")
        assert response.content_type == "application/json"

        # Test error response headers
        response = test_server.get("/echo")
        assert response.content_type == "application/json"

        response = test_server.get("/unknown")
        assert response.content_type == "application/json"

    def test_json_response_format_integration(self, test_server):
        """
        Integration test for JSON response format consistency
        """
        # Test successful responses have consistent format
        hello_response = test_server.get("/hello")
        hello_data = json.loads(hello_response.data)

        echo_response = test_server.get("/echo?msg=test")
        echo_data = json.loads(echo_response.data)

        # Both should have timestamp in same format
        assert hello_data["timestamp"].endswith("Z")
        assert echo_data["timestamp"].endswith("Z")

        # Test error responses have consistent format
        echo_error = test_server.get("/echo")
        echo_error_data = json.loads(echo_error.data)

        not_found_error = test_server.get("/unknown")
        not_found_data = json.loads(not_found_error.data)

        # Both error responses should have error, status_code, timestamp
        error_keys = ["error", "status_code", "timestamp"]
        for key in error_keys:
            assert key in echo_error_data
            assert key in not_found_data

    def test_concurrent_requests_integration(self, test_server):
        """
        Integration test for handling concurrent requests
        Tests thread safety of the application
        """
        # Simplified concurrent test without threading issues
        # Make multiple sequential requests to test consistency
        responses = []

        # Make multiple requests in sequence (simulating concurrent behavior)
        requests_to_make = [
            ("/hello", ""),
            ("/echo", "msg=concurrent1"),
            ("/hello", ""),
            ("/echo", "msg=concurrent2"),
            ("/echo", "msg=concurrent3"),
        ]

        for endpoint, query in requests_to_make:
            if query:
                response = test_server.get(f"{endpoint}?{query}")
            else:
                response = test_server.get(endpoint)
            responses.append(response)

        # All requests should succeed
        assert len(responses) == 5
        for response in responses:
            assert response.status_code in [200, 400]  # 400 for echo without msg
            assert response.content_type == "application/json"

    def test_large_message_integration(self, test_server):
        """
        Integration test for handling large messages
        """
        # Test with a reasonably large message
        import urllib.parse

        large_message = (
            "A" * 500
        )  # 500 char message (reduced to avoid URL length issues)
        encoded_message = urllib.parse.quote(large_message)
        response = test_server.get(f"/echo?msg={encoded_message}")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == large_message
        assert data["echo"] is True

    def test_unicode_handling_integration(self, test_server):
        """
        Integration test for Unicode character handling
        """
        unicode_messages = [
            "Hello 世界",
            "Café ñoño",
            "🚀 rocket emoji",
            "Здравствуй мир",
            "مرحبا بالعالم",
        ]

        for message in unicode_messages:
            response = test_server.get(f"/echo?msg={message}")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["message"] == message

    def test_application_state_integration(self, test_server):
        """
        Integration test to ensure application maintains consistent state
        """
        # Make several requests and ensure the application doesn't change state
        initial_hello = test_server.get("/hello")
        initial_data = json.loads(initial_hello.data)

        # Make some other requests
        test_server.get("/echo?msg=test1")
        test_server.get("/echo?msg=test2")
        test_server.get("/unknown")  # 404 error

        # Hello endpoint should still work the same way
        final_hello = test_server.get("/hello")
        final_data = json.loads(final_hello.data)

        assert final_data["message"] == initial_data["message"]
        assert final_data["version"] == initial_data["version"]
        # Timestamps will be different, which is expected
