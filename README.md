# 🛡️ Burp-Lite with Passive Scanner

A lightweight HTTP intercepting proxy that logs requests and responses, and passively scans for basic web vulnerabilities — inspired by Burp Suite.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

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
| Traffic Logging | ✅ | Logged to logs/traffic.json in structured format |
| Passive Vulnerability Scanner | ✅ | Analyzes traffic for security issues |
| Web Dashboard | ✅ | View traffic and security findings |
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

### 4. Start the proxy server (in another terminal)
```bash
python3 proxy/server.py
```

### 5. Start the UI server (in a third terminal)
```bash
python3 ui/server.py
```

### 6. Send test traffic using the test client
```bash
python3 test_client/run_test.py
```

### 7. View the dashboard
Open your browser to: [http://localhost:8081/dashboard.html](http://localhost:8081/dashboard.html)

## 📁 Folder Structure

```
Burp-Lite-with-Scanner/
├── flask_app/        → Flask backend (app.py)
├── proxy/            → Proxy logic (server.py)
├── scanner/          → Passive scanner logic (passive.py)
├── logs/             → Intercepted traffic (traffic.json)
├── ui/               → Web dashboard interface
├── test_client/      → Test message script
├── requirements.txt
└── README.md
```

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

