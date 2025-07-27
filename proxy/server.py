import http.server
import socketserver
import requests
import os
import json
import datetime


PROXY_PORT = 8080
TARGET_HOST = 'localhost'
TARGET_PORT = 5000


LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'traffic.json')


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        # Read incoming request data
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else None

        # Rebuild the target URL (Flask app)
        target_url = f"http://{TARGET_HOST}:{TARGET_PORT}{self.path}"

        # Forward the request
        print(f"\n[+] {self.command} {self.path}")
        print("[>] Request Body:", body.decode() if body else "(empty)")

        headers = dict(self.headers)

        try:
            if self.command == 'POST':
                response = requests.post(target_url, data=body, headers=headers)
            else:
                response = requests.get(target_url, headers=headers)

            # Log response
            print("[<] Response Code:", response.status_code)
            print("[<] Response Body:", response.text)
            
            # Log the traffic to file
            self.log_to_file(self.command, self.path, headers, body, response)

            # Send back the response
            self.send_response(response.status_code)
            # Add security headers for our responses to demo the scanner
            self.send_header('X-Content-Type-Options', 'nosniff')
            # Deliberately omit some security headers to demonstrate the scanner
            # self.send_header('Content-Security-Policy', "default-src 'self'")
            # self.send_header('X-Frame-Options', 'DENY')
            
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)

        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

    def log_to_file(self, method, path, headers, request_body, response):
        log_entry = {
            "method": method,
            "path": path,
            "request_headers": dict(headers),
            "request_body": request_body.decode() if request_body else None,
            "response_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_body": response.text,
            "timestamp": datetime.datetime.now().isoformat()
        }

        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

        # Initialize JSON file if it doesn't exist or is empty
        if not os.path.exists(LOG_PATH) or os.path.getsize(LOG_PATH) == 0:
            with open(LOG_PATH, 'w') as f:
                f.write('[\n')
                f.write(json.dumps(log_entry, indent=2))
                f.write('\n]')
        else:
            # Read existing content, remove the closing bracket, add new entry
            with open(LOG_PATH, 'r') as f:
                content = f.read().rstrip().rstrip(']')
            
            with open(LOG_PATH, 'w') as f:
                f.write(content)
                f.write(',\n')
                f.write(json.dumps(log_entry, indent=2))
                f.write('\n]')

def run():
    with socketserver.ThreadingTCPServer(("", PROXY_PORT), ProxyHandler) as httpd:
        print(f"[*] Proxy running on port {PROXY_PORT} → forwarding to http://{TARGET_HOST}:{TARGET_PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
