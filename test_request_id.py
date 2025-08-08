#!/usr/bin/env python3
"""
Quick test to verify request ID uniqueness
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from app import app

def test_request_id_uniqueness():
    """Test that request IDs are unique"""
    app.config["TESTING"] = True
    
    request_ids = []
    
    with app.test_client() as client:
        # Make multiple rapid requests
        for i in range(10):
            response = client.get("/hello")
            request_id = response.headers.get("X-Request-ID")
            request_ids.append(request_id)
            print(f"Request {i+1}: {request_id}")
    
    # Check uniqueness
    unique_ids = set(request_ids)
    print(f"\nTotal requests: {len(request_ids)}")
    print(f"Unique IDs: {len(unique_ids)}")
    
    if len(unique_ids) == len(request_ids):
        print("✅ All request IDs are unique!")
        return True
    else:
        print("❌ Some request IDs are duplicated!")
        duplicates = [id for id in request_ids if request_ids.count(id) > 1]
        print(f"Duplicated IDs: {set(duplicates)}")
        return False

if __name__ == "__main__":
    success = test_request_id_uniqueness()
    sys.exit(0 if success else 1)