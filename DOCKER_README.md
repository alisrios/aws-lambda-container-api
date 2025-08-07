# Docker Container for AWS Lambda

This document describes the Docker container configuration for the AWS Lambda Container API project.

## Overview

The Dockerfile creates an optimized container image for AWS Lambda using the official AWS Lambda Python runtime. It implements multi-stage build, security best practices, and health checks.

## Container Features

### ✅ Multi-Stage Build
- **Builder stage**: Installs dependencies in isolation
- **Runtime stage**: Copies only necessary files for minimal image size
- **Optimization**: Reduces final image size and attack surface

### ✅ AWS Lambda Compatibility
- Uses official `public.ecr.aws/lambda/python:3.11` base image
- Configured with proper Lambda handler: `lambda_function.lambda_handler`
- Environment variables optimized for Lambda runtime

### ✅ Security Configuration
- Creates non-root user (`appuser`) for better security posture
- Proper file permissions (755) for application files
- Minimal dependencies and clean build process

### ✅ Health Check
- Built-in health check validates container functionality
- Tests Python import and basic application health
- Configurable intervals and retry logic

## File Structure

```
├── Dockerfile              # Multi-stage container definition
├── .dockerignore           # Build context optimization
├── validate_dockerfile.py  # Dockerfile validation script
├── test_container.py       # Container testing script (requires Docker)
├── test_lambda_import.py   # Lambda function validation
└── DOCKER_README.md        # This documentation
```

## Building the Container

### Prerequisites
- Docker installed and running
- AWS CLI configured (for ECR push)
- Application files in `src/` directory

### Build Command
```bash
# Build the container image
docker build -t lambda-container-api .

# Build with specific tag
docker build -t lambda-container-api:v1.0.0 .
```

## Testing the Container

### 1. Validate Configuration (No Docker Required)
```bash
# Validate Dockerfile structure and best practices
python validate_dockerfile.py

# Test Lambda function imports and execution
python test_lambda_import.py
```

### 2. Full Container Testing (Requires Docker)
```bash
# Run comprehensive container tests
python test_container.py
```

### 3. Manual Testing
```bash
# Test container health check
docker run --rm lambda-container-api python -c "import app; print('Health check passed')"

# Test Lambda handler directly
docker run --rm lambda-container-api python -c "
from lambda_function import lambda_handler
import json

event = {'httpMethod': 'GET', 'path': '/hello', 'queryStringParameters': None}
context = type('Context', (), {'aws_request_id': 'test-123'})()
response = lambda_handler(event, context)
print(json.dumps(response, indent=2))
"
```

## Container Specifications

### Base Image
- **Image**: `public.ecr.aws/lambda/python:3.11`
- **Architecture**: x86_64
- **Runtime**: Python 3.11

### Environment Variables
- `PYTHONPATH`: Set to Lambda task root
- `LOG_LEVEL`: INFO (configurable)
- `ENVIRONMENT`: production
- `API_VERSION`: 1.0.0

### Health Check
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start Period**: 5 seconds
- **Retries**: 3

### Security Features
- Non-root user creation
- Proper file permissions
- Minimal attack surface
- No unnecessary packages

## Deployment to ECR

### 1. Create ECR Repository
```bash
aws ecr create-repository --repository-name lambda-container-api --region us-east-1
```

### 2. Get Login Token
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### 3. Tag and Push
```bash
# Tag for ECR
docker tag lambda-container-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api:latest
```

## Troubleshooting

### Common Issues

#### Build Failures
- **Issue**: Dependencies not installing
- **Solution**: Check `src/requirements.txt` exists and is valid
- **Command**: `python validate_dockerfile.py`

#### Import Errors
- **Issue**: Lambda function cannot import modules
- **Solution**: Verify PYTHONPATH and file structure
- **Command**: `python test_lambda_import.py`

#### Permission Errors
- **Issue**: Container cannot access files
- **Solution**: Check file permissions in Dockerfile
- **Command**: Review `chown` and `chmod` commands

### Debug Commands

```bash
# Inspect container layers
docker history lambda-container-api

# Run interactive shell in container
docker run -it --entrypoint /bin/bash lambda-container-api

# Check container size
docker images lambda-container-api

# View container logs
docker logs <container-id>
```

## Best Practices Implemented

### 🔒 Security
- ✅ Non-root user execution
- ✅ Minimal base image
- ✅ No sensitive data in layers
- ✅ Proper file permissions

### 📦 Optimization
- ✅ Multi-stage build
- ✅ .dockerignore for build context
- ✅ Dependency caching
- ✅ Minimal final image

### 🏥 Reliability
- ✅ Health checks
- ✅ Error handling
- ✅ Logging configuration
- ✅ Graceful failures

### 🧪 Testing
- ✅ Automated validation
- ✅ Unit test compatibility
- ✅ Integration testing
- ✅ Manual test procedures

## Requirements Compliance

This Docker implementation satisfies the following requirements:

- **2.1**: ✅ Uses AWS Lambda compatible Docker image
- **2.2**: ✅ Includes all dependencies and runtime requirements
- **2.3**: ✅ Exposes application on correct port for Lambda execution
- **2.4**: ✅ Optimized for size and security best practices
- **2.5**: ✅ Container functions identically to non-containerized version

## Next Steps

1. **Build and test locally**: Use validation scripts
2. **Deploy to ECR**: Push image to Amazon ECR
3. **Configure Lambda**: Create Lambda function using container image
4. **Set up CI/CD**: Automate build and deployment process
5. **Monitor**: Set up CloudWatch logging and monitoring

## Support

For issues or questions:
1. Run validation scripts first
2. Check troubleshooting section
3. Review container logs
4. Verify AWS Lambda compatibility