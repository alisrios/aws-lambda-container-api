"""
Unit tests for monitoring and observability features
Tests structured logging, health endpoint, and monitoring functionality
"""

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from src.app import app


class TestStructuredLogging:
    """Test structured logging functionality"""

    def test_structured_logging_format(self, caplog):
        """Test that logs are formatted as structured JSON"""
        with app.test_client() as client:
            response = client.get("/hello")

            assert response.status_code == 200

            # Check that logs contain structured data
            log_records = [
                record for record in caplog.records if record.name == "src.app"
            ]
            assert len(log_records) > 0

            # Verify log contains expected fields
            for record in log_records:
                if hasattr(record, "extra_fields"):
                    assert (
                        "endpoint" in record.extra_fields
                        or "method" in record.extra_fields
                    )

    def test_request_id_generation(self):
        """Test that request IDs are generated and included in responses"""
        with app.test_client() as client:
            response = client.get("/hello")

            assert response.status_code == 200
            assert "X-Request-ID" in response.headers

            data = response.get_json()
            assert "request_id" in data
            assert data["request_id"] == response.headers["X-Request-ID"]

    def test_response_time_header(self):
        """Test that response time is included in headers"""
        with app.test_client() as client:
            response = client.get("/hello")

            assert response.status_code == 200
            assert "X-Response-Time" in response.headers

            # Response time should be a valid number
            response_time = float(response.headers["X-Response-Time"])
            assert response_time >= 0

    def test_custom_request_id_header(self):
        """Test that custom request ID from header is used"""
        custom_request_id = "test-request-123"

        with app.test_client() as client:
            response = client.get("/hello", headers={"X-Request-ID": custom_request_id})

            assert response.status_code == 200
            assert response.headers["X-Request-ID"] == custom_request_id

            data = response.get_json()
            assert data["request_id"] == custom_request_id


class TestHealthEndpoint:
    """Test health check endpoint functionality"""

    def test_health_endpoint_success(self):
        """Test health endpoint returns success status"""
        with app.test_client() as client:
            response = client.get("/health")

            assert response.status_code == 200

            data = response.get_json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "version" in data
            assert "environment" in data
            assert "request_id" in data
            assert "checks" in data

            # Verify checks structure
            checks = data["checks"]
            assert "application" in checks
            assert "memory" in checks
            assert "dependencies" in checks

    def test_health_endpoint_includes_uptime(self):
        """Test health endpoint includes uptime information"""
        # Set start time for the app
        app.start_time = time.time() - 10  # 10 seconds ago

        with app.test_client() as client:
            response = client.get("/health")

            assert response.status_code == 200

            data = response.get_json()
            assert "uptime_seconds" in data
            assert data["uptime_seconds"] >= 10

    @patch("psutil.Process")
    def test_health_endpoint_with_system_metrics(self, mock_process):
        """Test health endpoint includes system metrics when psutil is available"""
        # Mock psutil process
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value.rss = 50 * 1024 * 1024  # 50MB
        mock_process_instance.cpu_percent.return_value = 15.5
        mock_process_instance.open_files.return_value = []
        mock_process.return_value = mock_process_instance

        with app.test_client() as client:
            response = client.get("/health")

            assert response.status_code == 200

            data = response.get_json()
            assert "metrics" in data

            metrics = data["metrics"]
            assert "memory_usage_mb" in metrics
            assert "cpu_percent" in metrics
            assert "open_files" in metrics

            assert metrics["memory_usage_mb"] == 50.0
            assert metrics["cpu_percent"] == 15.5
            assert metrics["open_files"] == 0

    def test_health_endpoint_error_handling(self):
        """Test health endpoint handles errors gracefully"""
        with patch("src.app.time.time", side_effect=Exception("Time error")):
            with app.test_client() as client:
                response = client.get("/health")

                assert response.status_code == 503

                data = response.get_json()
                assert data["status"] == "unhealthy"
                assert "error" in data
                assert "timestamp" in data
                assert "request_id" in data


class TestErrorHandling:
    """Test error handling and logging"""

    def test_404_error_logging(self, caplog):
        """Test that 404 errors are properly logged"""
        with app.test_client() as client:
            response = client.get("/nonexistent")

            assert response.status_code == 404

            data = response.get_json()
            assert data["error"] == "Endpoint not found"
            assert data["status_code"] == 404
            assert "request_id" in data

            # Check logging
            log_records = [
                record for record in caplog.records if record.levelname == "WARNING"
            ]
            assert len(log_records) > 0

    def test_echo_endpoint_error_logging(self, caplog):
        """Test that echo endpoint errors are properly logged"""
        with app.test_client() as client:
            response = client.get("/echo")  # Missing msg parameter

            assert response.status_code == 400

            data = response.get_json()
            assert data["error"] == "Parameter 'msg' is required"
            assert "request_id" in data

            # Check warning log for missing parameter
            warning_records = [
                record for record in caplog.records if record.levelname == "WARNING"
            ]
            assert len(warning_records) > 0


class TestLoggingIntegration:
    """Test logging integration with Flask app"""

    def test_before_request_logging(self, caplog):
        """Test that incoming requests are logged"""
        with app.test_client() as client:
            response = client.get("/hello?test=value")

            assert response.status_code == 200

            # Check for incoming request log
            info_records = [
                record for record in caplog.records if record.levelname == "INFO"
            ]
            request_logs = [
                record
                for record in info_records
                if "Incoming request" in record.message
            ]

            assert len(request_logs) > 0

    def test_after_request_logging(self, caplog):
        """Test that completed requests are logged"""
        with app.test_client() as client:
            response = client.get("/hello")

            assert response.status_code == 200

            # Check for request completed log
            info_records = [
                record for record in caplog.records if record.levelname == "INFO"
            ]
            completion_logs = [
                record
                for record in info_records
                if "Request completed" in record.message
            ]

            assert len(completion_logs) > 0

    def test_endpoint_specific_logging(self, caplog):
        """Test that endpoints log specific information"""
        with app.test_client() as client:
            response = client.get("/echo?msg=test_message")

            assert response.status_code == 200

            # Check for endpoint-specific log
            info_records = [
                record for record in caplog.records if record.levelname == "INFO"
            ]
            endpoint_logs = [
                record
                for record in info_records
                if "Echo endpoint processed successfully" in record.message
            ]

            assert len(endpoint_logs) > 0
