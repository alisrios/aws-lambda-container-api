"""
Unit tests for AWS Lambda handler
Tests the lambda_function.py module and its integration with Flask app
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lambda_function import lambda_handler


class TestLambdaHandler:
    """Test class for Lambda handler unit tests"""
    
    def create_api_gateway_event(self, http_method='GET', path='/', query_params=None):
        """Helper method to create API Gateway event"""
        event = {
            'httpMethod': http_method,
            'path': path,
            'queryStringParameters': query_params or {},
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': None,
            'isBase64Encoded': False
        }
        return event
    
    def create_lambda_context(self):
        """Helper method to create Lambda context"""
        context = MagicMock()
        context.aws_request_id = 'test-request-id-123'
        context.function_name = 'test-lambda-function'
        context.function_version = '1'
        context.memory_limit_in_mb = 512
        return context
    
    def test_lambda_handler_hello_endpoint(self):
        """Test Lambda handler with hello endpoint"""
        event = self.create_api_gateway_event(path='/hello')
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        assert 'Content-Type' in response['headers']
        assert response['headers']['Content-Type'] == 'application/json'
        assert 'Access-Control-Allow-Origin' in response['headers']
        
        body_data = json.loads(response['body'])
        assert body_data['message'] == 'Hello World'
        assert body_data['version'] == '1.0.0'
        assert 'timestamp' in body_data
    
    def test_lambda_handler_echo_endpoint_with_message(self):
        """Test Lambda handler with echo endpoint and message"""
        event = self.create_api_gateway_event(
            path='/echo',
            query_params={'msg': 'Hello Lambda'}
        )
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'application/json'
        
        body_data = json.loads(response['body'])
        assert body_data['message'] == 'Hello Lambda'
        assert body_data['echo'] is True
        assert 'timestamp' in body_data
    
    def test_lambda_handler_echo_endpoint_without_message(self):
        """Test Lambda handler with echo endpoint without message"""
        event = self.create_api_gateway_event(path='/echo')
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        assert response['headers']['Content-Type'] == 'application/json'
        
        body_data = json.loads(response['body'])
        assert body_data['error'] == "Parameter 'msg' is required"
        assert body_data['status_code'] == 400
    
    def test_lambda_handler_unknown_endpoint(self):
        """Test Lambda handler with unknown endpoint"""
        event = self.create_api_gateway_event(path='/unknown')
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 404
        assert response['headers']['Content-Type'] == 'application/json'
        
        body_data = json.loads(response['body'])
        assert body_data['error'] == "Endpoint not found"
        assert body_data['status_code'] == 404
    
    def test_lambda_handler_cors_headers(self):
        """Test that Lambda handler includes CORS headers"""
        event = self.create_api_gateway_event(path='/hello')
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        headers = response['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Access-Control-Allow-Methods'] == 'GET, POST, OPTIONS'
        assert headers['Access-Control-Allow-Headers'] == 'Content-Type'
    
    def test_lambda_handler_with_http_api_format(self):
        """Test Lambda handler with HTTP API event format (API Gateway v2)"""
        event = {
            'requestContext': {
                'http': {
                    'method': 'GET'
                }
            },
            'rawPath': '/hello',
            'queryStringParameters': {}
        }
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        body_data = json.loads(response['body'])
        assert body_data['message'] == 'Hello World'
    
    def test_lambda_handler_with_multiple_query_params(self):
        """Test Lambda handler with multiple query parameters"""
        event = self.create_api_gateway_event(
            path='/echo',
            query_params={'msg': 'test message', 'extra': 'ignored'}
        )
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        body_data = json.loads(response['body'])
        assert body_data['message'] == 'test message'
    
    def test_lambda_handler_with_none_query_params(self):
        """Test Lambda handler when queryStringParameters is None"""
        event = self.create_api_gateway_event(path='/echo')
        event['queryStringParameters'] = None
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body_data = json.loads(response['body'])
        assert body_data['error'] == "Parameter 'msg' is required"
    
    @patch('lambda_function.logger')
    def test_lambda_handler_logging(self, mock_logger):
        """Test that Lambda handler logs events and responses"""
        event = self.create_api_gateway_event(path='/hello')
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        # Should log the incoming event
        mock_logger.info.assert_any_call(f"Received event: {json.dumps(event)}")
        
        # Should log the response
        assert mock_logger.info.call_count >= 2
    
    @patch('lambda_function.app')
    def test_lambda_handler_exception_handling(self, mock_app):
        """Test Lambda handler exception handling"""
        # Mock app.test_client to raise an exception
        mock_app.test_client.side_effect = Exception("Test exception")
        
        event = self.create_api_gateway_event(path='/hello')
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 500
        assert response['headers']['Content-Type'] == 'application/json'
        
        body_data = json.loads(response['body'])
        assert body_data['error'] == 'Internal server error'
        assert body_data['status_code'] == 500
        assert body_data['request_id'] == 'test-request-id-123'
    
    def test_lambda_handler_exception_without_context(self):
        """Test Lambda handler exception handling without context"""
        event = self.create_api_gateway_event(path='/hello')
        
        # Mock to cause an exception
        with patch('lambda_function.app') as mock_app:
            mock_app.test_client.side_effect = Exception("Test exception")
            
            response = lambda_handler(event, None)
            
            assert response['statusCode'] == 500
            body_data = json.loads(response['body'])
            assert body_data['request_id'] == 'unknown'
    
    def test_lambda_handler_post_method(self):
        """Test Lambda handler with POST method"""
        event = self.create_api_gateway_event(http_method='POST', path='/hello')
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        # The Lambda handler currently doesn't check HTTP method, so it will work
        # This is actually correct behavior for API Gateway integration
        assert response['statusCode'] == 200
        body_data = json.loads(response['body'])
        assert body_data['message'] == 'Hello World'
    
    def test_lambda_handler_missing_path(self):
        """Test Lambda handler with missing path in event"""
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {}
        }
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        # Should default to '/' path and return 404
        assert response['statusCode'] == 404
    
    def test_lambda_handler_missing_method(self):
        """Test Lambda handler with missing HTTP method in event"""
        event = {
            'path': '/hello',
            'queryStringParameters': {}
        }
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        # Should default to 'GET' method
        assert response['statusCode'] == 200
        body_data = json.loads(response['body'])
        assert body_data['message'] == 'Hello World'
    
    def test_response_format_compliance(self):
        """Test that response format complies with API Gateway requirements"""
        event = self.create_api_gateway_event(path='/hello')
        context = self.create_lambda_context()
        
        response = lambda_handler(event, context)
        
        # Check required fields for API Gateway response
        required_fields = ['statusCode', 'headers', 'body']
        for field in required_fields:
            assert field in response
        
        # Check that statusCode is an integer
        assert isinstance(response['statusCode'], int)
        
        # Check that headers is a dictionary
        assert isinstance(response['headers'], dict)
        
        # Check that body is a string
        assert isinstance(response['body'], str)
        
        # Check that body contains valid JSON
        json.loads(response['body'])  # Should not raise an exception