# Test Suite Documentation

## Overview

This test suite provides comprehensive testing for the AWS Lambda Container API project, covering unit tests, integration tests, and code coverage reporting.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_app.py         # Flask application unit tests
│   └── test_lambda_handler.py  # Lambda handler unit tests
├── integration/            # Integration tests for complete workflows
│   └── test_api_endpoints.py   # API endpoint integration tests
├── conftest.py            # Shared test configuration and fixtures
└── README.md              # This documentation
```

## Test Categories

### Unit Tests (`tests/unit/`)

**Flask Application Tests (`test_app.py`)**
- Tests individual Flask endpoints (`/hello`, `/echo`)
- Validates request/response formats
- Tests error handling and edge cases
- Verifies logging functionality
- Tests HTTP status codes and headers

**Lambda Handler Tests (`test_lambda_handler.py`)**
- Tests AWS Lambda integration
- Validates API Gateway event processing
- Tests CORS header configuration
- Verifies error handling in Lambda context
- Tests different event formats (REST API vs HTTP API)

### Integration Tests (`tests/integration/`)

**API Endpoints Integration (`test_api_endpoints.py`)**
- Tests complete request-response cycles
- Validates multiple consecutive requests
- Tests query parameter handling
- Verifies error scenarios end-to-end
- Tests Unicode and special character handling
- Validates JSON response consistency

## Running Tests

### Quick Test Run
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test categories
python -m pytest tests/unit/        # Unit tests only
python -m pytest tests/integration/ # Integration tests only
```

### Using Test Runner Script
```bash
# Comprehensive test run with coverage and quality checks
python run_tests.py
```

### Test Configuration

The test suite is configured via `pytest.ini`:
- **Coverage Target**: 85% minimum
- **Coverage Reports**: HTML (htmlcov/) and terminal
- **Test Discovery**: Automatic for `test_*.py` files
- **Output Format**: Verbose with short traceback

## Coverage Requirements

- **Minimum Coverage**: 85%
- **Current Coverage**: 87%
- **Coverage Reports**: 
  - HTML report: `htmlcov/index.html`
  - Terminal output with missing lines
  - XML report for CI/CD integration

## Test Requirements

The following requirements are validated by the test suite:

### Requirement 7.2 (Error Handling and Logging)
- ✅ Proper error handling in all endpoints
- ✅ Structured logging for debugging
- ✅ Appropriate HTTP status codes

### Requirement 7.4 (Testing and Validation)
- ✅ Unit tests for all Flask functions
- ✅ Integration tests for API endpoints
- ✅ Lambda handler testing
- ✅ Coverage reporting above 85%

## Test Fixtures and Utilities

### Shared Fixtures (`conftest.py`)
- `setup_test_environment`: Configures test environment variables
- `sample_api_gateway_event`: Mock API Gateway event for testing
- `sample_lambda_context`: Mock Lambda context for testing

### Test Utilities
- URL encoding helpers for special characters
- Mock context managers for error simulation
- Response validation helpers

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:
- Exit codes indicate test success/failure
- Coverage thresholds enforce quality gates
- XML coverage reports for CI integration
- Structured output for automated parsing

## Best Practices

1. **Test Isolation**: Each test is independent and can run in any order
2. **Mocking**: External dependencies are mocked appropriately
3. **Coverage**: All critical paths are tested
4. **Documentation**: Tests serve as living documentation
5. **Maintainability**: Tests are readable and well-organized

## Troubleshooting

### Common Issues

**Import Errors**: Ensure `src/` directory is in Python path
```bash
export PYTHONPATH="${PYTHONPATH}:./src"
```

**Coverage Issues**: Check that all source files are included
```bash
python -m pytest --cov=src --cov-report=term-missing
```

**Test Failures**: Run with verbose output for debugging
```bash
python -m pytest -v --tb=long
```

### Performance

- **Unit Tests**: ~2 seconds
- **Integration Tests**: ~3 seconds  
- **Full Suite**: ~6 seconds
- **Coverage Analysis**: Additional ~1 second

## Future Enhancements

- [ ] Performance/load testing
- [ ] Contract testing for API Gateway integration
- [ ] End-to-end tests with actual AWS resources
- [ ] Security testing for input validation
- [ ] Mutation testing for test quality validation