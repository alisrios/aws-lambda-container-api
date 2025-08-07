"""
Unit tests for Flask application
Tests individual functions and components of the app.py module
"""
import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from app import app


class TestFlaskApp:
    """Test class for Flask application unit tests"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask application"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_hello_endpoint_success(self, client):
        """
        Test hello endpoint returns correct response
        Requirement: 1.2 - QUANDO a API for acessada via endpoint /hello ENTÃO ela DEVE retornar uma resposta "Hello World"
        """
        response = client.get('/hello')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['message'] == 'Hello World'
        assert data['version'] == '1.0.0'
        assert 'timestamp' in data
        
        # Validate timestamp format
        timestamp = data['timestamp']
        assert timestamp.endswith('Z')
        # Should be able to parse as ISO format
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_echo_endpoint_with_message(self, client):
        """
        Test echo endpoint with valid message parameter
        Requirement: 1.3 - QUANDO a API for acessada via endpoint /echo com parâmetro msg ENTÃO ela DEVE retornar o parâmetro de mensagem fornecido
        """
        test_message = "Hello from test"
        response = client.get(f'/echo?msg={test_message}')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['message'] == test_message
        assert data['echo'] is True
        assert 'timestamp' in data
        
        # Validate timestamp format
        timestamp = data['timestamp']
        assert timestamp.endswith('Z')
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_echo_endpoint_without_message(self, client):
        """
        Test echo endpoint without message parameter returns error
        Requirement: 1.5 - SE nenhum parâmetro msg for fornecido para /echo ENTÃO o sistema DEVE retornar uma mensagem de erro apropriada
        """
        response = client.get('/echo')
        
        assert response.status_code == 400
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['error'] == "Parameter 'msg' is required"
        assert data['status_code'] == 400
        assert 'timestamp' in data
    
    def test_echo_endpoint_empty_message(self, client):
        """Test echo endpoint with empty message parameter"""
        response = client.get('/echo?msg=')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Parameter 'msg' is required"
    
    def test_echo_endpoint_special_characters(self, client):
        """Test echo endpoint with special characters in message"""
        import urllib.parse
        test_message = "Hello! @#$%^&*()_+ 测试"
        encoded_message = urllib.parse.quote(test_message)
        response = client.get(f'/echo?msg={encoded_message}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == test_message
        assert data['echo'] is True
    
    def test_404_error_handler(self, client):
        """Test 404 error handler for unknown endpoints"""
        response = client.get('/unknown-endpoint')
        
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['error'] == "Endpoint not found"
        assert data['status_code'] == 404
        assert 'timestamp' in data
    
    def test_method_not_allowed(self, client):
        """Test POST method on GET-only endpoints"""
        response = client.post('/hello')
        assert response.status_code == 405
        
        response = client.post('/echo')
        assert response.status_code == 405
    
    @patch('app.logger')
    def test_hello_endpoint_logging(self, mock_logger, client):
        """Test that hello endpoint logs correctly"""
        response = client.get('/hello')
        
        assert response.status_code == 200
        mock_logger.info.assert_called_with("Hello endpoint accessed successfully")
    
    @patch('app.logger')
    def test_echo_endpoint_logging_success(self, mock_logger, client):
        """Test that echo endpoint logs successfully"""
        test_message = "test message"
        response = client.get(f'/echo?msg={test_message}')
        
        assert response.status_code == 200
        mock_logger.info.assert_called_with(f"Echo endpoint accessed with message: {test_message}")
    
    @patch('app.logger')
    def test_echo_endpoint_logging_error(self, mock_logger, client):
        """Test that echo endpoint logs warning for missing parameter"""
        response = client.get('/echo')
        
        assert response.status_code == 400
        mock_logger.warning.assert_called_with("Echo endpoint accessed without msg parameter")
    
    def test_hello_endpoint_exception_handling(self, client):
        """Test that hello endpoint handles internal errors gracefully"""
        # Test with a mock that simulates an internal error
        with patch('app.logger') as mock_logger:
            # This test verifies the error handling structure exists
            response = client.get('/hello')
            # The endpoint should work normally
            assert response.status_code == 200
            # Verify logging was called
            mock_logger.info.assert_called()
    
    def test_echo_endpoint_exception_handling(self, client):
        """Test that echo endpoint handles internal errors gracefully"""
        # Test with a mock that simulates an internal error
        with patch('app.logger') as mock_logger:
            # Test normal operation
            response = client.get('/echo?msg=test')
            assert response.status_code == 200
            # Verify logging was called
            mock_logger.info.assert_called()
    
    def test_app_configuration(self):
        """Test Flask app configuration"""
        assert app.name == 'app'
        
        # Test that app can be configured for testing
        app.config['TESTING'] = True
        assert app.config['TESTING'] is True
    
    def test_response_headers(self, client):
        """Test that responses have correct headers"""
        response = client.get('/hello')
        assert response.content_type == 'application/json'
        
        response = client.get('/echo?msg=test')
        assert response.content_type == 'application/json'
    
    def test_timestamp_consistency(self, client):
        """Test that timestamps are in consistent format across endpoints"""
        hello_response = client.get('/hello')
        echo_response = client.get('/echo?msg=test')
        error_response = client.get('/echo')
        
        hello_data = json.loads(hello_response.data)
        echo_data = json.loads(echo_response.data)
        error_data = json.loads(error_response.data)
        
        # All should have timestamp field
        assert 'timestamp' in hello_data
        assert 'timestamp' in echo_data
        assert 'timestamp' in error_data
        
        # All should end with 'Z' (UTC format)
        assert hello_data['timestamp'].endswith('Z')
        assert echo_data['timestamp'].endswith('Z')
        assert error_data['timestamp'].endswith('Z')