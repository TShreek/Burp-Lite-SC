import requests
from typing import List, Dict, Any

class ActiveScanner:
    def __init__(self):
        self.payloads = {
            "xss": "<script>alert(1)</script>",
            "sql": "' OR '1'='1",
            "traversal": "../../../../etc/passwd"
        }

    def scan(self, base_url: str, method: str, path: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        findings = []
        target_url = base_url.rstrip("/") + path

        for vuln_type, payload in self.payloads.items():
            if method.upper() != "GET":
                continue  # Basic GET-based scanner

            try:
                # Inject payload in query param
                test_url = f"{target_url}?test={payload}"
                response = requests.get(test_url, headers=headers, timeout=5)

                if vuln_type == "xss" and payload in response.text:
                    findings.append({
                        "severity": "High",
                        "title": "Reflected XSS Detected",
                        "url": test_url,
                        "description": "Payload reflected in response",
                        "remediation": "Escape user input in output."
                    })

                if vuln_type == "sql" and "syntax" in response.text.lower():
                    findings.append({
                        "severity": "High",
                        "title": "Possible SQL Injection",
                        "url": test_url,
                        "description": "SQL error message found",
                        "remediation": "Use parameterized queries."
                    })

                if vuln_type == "traversal" and "root:" in response.text:
                    findings.append({
                        "severity": "Critical",
                        "title": "Directory Traversal Detected",
                        "url": test_url,
                        "description": "Unix password file content found",
                        "remediation": "Sanitize file path inputs."
                    })

            except Exception as e:
                continue

        return findings
