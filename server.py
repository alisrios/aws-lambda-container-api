#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.request
import urllib.parse
from urllib.parse import urlparse, parse_qs

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/test':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Fazer requisição para Lambda
                lambda_url = 'http://lambda-api:8080/2015-03-31/functions/function/invocations'
                lambda_payload = json.dumps(data).encode('utf-8')
                
                req = urllib.request.Request(
                    lambda_url,
                    data=lambda_payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = response.read().decode('utf-8')
                    
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(result.encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = json.dumps({'error': str(e)})
                self.wfile.write(error_response.encode('utf-8'))
        else:
            super().do_POST()

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print(f"Servidor rodando em http://localhost:{PORT}")
        print("Pressione Ctrl+C para parar")
        httpd.serve_forever()