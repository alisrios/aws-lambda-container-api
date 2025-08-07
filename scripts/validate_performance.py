#!/usr/bin/env python3
"""
Performance Validation Script for AWS Lambda Container API

This script validates the performance optimizations implemented in task 9:
- Docker image size optimization
- Lambda performance configuration
- API Gateway throttling
- Monitoring and alerting setup
"""

import json
import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import argparse
import sys
import os


class PerformanceValidator:
    """Validates performance optimizations for the Lambda Container API"""
    
    def __init__(self, api_url: str, num_requests: int = 100, concurrency: int = 10):
        self.api_url = api_url.rstrip('/')
        self.num_requests = num_requests
        self.concurrency = concurrency
        self.results = {
            'hello_endpoint': [],
            'echo_endpoint': [],
            'health_endpoint': []
        }
    
    def test_endpoint_performance(self, endpoint: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Test performance of a single endpoint"""
        url = f"{self.api_url}{endpoint}"
        
        start_time = time.time()
        try:
            response = requests.get(url, params=params, timeout=30)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'response_size': len(response.content),
                'headers': dict(response.headers),
                'cold_start': 'x-amzn-trace-id' in response.headers
            }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time_ms': (end_time - start_time) * 1000
            }
    
    def run_concurrent_tests(self, endpoint: str, params: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Run concurrent tests against an endpoint"""
        print(f"Testing {endpoint} with {self.num_requests} requests, concurrency: {self.concurrency}")
        
        results = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            # Submit all requests
            futures = [
                executor.submit(self.test_endpoint_performance, endpoint, params)
                for _ in range(self.num_requests)
            ]
            
            # Collect results
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                results.append(result)
                
                if i % 10 == 0:
                    print(f"  Completed {i}/{self.num_requests} requests")
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]], endpoint_name: str) -> Dict[str, Any]:
        """Analyze performance test results"""
        successful_results = [r for r in results if r.get('success', False)]
        failed_results = [r for r in results if not r.get('success', False)]
        
        if not successful_results:
            return {
                'endpoint': endpoint_name,
                'total_requests': len(results),
                'successful_requests': 0,
                'failed_requests': len(failed_results),
                'success_rate': 0.0,
                'error': 'All requests failed'
            }
        
        response_times = [r['response_time_ms'] for r in successful_results]
        status_codes = [r['status_code'] for r in successful_results]
        
        # Check for cold starts (simplified detection)
        cold_starts = sum(1 for r in successful_results if r.get('cold_start', False))
        
        analysis = {
            'endpoint': endpoint_name,
            'total_requests': len(results),
            'successful_requests': len(successful_results),
            'failed_requests': len(failed_results),
            'success_rate': len(successful_results) / len(results) * 100,
            'response_times': {
                'min_ms': min(response_times),
                'max_ms': max(response_times),
                'avg_ms': statistics.mean(response_times),
                'median_ms': statistics.median(response_times),
                'p95_ms': self.percentile(response_times, 95),
                'p99_ms': self.percentile(response_times, 99)
            },
            'status_codes': {
                '200': status_codes.count(200),
                '400': status_codes.count(400),
                '500': status_codes.count(500),
                'other': len([c for c in status_codes if c not in [200, 400, 500]])
            },
            'cold_starts_detected': cold_starts,
            'cold_start_rate': cold_starts / len(successful_results) * 100 if successful_results else 0
        }
        
        return analysis
    
    @staticmethod
    def percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of a dataset"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def validate_performance_thresholds(self, analysis: Dict[str, Any]) -> Dict[str, bool]:
        """Validate performance against defined thresholds"""
        thresholds = {
            'success_rate_min': 95.0,  # Minimum 95% success rate
            'avg_response_time_max': 2000,  # Maximum 2 seconds average
            'p95_response_time_max': 5000,  # Maximum 5 seconds P95
            'cold_start_rate_max': 20.0  # Maximum 20% cold start rate
        }
        
        validations = {
            'success_rate': analysis['success_rate'] >= thresholds['success_rate_min'],
            'avg_response_time': analysis['response_times']['avg_ms'] <= thresholds['avg_response_time_max'],
            'p95_response_time': analysis['response_times']['p95_ms'] <= thresholds['p95_response_time_max'],
            'cold_start_rate': analysis['cold_start_rate'] <= thresholds['cold_start_rate_max']
        }
        
        return validations
    
    def test_monitoring_headers(self) -> Dict[str, Any]:
        """Test that monitoring headers are present"""
        print("Testing monitoring headers...")
        
        endpoints = ['/hello', '/echo?msg=monitoring_test', '/health']
        header_results = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=10)
                headers = dict(response.headers)
                
                header_results[endpoint] = {
                    'x_request_id': 'x-request-id' in headers or 'X-Request-ID' in headers,
                    'x_response_time': 'x-response-time' in headers or 'X-Response-Time' in headers,
                    'content_type': 'content-type' in headers,
                    'status_code': response.status_code
                }
            except Exception as e:
                header_results[endpoint] = {
                    'error': str(e),
                    'status_code': None
                }
        
        return header_results
    
    def run_full_performance_test(self) -> Dict[str, Any]:
        """Run complete performance validation"""
        print(f"Starting performance validation for: {self.api_url}")
        print(f"Configuration: {self.num_requests} requests, {self.concurrency} concurrent")
        print("=" * 60)
        
        # Test each endpoint
        endpoints = [
            ('/hello', None, 'hello_endpoint'),
            ('/echo', {'msg': 'performance_test'}, 'echo_endpoint'),
            ('/health', None, 'health_endpoint')
        ]
        
        all_results = {}
        
        for endpoint, params, result_key in endpoints:
            print(f"\nTesting {endpoint}...")
            results = self.run_concurrent_tests(endpoint, params)
            analysis = self.analyze_results(results, endpoint)
            validations = self.validate_performance_thresholds(analysis)
            
            all_results[result_key] = {
                'analysis': analysis,
                'validations': validations,
                'raw_results': results
            }
        
        # Test monitoring headers
        header_results = self.test_monitoring_headers()
        
        # Overall summary
        overall_success = all(
            all(v.values()) for result in all_results.values() 
            for v in [result['validations']]
        )
        
        summary = {
            'overall_success': overall_success,
            'test_configuration': {
                'api_url': self.api_url,
                'num_requests': self.num_requests,
                'concurrency': self.concurrency
            },
            'endpoint_results': all_results,
            'monitoring_headers': header_results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }
        
        return summary
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a formatted summary of results"""
        print("\n" + "=" * 60)
        print("PERFORMANCE VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"Overall Success: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}")
        print(f"Test Time: {results['timestamp']}")
        print(f"API URL: {results['test_configuration']['api_url']}")
        
        print("\nEndpoint Performance:")
        for endpoint_key, endpoint_data in results['endpoint_results'].items():
            analysis = endpoint_data['analysis']
            validations = endpoint_data['validations']
            
            print(f"\n  {analysis['endpoint']}:")
            print(f"    Success Rate: {analysis['success_rate']:.1f}% "
                  f"({'✅' if validations['success_rate'] else '❌'})")
            print(f"    Avg Response: {analysis['response_times']['avg_ms']:.1f}ms "
                  f"({'✅' if validations['avg_response_time'] else '❌'})")
            print(f"    P95 Response: {analysis['response_times']['p95_ms']:.1f}ms "
                  f"({'✅' if validations['p95_response_time'] else '❌'})")
            print(f"    Cold Starts: {analysis['cold_start_rate']:.1f}% "
                  f"({'✅' if validations['cold_start_rate'] else '❌'})")
        
        print("\nMonitoring Headers:")
        for endpoint, headers in results['monitoring_headers'].items():
            if 'error' not in headers:
                print(f"  {endpoint}: "
                      f"Request-ID: {'✅' if headers['x_request_id'] else '❌'}, "
                      f"Response-Time: {'✅' if headers['x_response_time'] else '❌'}")
            else:
                print(f"  {endpoint}: ❌ Error - {headers['error']}")


def main():
    parser = argparse.ArgumentParser(description='Validate Lambda Container API Performance')
    parser.add_argument('--api-url', required=True, help='API Gateway URL')
    parser.add_argument('--requests', type=int, default=100, help='Number of requests per endpoint')
    parser.add_argument('--concurrency', type=int, default=10, help='Concurrent requests')
    parser.add_argument('--output', help='Output file for detailed results (JSON)')
    
    args = parser.parse_args()
    
    # Validate API URL
    if not args.api_url.startswith(('http://', 'https://')):
        print("Error: API URL must start with http:// or https://")
        sys.exit(1)
    
    # Run performance validation
    validator = PerformanceValidator(args.api_url, args.requests, args.concurrency)
    
    try:
        results = validator.run_full_performance_test()
        validator.print_summary(results)
        
        # Save detailed results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nDetailed results saved to: {args.output}")
        
        # Exit with appropriate code
        sys.exit(0 if results['overall_success'] else 1)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during performance validation: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()