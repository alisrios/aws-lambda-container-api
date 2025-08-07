#!/usr/bin/env python3
"""
Test script to validate Lambda function can be imported and executed
Tests the containerized application logic without Docker
"""
import sys
import os
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_lambda_import():
    """Test that lambda_function can be imported"""
    try:
        from lambda_function import lambda_handler
        print("✅ Lambda function imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import lambda function: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing lambda function: {e}")
        return False

def test_flask_app_import():
    """Test that Flask app can be imported"""
    try:
        from app import app
        print("✅ Flask app imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        return False

def test_lambda_handler_execution():
    """Test Lambda handler execution with sample events"""
    try:
        from lambda_function import lambda_handler
        
        # Test /hello endpoint
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
        
        # Mock context
        class MockContext:
            aws_request_id = "test-123"
        
        context = MockContext()
        
        print("  Testing /hello endpoint...")
        response = lambda_handler(hello_event, context)
        
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            if 'Hello World' in body.get('message', ''):
                print("    ✅ /hello endpoint working correctly")
            else:
                print(f"    ❌ /hello endpoint returned unexpected response: {body}")
                return False
        else:
            print(f"    ❌ /hello endpoint returned status {response['statusCode']}")
            return False
        
        # Test /echo endpoint
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
        
        print("  Testing /echo endpoint...")
        response = lambda_handler(echo_event, context)
        
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            if body.get('message') == 'test message':
                print("    ✅ /echo endpoint working correctly")
            else:
                print(f"    ❌ /echo endpoint returned unexpected response: {body}")
                return False
        else:
            print(f"    ❌ /echo endpoint returned status {response['statusCode']}")
            return False
        
        # Test /echo endpoint without msg parameter
        echo_no_msg_event = {
            "httpMethod": "GET",
            "path": "/echo",
            "queryStringParameters": None,
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }
        
        print("  Testing /echo endpoint without msg parameter...")
        response = lambda_handler(echo_no_msg_event, context)
        
        if response['statusCode'] == 400:
            body = json.loads(response['body'])
            if 'required' in body.get('error', '').lower():
                print("    ✅ /echo endpoint error handling working correctly")
            else:
                print(f"    ❌ /echo endpoint error message unexpected: {body}")
                return False
        else:
            print(f"    ❌ /echo endpoint should return 400 but returned {response['statusCode']}")
            return False
        
        print("✅ Lambda handler execution tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Lambda handler execution failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Lambda function for container compatibility...")
    print("=" * 50)
    
    tests = [
        ("Lambda Import", test_lambda_import),
        ("Flask App Import", test_flask_app_import),
        ("Lambda Handler Execution", test_lambda_handler_execution)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Lambda function tests passed! Ready for containerization.")
        return True
    else:
        print("💥 Some tests failed. Please fix issues before containerizing.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)