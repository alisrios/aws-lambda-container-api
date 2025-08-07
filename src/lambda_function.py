"""
AWS Lambda handler for Flask application
Integrates Flask app with AWS Lambda runtime
"""
import json
import logging
import time
import os
from datetime import datetime
from app import app

# Configure structured logging for Lambda
class LambdaStructuredFormatter(logging.Formatter):
    """Custom formatter for Lambda structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'aws_request_id': getattr(record, 'aws_request_id', 'unknown'),
            'function_name': os.getenv('AWS_LAMBDA_FUNCTION_NAME', 'unknown'),
            'function_version': os.getenv('AWS_LAMBDA_FUNCTION_VERSION', 'unknown'),
            'memory_limit': os.getenv('AWS_LAMBDA_FUNCTION_MEMORY_SIZE', 'unknown')
        }
        
        # Add extra fields from record
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
            
        return json.dumps(log_entry)

# Setup Lambda logger
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

# Remove existing handlers and add structured handler
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

handler = logging.StreamHandler()
handler.setFormatter(LambdaStructuredFormatter())
logger.addHandler(handler)

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    Processes API Gateway events and returns responses
    
    Args:
        event: API Gateway event
        context: Lambda context object
        
    Returns:
        dict: API Gateway response format
    """
    start_time = time.time()
    request_id = context.aws_request_id if context else f"lambda-{int(time.time() * 1000)}"
    
    try:
        # Extract HTTP method and path
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        path = event.get('path', event.get('rawPath', '/'))
        query_params = event.get('queryStringParameters') or {}
        
        # Log incoming request with structured data
        logger.info("Lambda handler invoked", extra={
            'extra_fields': {
                'aws_request_id': request_id,
                'http_method': http_method,
                'path': path,
                'query_params': query_params,
                'source_ip': event.get('requestContext', {}).get('identity', {}).get('sourceIp'),
                'user_agent': event.get('requestContext', {}).get('identity', {}).get('userAgent'),
                'remaining_time_ms': context.get_remaining_time_in_millis() if context else 0
            }
        })
        
        # Create a test client for the Flask app
        with app.test_client() as client:
            # Add request ID header for Flask app
            headers = {'X-Request-ID': request_id}
            
            # Handle different endpoints
            if path == '/hello' and http_method == 'GET':
                response = client.get('/hello', headers=headers)
            elif path == '/echo' and http_method == 'GET':
                # Build query string
                query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
                url = f'/echo?{query_string}' if query_string else '/echo'
                response = client.get(url, headers=headers)
            elif path == '/health' and http_method == 'GET':
                response = client.get('/health', headers=headers)
            else:
                # Handle unknown paths
                response = client.get(path, headers=headers)
            
            # Calculate processing time
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Convert Flask response to API Gateway format
            api_response = {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'X-Request-ID': request_id,
                    'X-Response-Time': str(duration_ms)
                },
                'body': response.get_data(as_text=True)
            }
            
            # Log successful response
            logger.info("Lambda handler completed successfully", extra={
                'extra_fields': {
                    'aws_request_id': request_id,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'response_size': len(api_response['body']),
                    'memory_used_mb': context.memory_limit_in_mb if context else 0
                }
            })
            
            return api_response
            
    except Exception as e:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        # Log error with structured data
        logger.error("Error in lambda_handler", extra={
            'extra_fields': {
                'aws_request_id': request_id,
                'error': str(e),
                'error_type': type(e).__name__,
                'duration_ms': duration_ms,
                'path': event.get('path', 'unknown'),
                'method': event.get('httpMethod', 'unknown')
            }
        })
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-Request-ID': request_id,
                'X-Response-Time': str(duration_ms)
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'status_code': 500,
                'request_id': request_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        }