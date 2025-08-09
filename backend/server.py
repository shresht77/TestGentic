# Simple local backend server for DPDP Hotel Compliance PoC
# Serves static files from dpdp_frontend and exposes health & consent capture endpoints.

import http.server
import socketserver
import os
import json
from urllib.parse import parse_qs

# Determine base directory (project root)
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.normpath(os.path.join(current_dir, '..', 'dpdp_frontend'))

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'ok'}
            self.wfile.write(json.dumps(response).encode())
            return
        # Otherwise serve static files
        super().do_GET()

    def do_POST(self):
        if self.path == '/consent/capture':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            # Attempt to parse as URL-encoded form data
            data = parse_qs(body)
            # In a real application, this data would be stored in a persistent ledger (e.g., DynamoDB)
            response = {
                'message': 'Consent captured successfully',
                'data': data,
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            # Unsupported path
            self.send_error(404, "Not found")

    def translate_path(self, path):
        # Override to serve files from the frontend directory
        # For root, serve index.html
        if path == '/':
            path = '/index.html'
        # Remove query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Build full local path
        return os.path.join(frontend_dir, path.lstrip('/'))

def run(server_class=socketserver.TCPServer, handler_class=RequestHandler, port=8000):
    os.chdir(frontend_dir)
    with server_class(("", port), handler_class) 
        httpd.serve_forever()

if __name__ == '__main__':
    run()
