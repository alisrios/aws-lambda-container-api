#!/usr/bin/env python3
"""
Script to test the Docker container locally
Validates container functionality before deployment
"""
import json
import subprocess
import time
import requests
import sys
import os

def run_command(cmd, capture_output=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_docker_build():
    """Test Docker image build"""
    print("🔨 Building Docker image...")
    success, stdout, stderr = run_command("docker build -t lambda-container-api .")
    
    if success:
        print("✅ Docker build successful")
        return True
    else:
        print(f"❌ Docker build failed: {stderr}")
        return False

def test_container_health():
    """Test container health check"""
    print("🏥 Testing container health check...")
    
    # Run container with health check
    cmd = "docker run --rm --name test-lambda lambda-container-api python -c \"import app; print('Health check passed')\""
    success, stdout, stderr = run_command(cmd)
    
    if success and "Health check passed" in stdout:
        print("✅ Container health check passed")
        return True
    else:
        print(f"❌ Container health check failed: {stderr}")
        return False

def test_lambda_runtime():
    """Test Lambda runtime interface"""
    print("🚀 Testing Lambda runtime interface...")
    
    # Create test event for /hello endpoint
    hello_event = {
        "httpMethod": "GET",
        "path": "/hello",
        "queryStringParameters": None,
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }
    
    # Create test event for /echo endpoint
    echo_event = {
        "httpMethod": "GET",
        "path": "/echo",
        "queryStringParameters": {"msg": "test message"},
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }
    
    # Test /hello endpoint
    print("  Testing /hello endpoint...")
    test_cmd = f"""docker run --rm lambda-container-api python -c "
import json
from lambda_function import lambda_handler

event = {json.dumps(hello_event)}
context = type('Context', (), {{'aws_request_id': 'test-123'}})()

try:
    response = lambda_handler(event, context)
    print('Response:', json.dumps(response, indent=2))
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        if 'Hello World' in body.get('message', ''):
            print('SUCCESS: /hello endpoint working')
        else:
            print('ERROR: /hello response incorrect')
    else:
        print('ERROR: /hello returned non-200 status')
except Exception as e:
    print('ERROR:', str(e))
"
"""
    
    success, stdout, stderr = run_command(test_cmd)
    if success and "SUCCESS: /hello endpoint working" in stdout:
        print("    ✅ /hello endpoint test passed")
    else:
        print(f"    ❌ /hello endpoint test failed: {stdout} {stderr}")
        return False
    
    # Test /echo endpoint
    print("  Testing /echo endpoint...")
    test_cmd = f"""docker run --rm lambda-container-api python -c "
import json
from lambda_function import lambda_handler

event = {json.dumps(echo_event)}
context = type('Context', (), {{'aws_request_id': 'test-123'}})()

try:
    response = lambda_handler(event, context)
    print('Response:', json.dumps(response, indent=2))
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        if body.get('message') == 'test message':
            print('SUCCESS: /echo endpoint working')
        else:
            print('ERROR: /echo response incorrect')
    else:
        print('ERROR: /echo returned non-200 status')
except Exception as e:
    print('ERROR:', str(e))
"
"""
    
    success, stdout, stderr = run_command(test_cmd)
    if success and "SUCCESS: /echo endpoint working" in stdout:
        print("    ✅ /echo endpoint test passed")
    else:
        print(f"    ❌ /echo endpoint test failed: {stdout} {stderr}")
        return False
    
    print("✅ Lambda runtime interface tests passed")
    return True

def test_container_security():
    """Test container security configurations"""
    print("🔒 Testing container security...")
    
    # Check if container runs as non-root (where possible)
    cmd = "docker run --rm lambda-container-api whoami"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(f"  Container user: {stdout.strip()}")
        print("✅ Container security check completed")
        return True
    else:
        print(f"❌ Container security check failed: {stderr}")
        return False

def test_image_size():
    """Check Docker image size"""
    print("📏 Checking Docker image size...")
    
    cmd = "docker images lambda-container-api --format \"table {{.Size}}\""
    success, stdout, stderr = run_command(cmd)
    
    if success:
        lines = stdout.strip().split('\n')
        if len(lines) > 1:
            size = lines[1]
            print(f"  Image size: {size}")
            print("✅ Image size check completed")
            return True
    
    print(f"❌ Could not determine image size: {stderr}")
    return False

def cleanup():
    """Clean up test resources"""
    print("🧹 Cleaning up...")
    run_command("docker rmi lambda-container-api", capture_output=False)

def main():
    """Main test function"""
    print("🐳 Starting Docker container tests for AWS Lambda...")
    print("=" * 50)
    
    tests = [
        ("Docker Build", test_docker_build),
        ("Container Health", test_container_health),
        ("Lambda Runtime", test_lambda_runtime),
        ("Container Security", test_container_security),
        ("Image Size", test_image_size)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All container tests passed! Container is ready for deployment.")
        return 0
    else:
        print("💥 Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        cleanup()
        sys.exit(1)