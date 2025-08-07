#!/usr/bin/env python3
"""
Test script to verify the Flask application implementation
Tests the requirements specified in the task
"""
import sys
import os
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app
from src.lambda_function import lambda_handler

def test_flask_endpoints():
    """Test Flask endpoints directly"""
    print("Testing Flask endpoints...")
    
    with app.test_client() as client:
        # Test /hello endpoint (Requirement 1.2)
        print("\n1. Testing /hello endpoint:")
        response = client.get('/hello')
        print(f"   Status Code: {response.status_code}")
        data = json.loads(response.get_data(as_text=True))
        print(f"   Response: {data}")
        assert response.status_code == 200
        assert "Hello World" in data["message"]
        print("   ✓ /hello endpoint works correctly")
        
        # Test /echo endpoint with parameter (Requirement 1.3)
        print("\n2. Testing /echo endpoint with parameter:")
        response = client.get('/echo?msg=test_message')
        print(f"   Status Code: {response.status_code}")
        data = json.loads(response.get_data(as_text=True))
        print(f"   Response: {data}")
        assert response.status_code == 200
        assert data["message"] == "test_message"
        print("   ✓ /echo endpoint with parameter works correctly")
        
        # Test /echo endpoint without parameter (Requirement 1.5)
        print("\n3. Testing /echo endpoint without parameter:")
        response = client.get('/echo')
        print(f"   Status Code: {response.status_code}")
        data = json.loads(response.get_data(as_text=True))
        print(f"   Response: {data}")
        assert response.status_code == 400
        assert "Parameter 'msg' is required" in data["error"]
        print("   ✓ /echo endpoint error handling works correctly")

def test_lambda_handler():
    """Test Lambda handler function"""
    print("\n\nTesting Lambda handler...")
    
    # Test /hello via Lambda handler
    print("\n4. Testing Lambda handler for /hello:")
    event = {
        'httpMethod': 'GET',
        'path': '/hello',
        'queryStringParameters': None
    }
    context = type('Context', (), {'aws_request_id': 'test-request-id'})()
    
    response = lambda_handler(event, context)
    print(f"   Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"   Response Body: {body}")
    assert response['statusCode'] == 200
    assert "Hello World" in body["message"]
    print("   ✓ Lambda handler for /hello works correctly")
    
    # Test /echo via Lambda handler
    print("\n5. Testing Lambda handler for /echo:")
    event = {
        'httpMethod': 'GET',
        'path': '/echo',
        'queryStringParameters': {'msg': 'lambda_test'}
    }
    
    response = lambda_handler(event, context)
    print(f"   Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"   Response Body: {body}")
    assert response['statusCode'] == 200
    assert body["message"] == "lambda_test"
    print("   ✓ Lambda handler for /echo works correctly")

if __name__ == '__main__':
    try:
        test_flask_endpoints()
        test_lambda_handler()
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("✅ Task 1 implementation is complete and verified")
        print("="*50)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)