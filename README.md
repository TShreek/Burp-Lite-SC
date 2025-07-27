# 🛡️ Burp-Lite with Passive Scanner

A lightweight HTTP intercepting proxy that logs requests and responses, and passively scans for basic web vulnerabilities — inspired by Burp Suite.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start Flask backend
python3 flask_app/app.py

# Terminal 2: Start proxy server
python3 proxy/server.py

# Terminal 3: Start UI server (optional, for web interface)
python3 ui/server.py

# Terminal 4: Generate test traffic
python3 test_client/run_test.py
```

Traffic will be intercepted and logged to `logs/traffic.json`. View the web interface at http://localhost:8081/index.html

## 📋 Project Overview

Burp-Lite is a Python-based HTTP proxy designed for learning, research, and demo purposes. It acts as a man-in-the-middle between a client and server, allowing you to:

- 🔍 **Intercept HTTP traffic**
- 📝 **Log requests and responses**
- 🔒 **Analyze traffic for common security misconfigurations**
- 🧩 **Build your own scanning rules**

## 🤔 Why This Project?

This tool was built as a hands-on way to understand:

- How intercepting proxies like Burp Suite and mitmproxy work
- HTTP protocol and headers
- Common security issues in web apps
- How to structure a vulnerability scanner

It's ideal for:
- 📚 **Cybersecurity learners**
- 👨‍💻 **Security engineers**
- 💼 **Interview/demo portfolios**

## 🔄 Architecture Flow

```
Client (curl or browser)
   ↓
Burp-Lite Proxy (localhost:8080)
   ↓
Flask App Server (localhost:5000)
   ↑
Proxy logs & scanner runs
   ↑
Response back to client
```

## ✨ Features

| Feature | Status | Description |
|---------|--------|-------------|
| HTTP Intercepting Proxy | ✅ | Intercepts and forwards HTTP requests |
| Traffic Logging | ✅ | Logs to console and logs/traffic.json in structured format |
| Passive Vulnerability Scanner | ✅ | Analyzes traffic for security issues (headers, sensitive data) |
| Test Client | ✅ | Simulates traffic for testing and demonstration |
| Web Dashboard | ✅ | View traffic and security findings in a browser interface |
| Request/Response Tampering | 🔜 | Modify requests on-the-fly |
| HTTPS/TLS Interception | 🔜 | Support for HTTPS traffic |

## 🚀 How to Run

### 1. Clone this repository
```bash
git clone https://github.com/TShreek/Burp-Lite-with-Scanner.git
cd Burp-Lite-with-Scanner
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Flask backend (in one terminal)
```bash
python3 flask_app/app.py
```
You should see a message indicating the Flask app is running on port 5000.

### 4. Start the proxy server (in another terminal)
```bash
python3 proxy/server.py
```
This will start the proxy on port 8080 that forwards requests to the Flask app.

### 5. Start the UI server (in a third terminal)
```bash
python3 ui/server.py
```
The UI server will run on port 8081 by default.

If port 8081 is already in use, you can specify a different port:
```bash
python3 ui/server.py --port 8082
```

### 6. Send requests through the proxy
You can either:

A. Use the test client to simulate traffic:
```bash
python3 test_client/run_test.py
```

B. Or send individual requests using curl:
```bash
curl -X POST http://localhost:8080/send \
-H "Content-Type: application/json" \
-d '{"from": "Alice", "to": "Bob", "message": "Hello from Burp-Lite!"}'
```

### 7. View intercepted traffic
You have two options to view traffic:

A. **Web Dashboard**: Open your browser to [http://localhost:8081/index.html](http://localhost:8081/index.html)
   - Click "Load Traffic" to refresh the view
   - Click on any request to see details
   - Click "Clear All" to reset the traffic log file
   
B. **Command Line**: The proxy will log all traffic to the console

### 8. Run the scanner (optional)
To analyze the captured traffic for security issues:
```bash
python3 scanner/passive.py
```
The scanner results will also appear in the web dashboard for each request.

## 📁 Folder Structure

```
Burp-Lite-with-Scanner/
├── flask_app/        → Flask backend (app.py)
├── proxy/            → Proxy logic (server.py)
├── scanner/          → Passive scanner logic (passive.py)
├── logs/             → Intercepted traffic (traffic.json)
├── ui/               → Web dashboard interface
│   ├── index.html    → Main HTML interface
│   ├── styles.css    → CSS styling
│   ├── scripts.js    → JavaScript functionality
│   └── server.py     → UI server
├── test_client/      → Test message script
├── requirements.txt
└── README.md
```

## ⚙️ Requirements & Dependencies

- Python 3.7+
- Flask 2.0.1
- Requests 2.26.0
- Werkzeug 2.0.1

## 🛠️ Troubleshooting

- **Flask Import Error**: If you encounter `ImportError: cannot import name 'url_quote'`, run:
  ```bash
  pip install werkzeug==2.0.1 flask==2.0.1
  ```

- **Empty Traffic Log**: If no traffic is being logged, ensure all components are running:
  1. Flask app on port 5000
  2. Proxy server on port 8080
  3. Check that requests are going through the proxy (http://localhost:8080)

- **UI Server Port Already in Use**: If you get "Address already in use" when starting the UI server:
  ```bash
  python3 ui/server.py --port 8082
  ```

- **UI Not Showing Traffic**: If the UI dashboard doesn't display traffic:
  1. Click the "Load Traffic" button to manually refresh
  2. Check browser console (F12) for any JavaScript errors
  3. Verify the traffic.json file has content: `cat logs/traffic.json | head`
  4. Try a hard refresh (Ctrl+Shift+R or Cmd+Shift+R on Mac)

- **Case-Sensitive Filenames**: Ensure file references match exact case (app.py vs App.py)

## 🔍 Passive Scanner Rules

The scanner currently checks for:

- 🚫 Missing Content-Security-Policy
- 🚫 Missing X-Frame-Options
- 🔑 Insecure Set-Cookie flags (Secure, HttpOnly)
- 🔒 Potential sensitive information disclosure

## 🎓 Learning Outcomes

- Build an intercepting proxy with Python
- Understand request/response flow
- Learn HTTP header security best practices
- Structure a vulnerability scanning system
- Create a web interface for security tools

## 📜 License
MIT License. Use for learning and ethical purposes only.

## 🙏 Credits

- Built using Python 3 and Flask
- Inspired by Burp Suite and mitmproxy

