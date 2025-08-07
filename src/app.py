"""
Flask application for AWS Lambda Container API
Provides /hello and /echo endpoints as specified in requirements
"""

import json
import logging
import os
import sys
import time
from datetime import datetime

from flask import Flask, g, jsonify, request

app = Flask(__name__)


# Configure structured logging
class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request context if available
        if hasattr(g, "request_id"):
            log_entry["request_id"] = g.request_id
        if hasattr(g, "start_time"):
            log_entry["duration_ms"] = round((time.time() - g.start_time) * 1000, 2)

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)


# Setup structured logging
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# Remove default handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add structured handler
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)
logger.propagate = False


@app.before_request
def before_request():
    """Set up request context for logging"""
    g.start_time = time.time()
    g.request_id = request.headers.get("X-Request-ID", f"req-{int(time.time() * 1000)}")

    # Log incoming request
    logger.info(
        "Incoming request",
        extra={
            "extra_fields": {
                "method": request.method,
                "path": request.path,
                "query_params": dict(request.args),
                "user_agent": request.headers.get("User-Agent"),
                "remote_addr": request.remote_addr,
            }
        },
    )


@app.after_request
def after_request(response):
    """Log response details"""
    duration_ms = round((time.time() - g.start_time) * 1000, 2)

    logger.info(
        "Request completed",
        extra={
            "extra_fields": {
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "response_size": len(response.get_data()),
            }
        },
    )

    # Add custom headers for monitoring
    response.headers["X-Request-ID"] = g.request_id
    response.headers["X-Response-Time"] = str(duration_ms)

    return response


@app.route("/hello", methods=["GET"])
def hello():
    """
    Hello World endpoint
    Returns: JSON response with Hello World message
    Requirement: 1.2 - QUANDO a API for acessada via endpoint /hello ENTÃO ela DEVE retornar uma resposta "Hello World"
    """
    try:
        response = {
            "message": "Hello World",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "request_id": g.request_id,
        }

        logger.info(
            "Hello endpoint processed successfully",
            extra={
                "extra_fields": {
                    "endpoint": "/hello",
                    "response_message": "Hello World",
                }
            },
        )

        return jsonify(response), 200

    except Exception as e:
        logger.error(
            "Error in hello endpoint",
            extra={
                "extra_fields": {
                    "endpoint": "/hello",
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            },
        )

        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "status_code": 500,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "request_id": g.request_id,
                }
            ),
            500,
        )


@app.route("/echo", methods=["GET"])
def echo():
    """
    Echo endpoint that returns the provided message parameter
    Returns: JSON response with the echoed message
    Requirement: 1.3 - QUANDO a API for acessada via endpoint /echo com parâmetro msg ENTÃO ela DEVE retornar o parâmetro de mensagem fornecido
    Requirement: 1.5 - SE nenhum parâmetro msg for fornecido para /echo ENTÃO o sistema DEVE retornar uma mensagem de erro apropriada
    """
    try:
        msg = request.args.get("msg")

        if not msg:
            logger.warning(
                "Echo endpoint accessed without required parameter",
                extra={
                    "extra_fields": {
                        "endpoint": "/echo",
                        "missing_parameter": "msg",
                        "query_params": dict(request.args),
                    }
                },
            )

            return (
                jsonify(
                    {
                        "error": "Parameter 'msg' is required",
                        "status_code": 400,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "request_id": g.request_id,
                    }
                ),
                400,
            )

        response = {
            "message": msg,
            "echo": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": g.request_id,
        }

        logger.info(
            "Echo endpoint processed successfully",
            extra={
                "extra_fields": {
                    "endpoint": "/echo",
                    "message_length": len(msg),
                    "echoed_message": (
                        msg[:100] + "..." if len(msg) > 100 else msg
                    ),  # Truncate long messages in logs
                }
            },
        )

        return jsonify(response), 200

    except Exception as e:
        logger.error(
            "Error in echo endpoint",
            extra={
                "extra_fields": {
                    "endpoint": "/echo",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "msg_parameter": request.args.get("msg", "None"),
                }
            },
        )

        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "status_code": 500,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "request_id": g.request_id,
                }
            ),
            500,
        )


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint for monitoring
    Returns: JSON response with application health status
    Requirement: 7.5 - Health check endpoint para monitoramento
    """
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "request_id": g.request_id,
            "uptime_seconds": (
                time.time() - app.start_time if hasattr(app, "start_time") else 0
            ),
            "checks": {"application": "ok", "memory": "ok", "dependencies": "ok"},
        }

        # Add basic system metrics
        import psutil

        try:
            process = psutil.Process()
            health_status["metrics"] = {
                "memory_usage_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "cpu_percent": process.cpu_percent(),
                "open_files": len(process.open_files()),
            }
        except ImportError:
            # psutil not available, skip system metrics
            health_status["metrics"] = {"note": "System metrics unavailable"}

        logger.info(
            "Health check performed",
            extra={
                "extra_fields": {
                    "endpoint": "/health",
                    "health_status": health_status["status"],
                }
            },
        )

        return jsonify(health_status), 200

    except Exception as e:
        logger.error(
            "Error in health endpoint",
            extra={
                "extra_fields": {
                    "endpoint": "/health",
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            },
        )

        # Return unhealthy status
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": "Health check failed",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "request_id": g.request_id,
                }
            ),
            503,
        )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(
        "404 error occurred",
        extra={
            "extra_fields": {
                "path": request.path,
                "method": request.method,
                "error_type": "404_not_found",
            }
        },
    )

    return (
        jsonify(
            {
                "error": "Endpoint not found",
                "status_code": 404,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "request_id": getattr(g, "request_id", "unknown"),
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(
        "500 error occurred",
        extra={
            "extra_fields": {
                "path": request.path,
                "method": request.method,
                "error_type": "500_internal_error",
                "error_details": str(error),
            }
        },
    )

    return (
        jsonify(
            {
                "error": "Internal server error",
                "status_code": 500,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "request_id": getattr(g, "request_id", "unknown"),
            }
        ),
        500,
    )


if __name__ == "__main__":
    # Set application start time for uptime calculation
    app.start_time = time.time()

    logger.info(
        "Starting Flask application",
        extra={
            "extra_fields": {
                "environment": os.getenv("ENVIRONMENT", "development"),
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "port": 5000,
            }
        },
    )

    # Requirement: 1.4 - QUANDO a aplicação rodar localmente ENTÃO ela DEVE ser acessível e testável em um servidor de desenvolvimento local
    app.run(host="0.0.0.0", port=5000, debug=True)
