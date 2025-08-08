"""
AWS Lambda handler for Flask application
Integrates Flask app with AWS Lambda runtime
"""

import json
import logging
import os
import time
from datetime import datetime

from app import app


# Configure structured logging for Lambda
class LambdaStructuredFormatter(logging.Formatter):
    """Custom formatter for Lambda structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "aws_request_id": getattr(record, "aws_request_id", "unknown"),
            "function_name": os.getenv("AWS_LAMBDA_FUNCTION_NAME", "unknown"),
            "function_version": os.getenv("AWS_LAMBDA_FUNCTION_VERSION", "unknown"),
            "memory_limit": os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "unknown"),
        }

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)


# Setup Lambda logger
logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

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
        http_method = event.get(
            "httpMethod",
            event.get("requestContext", {}).get("http", {}).get("method", "GET"),
        )
        path = event.get("path", event.get("rawPath", "/"))
        query_params = event.get("queryStringParameters") or {}

        logger.info(f"Processing request: {http_method} {path}")

        # Use Flask test client to process the request
        with app.test_client() as client:
            # Convert Lambda event to Flask request
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url = f"{path}?{query_string}" if query_string else path
            
            # For Lambda integration, always use GET method to match Flask routes
            # This allows API Gateway to accept any method but Flask handles it as GET
            flask_response = client.get(url)
            
            status_code = flask_response.status_code
            try:
                response_body = flask_response.get_json()
            except:
                response_body = json.loads(flask_response.get_data(as_text=True))

        logger.info(f"Returning response: {status_code}")

        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps(response_body),
        }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "error": "Internal server error",
                    "status_code": 500,
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "request_id": context.aws_request_id if context else "unknown",
                }
            ),
        }
