"""
Performance tests for deployed AWS Lambda Container API
Tests API performance under various load conditions
Requirements: 7.3, 7.4, 7.5
"""
import time
import requests
import pytest
import concurrent.futures
from typing import List, Dict, Tuple
import statistics


class TestAPIPerformance:
    """Performance tests for the deployed API"""
    
    def test_single_request_performance(self, api_endpoints, test_timeout):
        """Test performance of single requests to each endpoint"""
        endpoints = [
            ('hello', api_endpoints['hello_url']),
            ('echo', api_endpoints['echo_url'] + '?msg=performance_test')
        ]
        
        for endpoint_name, url in endpoints:
            start_time = time.time()
            response = requests.get(url, timeout=test_timeout)
            response_time = time.time() - start_time
            
            assert response.status_code == 200, f"{endpoint_name} endpoint failed"
            assert response_time < 10.0, f"{endpoint_name} response time too high: {response_time:.2f}s"
            
            print(f"✓ {endpoint_name} endpoint: {response_time:.2f}s")
    
    def test_concurrent_requests(self, api_endpoints, performance_config, test_timeout):
        """Test API performance under concurrent load"""
        def make_request(url: str) -> Tuple[int, float, str]:
            """Make a single request and return status, time, and error"""
            try:
                start_time = time.time()
                response = requests.get(url, timeout=test_timeout)
                response_time = time.time() - start_time
                return response.status_code, response_time, None
            except Exception as e:
                return 0, 0, str(e)
        
        # Test concurrent requests to hello endpoint
        num_requests = performance_config['concurrent_requests']
        url = api_endpoints['hello_url']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request, url) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r[0] == 200]
        failed_requests = [r for r in results if r[0] != 200 or r[2] is not None]
        
        success_rate = len(successful_requests) / num_requests * 100
        
        assert success_rate >= performance_config['min_success_rate'], \
            f"Success rate too low: {success_rate:.1f}%"
        
        if successful_requests:
            response_times = [r[1] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            assert avg_response_time < performance_config['max_response_time'], \
                f"Average response time too high: {avg_response_time:.2f}s"
            
            print(f"✓ Concurrent requests test:")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Average response time: {avg_response_time:.2f}s")
            print(f"  Max response time: {max_response_time:.2f}s")
    
    def test_message_size_performance(self, api_endpoints, test_timeout):
        """Test performance with different message sizes"""
        message_sizes = [10, 100, 1000, 5000]  # Character counts
        
        for size in message_sizes:
            test_message = "A" * size
            url = f"{api_endpoints['echo_url']}?msg={test_message}"
            
            start_time = time.time()
            response = requests.get(url, timeout=test_timeout)
            response_time = time.time() - start_time
            
            assert response.status_code == 200, f"Failed for message size {size}"
            
            data = response.json()
            assert data['message'] == test_message, f"Message mismatch for size {size}"
            
            # Performance should scale reasonably with message size
            max_expected_time = 5.0 + (size / 1000)  # Allow more time for larger messages
            assert response_time < max_expected_time, \
                f"Response time too high for {size} chars: {response_time:.2f}s"
            
            print(f"✓ Message size {size} chars: {response_time:.2f}s")
    
    @pytest.mark.slow
    def test_sustained_load(self, api_endpoints, performance_config, test_timeout):
        """Test API under sustained load over time"""
        duration = performance_config['sustained_duration']
        requests_per_second = performance_config['requests_per_second']
        url = api_endpoints['hello_url']
        
        results = []
        start_time = time.time()
        request_count = 0
        
        print(f"Running sustained load test for {duration}s at {requests_per_second} req/s...")
        
        while time.time() - start_time < duration:
            try:
                req_start = time.time()
                response = requests.get(url, timeout=test_timeout)
                req_time = time.time() - req_start
                
                results.append({
                    'status_code': response.status_code,
                    'response_time': req_time,
                    'timestamp': time.time()
                })
                request_count += 1
                
                # Control request rate
                time.sleep(max(0, 1.0 / requests_per_second - req_time))
                
            except Exception as e:
                results.append({
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        # Analyze sustained load results
        successful_requests = [r for r in results if r.get('status_code') == 200]
        error_requests = [r for r in results if 'error' in r]
        
        success_rate = len(successful_requests) / len(results) * 100
        avg_response_time = statistics.mean(r['response_time'] for r in successful_requests)
        
        assert success_rate >= performance_config['min_success_rate'], \
            f"Sustained load success rate too low: {success_rate:.1f}%"
        
        assert avg_response_time < performance_config['max_response_time'], \
            f"Sustained load average response time too high: {avg_response_time:.2f}s"
        
        print(f"✓ Sustained load test results:")
        print(f"  Total requests: {len(results)}")
        print(f"  Successful requests: {len(successful_requests)}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Average response time: {avg_response_time:.2f}s")
    
    def test_cold_start_performance(self, api_endpoints, lambda_info, aws_clients, test_timeout):
        """Test Lambda cold start performance"""
        # First, try to force a cold start by waiting
        print("Waiting to allow for potential cold start...")
        time.sleep(60)  # Wait 1 minute to increase chance of cold start
        
        # Make request and measure time
        start_time = time.time()
        response = requests.get(api_endpoints['hello_url'], timeout=test_timeout)
        total_time = time.time() - start_time
        
        assert response.status_code == 200, "Cold start request failed"
        
        # Cold starts for container images can be longer, but should be reasonable
        assert total_time < 30.0, f"Cold start time too high: {total_time:.2f}s"
        
        print(f"✓ Cold start test: {total_time:.2f}s")
        
        # Follow up with a warm request
        start_time = time.time()
        warm_response = requests.get(api_endpoints['hello_url'], timeout=test_timeout)
        warm_time = time.time() - start_time
        
        assert warm_response.status_code == 200, "Warm request failed"
        assert warm_time < 5.0, f"Warm request time too high: {warm_time:.2f}s"
        
        print(f"✓ Warm request: {warm_time:.2f}s")
        
        # Warm request should be significantly faster
        if total_time > 5.0:  # Only check if first request was likely a cold start
            assert warm_time < total_time / 2, "Warm request not significantly faster than cold start"
    
    def test_error_response_performance(self, api_endpoints, test_timeout):
        """Test performance of error responses"""
        # Test 400 error (missing parameter)
        start_time = time.time()
        response = requests.get(api_endpoints['echo_url'], timeout=test_timeout)
        response_time = time.time() - start_time
        
        assert response.status_code == 400, "Expected 400 error"
        assert response_time < 5.0, f"Error response time too high: {response_time:.2f}s"
        
        print(f"✓ Error response performance: {response_time:.2f}s")
        
        # Test 404 error (invalid endpoint)
        invalid_url = f"{api_endpoints['api_url']}/nonexistent"
        start_time = time.time()
        response = requests.get(invalid_url, timeout=test_timeout)
        response_time = time.time() - start_time
        
        assert response.status_code == 404, "Expected 404 error"
        assert response_time < 5.0, f"404 response time too high: {response_time:.2f}s"
        
        print(f"✓ 404 response performance: {response_time:.2f}s")