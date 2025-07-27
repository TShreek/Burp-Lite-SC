"""
UI Server for Burp-Lite Scanner
Serves the dashboard UI and provides API access to logs and scanner results
"""
import os
import json
import http.server
import socketserver
import sys
from urllib.parse import urlparse, parse_qs
from scanner.passive import scan_traffic_file

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

UI_PORT = 8081
UI_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(os.path.dirname(UI_DIR), 'logs')
TRAFFIC_FILE = os.path.join(LOGS_DIR, 'traffic.json')

class UIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API endpoints
        if parsed_path.path == '/api/traffic':
            self.serve_json_file(TRAFFIC_FILE)
        elif parsed_path.path == '/api/scan':
            self.serve_scan_results()
        # Access to logs directory
        elif parsed_path.path.startswith('/logs/'):
            requested_file = os.path.join(
                os.path.dirname(UI_DIR), 
                parsed_path.path[1:]  # Remove leading slash
            )
            self.serve_file(requested_file)
        else:
            # Default to serving files from UI directory
            super().do_GET()
    
    def serve_json_file(self, file_path):
        """Serve a JSON file with proper content type"""
        if not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return
            
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_file(self, file_path):
        """Serve any file with appropriate content type"""
        if not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return
            
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            self.send_response(200)
            
            # Determine content type based on file extension
            _, ext = os.path.splitext(file_path)
            content_type = {
                '.json': 'application/json',
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif'
            }.get(ext.lower(), 'application/octet-stream')
            
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_scan_results(self):
        """Run scanner and return results"""
        try:
            if not os.path.exists(TRAFFIC_FILE):
                self.send_json_response({"error": "No traffic data found"})
                return
                
            findings = scan_traffic_file(TRAFFIC_FILE)
            self.send_json_response({"findings": findings})
        except Exception as e:
            self.send_error(500, str(e))
    
    def send_json_response(self, data):
        """Send a JSON response"""
        json_data = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(json_data)))
        self.end_headers()
        self.wfile.write(json_data)


def run():
    with socketserver.ThreadingTCPServer(("", UI_PORT), UIHandler) as httpd:
        print(f"[*] UI Server running on http://localhost:{UI_PORT}")
        print(f"[*] Open http://localhost:{UI_PORT}/dashboard.html in your browser")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
