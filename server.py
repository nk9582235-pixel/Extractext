import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = '{"status": "healthy", "service": "bot"}'
            self.wfile.write(response.encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = 'Hello, Render! The bot is running.'
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"🌐 Server listening on port {port}", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    start_server()