"""
Configuration for end-to-end tests
Provides fixtures and utilities for testing deployed API
"""

import json
import os
import subprocess

import boto3
import pytest
from botocore.exceptions import ClientError


@pytest.fixture(scope="session")
def terraform_outputs():
    """Get Terraform outputs for the deployed infrastructure"""
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd="terraform",
            capture_output=True,
            text=True,
            check=True,
        )
        outputs = json.loads(result.stdout)
        return outputs
    except subprocess.CalledProcessError as e:
        pytest.skip(f"Could not get Terraform outputs: {e}")
    except Exception as e:
        pytest.skip(f"Terraform outputs setup failed: {e}")


@pytest.fixture(scope="session")
def api_endpoints(terraform_outputs):
    """Extract API endpoint URLs from Terraform outputs"""
    return {
        "api_url": terraform_outputs["api_gateway_url"]["value"],
        "hello_url": terraform_outputs["hello_endpoint_url"]["value"],
        "echo_url": terraform_outputs["echo_endpoint_url"]["value"],
    }


@pytest.fixture(scope="session")
def lambda_info(terraform_outputs):
    """Extract Lambda function information from Terraform outputs"""
    return {
        "function_name": terraform_outputs["lambda_function_name"]["value"],
        "function_arn": terraform_outputs["lambda_function_arn"]["value"],
        "log_group": terraform_outputs["cloudwatch_log_group_name"]["value"],
    }


@pytest.fixture(scope="session")
def aws_clients():
    """Create AWS service clients for testing"""
    try:
        return {
            "cloudwatch_logs": boto3.client("logs"),
            "lambda": boto3.client("lambda"),
            "cloudwatch": boto3.client("cloudwatch"),
        }
    except Exception as e:
        pytest.skip(f"Could not create AWS clients: {e}")


@pytest.fixture
def test_timeout():
    """Default timeout for API requests"""
    return 30


@pytest.fixture
def performance_config():
    """Configuration for performance tests"""
    return {
        "concurrent_requests": 10,
        "sustained_duration": 30,
        "requests_per_second": 2,
        "max_response_time": 10.0,
        "min_success_rate": 95.0,
    }
