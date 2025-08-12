"""
UI Server for Burp-Lite Scanner
Serves the dashboard UI and provides API access to logs and scanner results
"""
import os
import json
import http.server
import socketserver
import sys
import argparse
from urllib.parse import urlparse, parse_qs

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import the scanner after adding the path
try:
    from scanner.passive import scan_traffic_file
except ImportError:
    # Fallback function if scanner module can't be imported
    def scan_traffic_file(file_path):
        print("Warning: scanner.passive module not found. Scanner functionality disabled.")
        return []

UI_PORT = 8081
UI_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(os.path.dirname(UI_DIR), 'logs')
TRAFFIC_FILE = os.path.join(LOGS_DIR, 'traffic.json')

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

class UIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def perform_active_scan(self):
        """Run the active scanner against the target app"""
        try:
            # Import the scanner
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from scanner.active import ActiveScanner
            
            # Read traffic file to get scan targets
            targets = []
            if os.path.exists(TRAFFIC_FILE):
                with open(TRAFFIC_FILE, 'r') as f:
                    try:
                        traffic = json.load(f)
                        if isinstance(traffic, list) and len(traffic) > 0:
                            # Use first traffic item to get base URL
                            targets.append({
                                'base_url': 'http://localhost:5000',
                                'method': traffic[0].get('method', 'GET'),
                                'path': traffic[0].get('path', '/'),
                                'headers': traffic[0].get('request_headers', {})
                            })
                    except json.JSONDecodeError:
                        pass
            
            # Default target if no traffic
            if not targets:
                targets = [{
                    'base_url': 'http://localhost:5000',
                    'method': 'GET',
                    'path': '/',
                    'headers': {}
                }]
            
            # Run active scan
            scanner = ActiveScanner()
            all_findings = []
            
            for target in targets:
                findings = scanner.scan(
                    base_url=target['base_url'],
                    method=target['method'],
                    path=target['path'],
                    headers=target['headers']
                )
                all_findings.extend(findings)
            
            # Return results
            self.send_json_response({"findings": all_findings})
            
        except Exception as e:
            print(f"Error in active scan: {e}")
            self.send_json_response({
                "error": str(e),
                "findings": []
            })
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API endpoints
        if parsed_path.path == '/api/traffic':
            self.serve_json_file(TRAFFIC_FILE)
        elif parsed_path.path == '/api/scan':
            self.serve_scan_results()
        elif parsed_path.path == '/api/db/entry':
            self.serve_entry_by_id(parsed_path)
        elif parsed_path.path == '/api/clear':
            self.clear_traffic_file()
        # Access to logs directory
        elif parsed_path.path.startswith('/logs/'):
            requested_file = os.path.join(
                os.path.dirname(UI_DIR), 
                parsed_path.path[1:]  # Remove leading slash
            )
            self.serve_file(requested_file)
        elif parsed_path.path == '/api/active_scan':
            self.perform_active_scan()

        else:
            # Default to serving files from UI directory
            super().do_GET()
    
    def serve_entry_by_id(self, parsed_path):
        """Serve a specific traffic entry by its ID"""
        # Parse query parameters to get the ID
        query_params = parse_qs(parsed_path.query)
        entry_id = query_params.get('id', [''])[0]
        
        if not entry_id:
            self.send_json_response({"error": "No ID provided"})
            return
            
        try:
            # Read the traffic file
            if not os.path.exists(TRAFFIC_FILE):
                self.send_json_response({"error": "Traffic file not found"})
                return
                
            with open(TRAFFIC_FILE, 'r') as f:
                try:
                    traffic_data = json.load(f)
                except json.JSONDecodeError:
                    self.send_json_response({"error": "Invalid traffic data format"})
                    return
            
            # Find the entry with the matching ID
            found_entry = None
            for entry in traffic_data:
                if entry.get('id') == entry_id:
                    found_entry = entry
                    break
            
            if found_entry:
                self.send_json_response(found_entry)
            else:
                self.send_json_response({"error": f"No entry found with ID: {entry_id}"})
                
        except Exception as e:
            print(f"Error serving entry by ID: {e}")
            self.send_json_response({"error": str(e)})
    
    def serve_json_file(self, file_path):
        """Serve a JSON file with proper content type"""
        if not os.path.exists(file_path):
            # Return empty JSON array if file doesn't exist yet
            empty_json = b'[]'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(empty_json)))
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow CORS
            self.end_headers()
            self.wfile.write(empty_json)
            return
            
        try:
            with open(file_path, 'rb') as f:
                content = f.read() or b'[]'  # Default to empty array if file is empty
                
            # Check if content is valid JSON
            try:
                json.loads(content)
            except json.JSONDecodeError:
                # If invalid JSON, return empty array
                content = b'[]'
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-cache, no-store')  # Prevent caching
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow CORS
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            print(f"Error serving JSON file: {e}")
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
        
    def clear_traffic_file(self):
        """Clear the traffic.json file"""
        try:
            # Create an empty JSON array file
            with open(TRAFFIC_FILE, 'w') as f:
                f.write('[]')
            
            # Log the action
            print(f"[*] Traffic log file cleared: {TRAFFIC_FILE}")
            
            # Return success response
            self.send_json_response({
                "status": "success", 
                "message": "Traffic log file cleared successfully"
            })
        except Exception as e:
            print(f"[!] Error clearing traffic log: {e}")
            self.send_error(500, f"Error clearing traffic log: {str(e)}")


def run():
    try:
        # Allow the socket to be reused immediately after the server is stopped
        socketserver.TCPServer.allow_reuse_address = True
        
        with socketserver.ThreadingTCPServer(("", UI_PORT), UIHandler) as httpd:
            print(f"[*] UI Server running on http://localhost:{UI_PORT}")
            print(f"[*] Open http://localhost:{UI_PORT}/index.html in your browser")
            print(f"[*] Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n[!] Error: Port {UI_PORT} is already in use.")
            print(f"[!] Either another instance of the server is running or the port wasn't released properly.")
            print(f"[!] Try the following:")
            print(f"    1. Wait a moment and try again")
            print(f"    2. Kill the process: sudo lsof -i :{UI_PORT} and then sudo kill <PID>")
            print(f"    3. Or use a different port: UI_PORT = {UI_PORT+1} (line 16 in this file)")
            sys.exit(1)
        else:
            raise
    except KeyboardInterrupt:
        print("\n[*] Server shutdown requested...")
        print("[*] Server stopped. Thank you for using Burp-Lite!")
        sys.exit(0)

def main():
    """Entry point for the UI server"""
    global UI_PORT
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Burp-Lite UI Server")
    parser.add_argument("-p", "--port", type=int, default=UI_PORT,
                        help=f"Port to run the UI server on (default: {UI_PORT})")
    args = parser.parse_args()
    
    # Override the UI_PORT if specified via command line
    if args.port != UI_PORT:
        UI_PORT = args.port
        print(f"[*] Using custom port: {UI_PORT}")
    
    run()


if __name__ == "__main__":
    main()
