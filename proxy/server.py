import http.server
import socketserver
import requests
import os
import json


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

            # Send back the response
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)

        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

def run():
    with socketserver.ThreadingTCPServer(("", PROXY_PORT), ProxyHandler) as httpd:
        print(f"[*] Proxy running on port {PROXY_PORT} → forwarding to http://{TARGET_HOST}:{TARGET_PORT}")
        httpd.serve_forever()

def log_to_file(self, method, path, headers, request_body, response):
    log_entry = {
        "method": method,
        "path": path,
        "request_headers": dict(headers),
        "request_body": request_body.decode() if request_body else None,
        "response_code": response.status_code,
        "response_body": response.text
    }

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    with open(LOG_PATH, 'a') as f:
        f.write(json.dumps(log_entry, indent=2))
        f.write(",\n")  # Add comma for readability (not perfect JSON array)

if __name__ == "__main__":
    run()
