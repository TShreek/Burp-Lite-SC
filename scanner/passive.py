"""
Passive Scanner for Burp-Lite
This module analyzes HTTP traffic for common security issues
"""
import json
import re
from typing import Dict, Any, List, Tuple

class PassiveScanner:
    def __init__(self):
        self.findings = []
    
    def scan_traffic(self, traffic_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scan a single traffic entry for security issues
        Returns a list of findings
        """
        self.findings = []
        
        # Run all scan rules against this traffic
        self._check_content_security_policy(traffic_entry)
        self._check_x_frame_options(traffic_entry)
        self._check_secure_cookies(traffic_entry)
        self._check_for_sensitive_info(traffic_entry)
        self._check_x_content_type_options(traffic_entry)
        self._check_server_header(traffic_entry)

        
        return self.findings
    
    def _check_content_security_policy(self, traffic: Dict[str, Any]) -> None:
        """Check if Content-Security-Policy header is missing"""
        if 'response_headers' not in traffic:
            return
            
        headers = {k.lower(): v for k, v in traffic['response_headers'].items()}
        if 'content-security-policy' not in headers:
            self.findings.append({
                'severity': 'Medium',
                'title': 'Missing Content-Security-Policy Header',
                'description': 'The Content-Security-Policy header is missing. This header helps prevent XSS attacks.',
                'url': traffic.get('path', 'Unknown'),
                'remediation': 'Add a Content-Security-Policy header to responses.'
            })
    
    def _check_x_frame_options(self, traffic: Dict[str, Any]) -> None:
        """Check if X-Frame-Options header is missing"""
        if 'response_headers' not in traffic:
            return
            
        headers = {k.lower(): v for k, v in traffic['response_headers'].items()}
        if 'x-frame-options' not in headers:
            self.findings.append({
                'severity': 'Low',
                'title': 'Missing X-Frame-Options Header',
                'description': 'The X-Frame-Options header is missing. This header helps prevent clickjacking attacks.',
                'url': traffic.get('path', 'Unknown'),
                'remediation': 'Add X-Frame-Options header with value DENY or SAMEORIGIN.'
            })
    
    def _check_secure_cookies(self, traffic: Dict[str, Any]) -> None:
        """Check for cookies without Secure or HttpOnly flags"""
        if 'response_headers' not in traffic:
            return
            
        headers = {k.lower(): v for k, v in traffic['response_headers'].items()}
        
        # Check for Set-Cookie headers
        cookie_headers = [headers[h] for h in headers if h == 'set-cookie']
        for cookie in cookie_headers:
            if 'httponly' not in cookie.lower():
                self.findings.append({
                    'severity': 'Medium',
                    'title': 'Cookie Without HttpOnly Flag',
                    'description': f'A cookie is set without the HttpOnly flag: {cookie}',
                    'url': traffic.get('path', 'Unknown'),
                    'remediation': 'Add HttpOnly flag to cookies to prevent access from JavaScript.'
                })
            
            if 'secure' not in cookie.lower():
                self.findings.append({
                    'severity': 'Medium',
                    'title': 'Cookie Without Secure Flag',
                    'description': f'A cookie is set without the Secure flag: {cookie}',
                    'url': traffic.get('path', 'Unknown'),
                    'remediation': 'Add Secure flag to cookies to prevent transmission over unencrypted connections.'
                })
    
    def _check_for_sensitive_info(self, traffic: Dict[str, Any]) -> None:
        """Check for sensitive information in responses"""
        if not traffic.get('response_body'):
            return
            
        response_body = str(traffic['response_body'])
        
        # Simple regex patterns for sensitive data
        patterns = {
            'Credit Card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'API Key Pattern': r'\b[a-zA-Z0-9]{32,45}\b',
            'AWS Key Pattern': r'AKIA[0-9A-Z]{16}',
            'Email Address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'Private Key': r'-----BEGIN [A-Z ]+ PRIVATE KEY-----'
        }
        
        for pattern_name, regex in patterns.items():
            matches = re.findall(regex, response_body)
            if matches:
                self.findings.append({
                    'severity': 'High',
                    'title': f'Potential {pattern_name} Disclosure',
                    'description': f'The response contains what appears to be sensitive {pattern_name} information',
                    'url': traffic.get('path', 'Unknown'),
                    'remediation': 'Remove sensitive information from responses.'
                })


def scan_traffic_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Scan all traffic entries in a file
    Returns a list of findings
    """
    all_findings = []
    scanner = PassiveScanner()
    
    try:
        with open(file_path, 'r') as f:
            traffic_data = json.load(f)
            
        if isinstance(traffic_data, list):
            for entry in traffic_data:
                findings = scanner.scan_traffic(entry)
                all_findings.extend(findings)
                
        return all_findings
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error scanning traffic file: {e}")
        return []
def _check_x_content_type_options(self, traffic: Dict[str, Any]) -> None:
    """Check if X-Content-Type-Options header is missing"""
    if 'response_headers' not in traffic:
        return

    headers = {k.lower(): v for k, v in traffic['response_headers'].items()}
    if 'x-content-type-options' not in headers:
        self.findings.append({
            'severity': 'Low',
            'title': 'Missing X-Content-Type-Options Header',
            'description': 'The X-Content-Type-Options header is missing. This header helps prevent MIME-sniffing attacks.',
            'url': traffic.get('path', 'Unknown'),
            'remediation': 'Add X-Content-Type-Options header with value nosniff.'
        })
def _check_server_header(self, traffic: Dict[str, Any]) -> None:
    """Warn if Server header leaks backend details"""
    if 'response_headers' not in traffic:
        return

    headers = {k.lower(): v for k, v in traffic['response_headers'].items()}
    server = headers.get('server')
    if server and any(keyword in server.lower() for keyword in ['apache', 'nginx', 'iis']):
        self.findings.append({
            'severity': 'Low',
            'title': 'Server Header Disclosure',
            'description': f'The Server header exposes backend details: {server}',
            'url': traffic.get('path', 'Unknown'),
            'remediation': 'Omit or mask the Server header to reduce fingerprinting.'
        })


if __name__ == "__main__":
    import os
    import sys
    
    log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'traffic.json')
    
    if not os.path.exists(log_path):
        print(f"Error: Traffic log file not found at {log_path}")
        sys.exit(1)
        
    print(f"Scanning traffic from {log_path}...")
    findings = scan_traffic_file(log_path)
    
    if findings:
        print(f"\n[!] Found {len(findings)} security issues:")
        for i, finding in enumerate(findings, 1):
            print(f"\n--- Finding #{i} ({finding['severity']}) ---")
            print(f"Title: {finding['title']}")
            print(f"URL: {finding['url']}")
            print(f"Description: {finding['description']}")
            print(f"Remediation: {finding['remediation']}")
    else:
        print("\n[✓] No security issues found")
