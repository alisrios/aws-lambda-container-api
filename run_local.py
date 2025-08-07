#!/usr/bin/env python3
"""
Local development server runner
Allows testing the Flask application locally before containerization
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app

if __name__ == '__main__':
    print("Starting Flask development server...")
    print("API endpoints available at:")
    print("  - http://localhost:5000/hello")
    print("  - http://localhost:5000/echo?msg=your_message")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=True)