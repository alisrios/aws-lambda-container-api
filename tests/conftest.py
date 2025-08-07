"""
Pytest configuration and shared fixtures
Global test configuration for AWS Lambda Container API tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add src directory to Python path for all tests
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    # Set environment variables for testing
    os.environ['TESTING'] = 'true'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    yield
    
    # Cleanup after tests
    if 'TESTING' in os.environ:
        del os.environ['TESTING']

@pytest.fixture
def sample_api_gateway_event():
    """Sample API Gateway event for testing"""
    return {
        'httpMethod': 'GET',
        'path': '/hello',
        'queryStringParameters': {},
        'headers': {
            'Content-Type': 'application/json',
            'User-Agent': 'test-agent'
        },
        'body': None,
        'isBase64Encoded': False,
        'requestContext': {
            'requestId': 'test-request-id',
            'stage': 'test'
        }
    }

@pytest.fixture
def sample_lambda_context():
    """Sample Lambda context for testing"""
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-request-id-123'
            self.function_name = 'test-lambda-function'
            self.function_version = '1'
            self.memory_limit_in_mb = 512
            self.remaining_time_in_millis = lambda: 30000
    
    return MockContext()

# Pytest markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)