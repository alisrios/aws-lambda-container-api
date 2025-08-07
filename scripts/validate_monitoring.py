#!/usr/bin/env python3
"""
Script to validate monitoring and observability setup
Tests all monitoring features including logging, health checks, and metrics
"""
import json
import requests
import time
import sys
import argparse
from typing import Dict, List, Any


class MonitoringValidator:
    """Validates monitoring and observability features"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
        self.results = []
    
    def log_result(self, test_name: str, success: bool, message: str, details: Dict[str, Any] = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if details and not success:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def test_health_endpoint(self) -> bool:
        """Test health endpoint functionality"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code != 200:
                self.log_result(
                    "Health Endpoint Status",
                    False,
                    f"Expected 200, got {response.status_code}",
                    {'status_code': response.status_code, 'response': response.text}
                )
                return False
            
            data = response.json()
            
            # Check required fields
            required_fields = ['status', 'timestamp', 'version', 'environment', 'request_id', 'checks']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result(
                    "Health Endpoint Structure",
                    False,
                    f"Missing required fields: {missing_fields}",
                    {'missing_fields': missing_fields, 'response': data}
                )
                return False
            
            # Check health status
            if data['status'] != 'healthy':
                self.log_result(
                    "Health Status",
                    False,
                    f"Expected 'healthy', got '{data['status']}'",
                    {'status': data['status'], 'response': data}
                )
                return False
            
            # Check all health checks are OK
            checks = data.get('checks', {})
            failed_checks = [name for name, status in checks.items() if status != 'ok']
            
            if failed_checks:
                self.log_result(
                    "Health Checks",
                    False,
                    f"Failed health checks: {failed_checks}",
                    {'failed_checks': failed_checks, 'all_checks': checks}
                )
                return False
            
            self.log_result(
                "Health Endpoint",
                True,
                "Health endpoint working correctly",
                {'status': data['status'], 'checks': len(checks)}
            )
            return True
            
        except Exception as e:
            self.log_result(
                "Health Endpoint",
                False,
                f"Exception occurred: {str(e)}",
                {'exception': str(e)}
            )
            return False
    
    def test_monitoring_headers(self) -> bool:
        """Test monitoring headers on all endpoints"""
        endpoints = ['/hello', '/echo?msg=monitoring_test', '/health']
        all_passed = True
        
        for endpoint in endpoints:
            try:
                custom_id = f"validator-{int(time.time())}-{endpoint.replace('/', '').replace('?', '-')}"
                headers = {'X-Request-ID': custom_id}
                
                response = requests.get(f"{self.api_url}{endpoint}", headers=headers, timeout=10)
                
                if response.status_code != 200:
                    self.log_result(
                        f"Monitoring Headers {endpoint}",
                        False,
                        f"Endpoint returned {response.status_code}",
                        {'endpoint': endpoint, 'status_code': response.status_code}
                    )
                    all_passed = False
                    continue
                
                # Check X-Request-ID header
                if response.headers.get('X-Request-ID') != custom_id:
                    self.log_result(
                        f"Request ID Header {endpoint}",
                        False,
                        f"Request ID not propagated correctly",
                        {
                            'expected': custom_id,
                            'actual': response.headers.get('X-Request-ID'),
                            'endpoint': endpoint
                        }
                    )
                    all_passed = False
                    continue
                
                # Check X-Response-Time header
                if 'X-Response-Time' not in response.headers:
                    self.log_result(
                        f"Response Time Header {endpoint}",
                        False,
                        "Missing X-Response-Time header",
                        {'endpoint': endpoint, 'headers': dict(response.headers)}
                    )
                    all_passed = False
                    continue
                
                # Validate response time is reasonable
                try:
                    response_time = float(response.headers['X-Response-Time'])
                    if response_time <= 0 or response_time > 30000:  # 30 seconds max
                        self.log_result(
                            f"Response Time Value {endpoint}",
                            False,
                            f"Unreasonable response time: {response_time}ms",
                            {'endpoint': endpoint, 'response_time': response_time}
                        )
                        all_passed = False
                        continue
                except ValueError:
                    self.log_result(
                        f"Response Time Format {endpoint}",
                        False,
                        f"Invalid response time format: {response.headers['X-Response-Time']}",
                        {'endpoint': endpoint, 'response_time': response.headers['X-Response-Time']}
                    )
                    all_passed = False
                    continue
                
                # Check request ID in response body
                try:
                    data = response.json()
                    if data.get('request_id') != custom_id:
                        self.log_result(
                            f"Request ID Body {endpoint}",
                            False,
                            "Request ID not in response body",
                            {
                                'expected': custom_id,
                                'actual': data.get('request_id'),
                                'endpoint': endpoint
                            }
                        )
                        all_passed = False
                        continue
                except json.JSONDecodeError:
                    self.log_result(
                        f"Response JSON {endpoint}",
                        False,
                        "Response is not valid JSON",
                        {'endpoint': endpoint, 'response': response.text[:200]}
                    )
                    all_passed = False
                    continue
                
                self.log_result(
                    f"Monitoring Headers {endpoint}",
                    True,
                    f"All monitoring headers present and correct",
                    {'endpoint': endpoint, 'response_time': response_time}
                )
                
            except Exception as e:
                self.log_result(
                    f"Monitoring Headers {endpoint}",
                    False,
                    f"Exception occurred: {str(e)}",
                    {'endpoint': endpoint, 'exception': str(e)}
                )
                all_passed = False
        
        return all_passed
    
    def test_error_monitoring(self) -> bool:
        """Test error monitoring and structured error responses"""
        error_cases = [
            ('/echo', 400, "Parameter 'msg' is required"),
            ('/nonexistent', 404, "Endpoint not found")
        ]
        
        all_passed = True
        
        for endpoint, expected_status, expected_error in error_cases:
            try:
                custom_id = f"error-test-{int(time.time())}"
                headers = {'X-Request-ID': custom_id}
                
                response = requests.get(f"{self.api_url}{endpoint}", headers=headers, timeout=10)
                
                if response.status_code != expected_status:
                    self.log_result(
                        f"Error Status {endpoint}",
                        False,
                        f"Expected {expected_status}, got {response.status_code}",
                        {
                            'endpoint': endpoint,
                            'expected_status': expected_status,
                            'actual_status': response.status_code
                        }
                    )
                    all_passed = False
                    continue
                
                # Check monitoring headers in error responses
                if response.headers.get('X-Request-ID') != custom_id:
                    self.log_result(
                        f"Error Request ID {endpoint}",
                        False,
                        "Request ID not in error response headers",
                        {'endpoint': endpoint, 'expected': custom_id}
                    )
                    all_passed = False
                    continue
                
                if 'X-Response-Time' not in response.headers:
                    self.log_result(
                        f"Error Response Time {endpoint}",
                        False,
                        "Response time header missing in error response",
                        {'endpoint': endpoint}
                    )
                    all_passed = False
                    continue
                
                # Check error response structure
                try:
                    data = response.json()
                    required_error_fields = ['error', 'status_code', 'timestamp', 'request_id']
                    missing_fields = [field for field in required_error_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"Error Response Structure {endpoint}",
                            False,
                            f"Missing error response fields: {missing_fields}",
                            {'endpoint': endpoint, 'missing_fields': missing_fields}
                        )
                        all_passed = False
                        continue
                    
                    if data['error'] != expected_error:
                        self.log_result(
                            f"Error Message {endpoint}",
                            False,
                            f"Unexpected error message",
                            {
                                'endpoint': endpoint,
                                'expected': expected_error,
                                'actual': data['error']
                            }
                        )
                        all_passed = False
                        continue
                    
                    self.log_result(
                        f"Error Monitoring {endpoint}",
                        True,
                        "Error monitoring working correctly",
                        {'endpoint': endpoint, 'status': expected_status}
                    )
                    
                except json.JSONDecodeError:
                    self.log_result(
                        f"Error Response JSON {endpoint}",
                        False,
                        "Error response is not valid JSON",
                        {'endpoint': endpoint, 'response': response.text[:200]}
                    )
                    all_passed = False
                    continue
                
            except Exception as e:
                self.log_result(
                    f"Error Monitoring {endpoint}",
                    False,
                    f"Exception occurred: {str(e)}",
                    {'endpoint': endpoint, 'exception': str(e)}
                )
                all_passed = False
        
        return all_passed
    
    def test_performance_monitoring(self) -> bool:
        """Test performance monitoring capabilities"""
        try:
            # Test response time consistency
            response_times = []
            
            for i in range(5):
                start_time = time.time()
                response = requests.get(f"{self.api_url}/hello", timeout=10)
                end_time = time.time()
                
                if response.status_code != 200:
                    self.log_result(
                        "Performance Monitoring",
                        False,
                        f"Request {i+1} failed with status {response.status_code}",
                        {'request_number': i+1, 'status_code': response.status_code}
                    )
                    return False
                
                actual_time = (end_time - start_time) * 1000  # Convert to ms
                header_time = float(response.headers.get('X-Response-Time', 0))
                
                response_times.append({
                    'actual': actual_time,
                    'header': header_time
                })
                
                time.sleep(0.1)  # Small delay between requests
            
            # Analyze response times
            avg_actual = sum(rt['actual'] for rt in response_times) / len(response_times)
            avg_header = sum(rt['header'] for rt in response_times) / len(response_times)
            
            # Check if response times are reasonable
            if avg_actual > 30000:  # 30 seconds
                self.log_result(
                    "Performance Monitoring",
                    False,
                    f"Average response time too high: {avg_actual:.2f}ms",
                    {'average_response_time': avg_actual, 'response_times': response_times}
                )
                return False
            
            # Check if header times are reasonable compared to actual times
            if avg_header <= 0 or avg_header > avg_actual * 2:
                self.log_result(
                    "Performance Header Accuracy",
                    False,
                    f"Header response times seem inaccurate",
                    {
                        'average_actual': avg_actual,
                        'average_header': avg_header,
                        'response_times': response_times
                    }
                )
                return False
            
            self.log_result(
                "Performance Monitoring",
                True,
                f"Performance monitoring working correctly",
                {
                    'average_response_time': avg_actual,
                    'average_header_time': avg_header,
                    'requests_tested': len(response_times)
                }
            )
            return True
            
        except Exception as e:
            self.log_result(
                "Performance Monitoring",
                False,
                f"Exception occurred: {str(e)}",
                {'exception': str(e)}
            )
            return False
    
    def run_all_tests(self) -> bool:
        """Run all monitoring validation tests"""
        print(f"🔍 Starting monitoring validation for: {self.api_url}")
        print("=" * 60)
        
        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Monitoring Headers", self.test_monitoring_headers),
            ("Error Monitoring", self.test_error_monitoring),
            ("Performance Monitoring", self.test_performance_monitoring)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} tests...")
            try:
                result = test_func()
                all_passed = all_passed and result
            except Exception as e:
                print(f"❌ FAIL {test_name}: Unexpected exception: {str(e)}")
                all_passed = False
        
        print("\n" + "=" * 60)
        
        # Summary
        passed_tests = sum(1 for result in self.results if result['success'])
        total_tests = len(self.results)
        
        if all_passed:
            print(f"🎉 All monitoring tests passed! ({passed_tests}/{total_tests})")
        else:
            print(f"❌ Some monitoring tests failed. ({passed_tests}/{total_tests})")
            print("\nFailed tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        return all_passed
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate detailed test report"""
        passed_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]
        
        return {
            'summary': {
                'total_tests': len(self.results),
                'passed_tests': len(passed_tests),
                'failed_tests': len(failed_tests),
                'success_rate': len(passed_tests) / len(self.results) if self.results else 0,
                'api_url': self.api_url,
                'timestamp': time.time()
            },
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'all_results': self.results
        }


def main():
    parser = argparse.ArgumentParser(description='Validate monitoring and observability setup')
    parser.add_argument('api_url', help='API Gateway URL to test')
    parser.add_argument('--output', '-o', help='Output report to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    validator = MonitoringValidator(args.api_url)
    success = validator.run_all_tests()
    
    if args.output:
        report = validator.generate_report()
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    if args.verbose:
        print(f"\n📊 Detailed Results:")
        for result in validator.results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
            if result['details'] and not result['success']:
                print(f"   {json.dumps(result['details'], indent=2)}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()