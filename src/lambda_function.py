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
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract HTTP method and path from API Gateway event
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        path = event.get('path', event.get('rawPath', '/'))
        query_params = event.get('queryStringParameters') or {}
        
        logger.info(f"Processing request: {http_method} {path}")
        
        # Handle different endpoints
        if path == '/hello' and http_method == 'GET':
            response_body = {
                'message': 'Hello World',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'version': '1.0.0'
            }
            status_code = 200
            
        elif path == '/echo' and http_method == 'GET':
            msg = query_params.get('msg')
            if not msg:
                response_body = {
                    'error': "Parameter 'msg' is required",
                    'status_code': 400,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                status_code = 400
            else:
                response_body = {
                    'message': msg,
                    'echo': True,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                status_code = 200
                
        elif path == '/health' and http_method == 'GET':
            response_body = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'version': '1.0.0',
                'environment': os.getenv('ENVIRONMENT', 'development')
            }
            status_code = 200
            
        else:
            response_body = {
                'error': 'Endpoint not found',
                'status_code': 404,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            status_code = 404
        
        logger.info(f"Returning response: {status_code}")
        
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps(response_body)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        }
