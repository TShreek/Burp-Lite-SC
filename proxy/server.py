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
    # Use a class-level session to persist cookies across all requests
    session = requests.Session()

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
            # Remove 'Host' header to let requests set it correctly
            headers.pop('Host', None)

            # Use the session to persist cookies
            if self.command == 'POST':
                response = self.session.post(target_url, data=body, headers=headers)
            else:
                response = self.session.get(target_url, headers=headers)

            # Log response
            print("[<] Response Code:", response.status_code)
            print("[<] Response Body:", response.text)
            print("[<] Session Cookies:", self.session.cookies.get_dict())
            
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
        import os, json, datetime, uuid
        log_entry = {
            "id": str(uuid.uuid4()),  # Add unique ID for each entry
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

        # Load existing array or start fresh
        data = []
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 0:
            try:
                with open(LOG_PATH, "r") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []

        data.append(log_entry)
        with open(LOG_PATH, "w") as f:
            json.dump(data, f, indent=2)

def run():
    with socketserver.ThreadingTCPServer(("", PROXY_PORT), ProxyHandler) as httpd:
        print(f"[*] Proxy running on port {PROXY_PORT} → forwarding to http://{TARGET_HOST}:{TARGET_PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
