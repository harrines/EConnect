#!/usr/bin/env python3
"""
E-Connect Security Testing - Phase 3: Data Security Testing
===========================================================
This module tests data security vulnerabilities including database security,
encryption, data leakage, and sensitive information handling.
"""

import requests
import json
import time
import base64
from datetime import datetime
import hashlib
import re
from urllib.parse import urljoin
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os

class Phase3DataSecurityTester:
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
    # Database Security Testing
    # ========================================================================
    
    def test_database_security(self):
        """Test database security configuration"""
        self.log_test("DATABASE", "Database Security Testing", "INFO", "Testing database security...")
        
        # Test MongoDB connection security
        self._test_mongodb_connection_security()
        
        # Test database injection vulnerabilities
        self._test_database_injection()
        
        # Test database access controls
        self._test_database_access_controls()
        
        # Test database information disclosure
        self._test_database_information_disclosure()
    
    def _test_mongodb_connection_security(self):
        """Test MongoDB connection security"""
        # Test common MongoDB ports and configurations
        mongodb_ports = [27017, 27018, 27019]
        mongodb_hosts = ["localhost", "127.0.0.1"]
        
        for host in mongodb_hosts:
            for port in mongodb_ports:
                try:
                    # Test unauthenticated access
                    client = pymongo.MongoClient(
                        host=host, 
                        port=port, 
                        serverSelectionTimeoutMS=2000,
                        connectTimeoutMS=2000
                    )
                    
                    # Try to list databases
                    databases = client.list_database_names()
                    
                    if databases:
                        self.log_test("DATABASE", f"MongoDB Security - {host}:{port}", "FAIL", 
                                    f"Unauthenticated database access possible. Databases: {databases[:3]}", "CRITICAL")
                    else:
                        self.log_test("DATABASE", f"MongoDB Security - {host}:{port}", "PASS", 
                                    "Database access properly restricted")
                    
                    client.close()
                    
                except (ConnectionFailure, ServerSelectionTimeoutError):
                    self.log_test("DATABASE", f"MongoDB Security - {host}:{port}", "PASS", 
                                "Database connection properly secured/not accessible")
                except Exception as e:
                    if "authentication failed" in str(e).lower():
                        self.log_test("DATABASE", f"MongoDB Security - {host}:{port}", "PASS", 
                                    "Authentication required - good security")
                    else:
                        self.log_test("DATABASE", f"MongoDB Security - {host}:{port}", "INFO", 
                                    f"Connection test result: {str(e)[:100]}")
    
    def _test_database_injection(self):
        """Test for NoSQL injection vulnerabilities"""
        nosql_payloads = [
            # MongoDB injection payloads
            {"$ne": None},
            {"$gt": ""},
            {"$where": "1==1"},
            {"$regex": ".*"},
            {"$exists": True},
            {"$or": [{"password": {"$ne": None}}]},
            {"$nin": [""]},
            {"$not": {"$eq": ""}},
            # Timing-based payloads
            {"$where": "sleep(5000) || true"},
            {"$regex": "^.*", "$options": "i"}
        ]
        
        # Test login endpoints with NoSQL injection
        for payload in nosql_payloads[:5]:  # Test first 5 payloads
            try:
                # Test in email field
                response = self.session.post(f"{self.base_url}/signin", json={
                    "email": payload,
                    "password": "test"
                })
                
                if response.status_code == 200 and "access_token" in response.text:
                    self.log_test("DATABASE", "NoSQL Injection - Login", "FAIL", 
                                f"Potential NoSQL injection bypass: {payload}", "CRITICAL")
                    return
                
                # Test in password field
                response = self.session.post(f"{self.base_url}/signin", json={
                    "email": "test@test.com",
                    "password": payload
                })
                
                if response.status_code == 200 and "access_token" in response.text:
                    self.log_test("DATABASE", "NoSQL Injection - Login", "FAIL", 
                                f"Potential NoSQL injection in password: {payload}", "CRITICAL")
                    return
                    
            except Exception as e:
                continue
        
        self.log_test("DATABASE", "NoSQL Injection - Login", "PASS", 
                    "No NoSQL injection vulnerabilities detected in login")
    
    def _test_database_access_controls(self):
        """Test database access control mechanisms"""
        # Test user data access controls
        user_ids_to_test = ["507f1f77bcf86cd799439011", "507f191e810c19729de860ea", "000000000000000000000000"]
        
        for user_id in user_ids_to_test:
            try:
                # Test direct user data access
                response = self.session.get(f"{self.base_url}/clock-records/{user_id}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "clock_records" in response_data and response_data["clock_records"]:
                        self.log_test("DATABASE", f"Data Access Control - {user_id}", "WARN", 
                                    "User data accessible without authentication", "MEDIUM")
                    else:
                        self.log_test("DATABASE", f"Data Access Control - {user_id}", "PASS", 
                                    "No data returned for unauthorized access")
                else:
                    self.log_test("DATABASE", f"Data Access Control - {user_id}", "PASS", 
                                f"Access properly restricted (Status: {response.status_code})")
                                
            except Exception as e:
                self.log_test("DATABASE", f"Data Access Control - {user_id}", "ERROR", str(e))
    
    def _test_database_information_disclosure(self):
        """Test for database information disclosure"""
        # Test endpoints that might leak database information
        info_endpoints = [
            "/",
            "/test",
            "/docs",
            "/openapi.json",
            "/health",
            "/status"
        ]
        
        for endpoint in info_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    response_text = response.text.lower()
                    
                    # Check for database information leakage
                    db_info_patterns = [
                        r"mongodb://",
                        r"database.*connection",
                        r"collection.*name",
                        r"db.*error",
                        r"mongo.*version",
                        r"connection.*string"
                    ]
                    
                    for pattern in db_info_patterns:
                        if re.search(pattern, response_text, re.IGNORECASE):
                            self.log_test("DATABASE", f"Information Disclosure - {endpoint}", "FAIL", 
                                        f"Database information exposed: {pattern}", "MEDIUM")
                            break
                    else:
                        self.log_test("DATABASE", f"Information Disclosure - {endpoint}", "PASS", 
                                    "No database information disclosed")
                        
            except Exception as e:
                self.log_test("DATABASE", f"Information Disclosure - {endpoint}", "ERROR", str(e))

    # ========================================================================
    # Data Encryption Testing
    # ========================================================================
    
    def test_data_encryption(self):
        """Test data encryption mechanisms"""
        self.log_test("ENCRYPTION", "Data Encryption Testing", "INFO", "Testing encryption mechanisms...")
        
        # Test password storage security
        self._test_password_storage()
        
        # Test data transmission encryption
        self._test_transmission_encryption()
        
        # Test sensitive data handling
        self._test_sensitive_data_handling()
    
    def _test_password_storage(self):
        """Test password storage security"""
        try:
            # Create test user to analyze password storage
            test_email = f"encryption_test_{int(time.time())}@test.com"
            test_password = "TestPassword123!"
            
            response = self.session.post(f"{self.base_url}/signup", json={
                "email": test_email,
                "password": test_password,
                "name": "Encryption Test User"
            })
            
            if response.status_code == 200:
                # Check if password is returned in response (should not be)
                response_text = response.text.lower()
                
                if test_password.lower() in response_text:
                    self.log_test("ENCRYPTION", "Password Storage", "FAIL", 
                                "Plain text password returned in signup response", "CRITICAL")
                elif "password" in response_text:
                    self.log_test("ENCRYPTION", "Password Storage", "WARN", 
                                "Password field present in response (check if hashed)", "MEDIUM")
                else:
                    self.log_test("ENCRYPTION", "Password Storage", "PASS", 
                                "Password not exposed in signup response")
                
                # Test login to see if plain text password works (it should)
                login_response = self.session.post(f"{self.base_url}/signin", json={
                    "email": test_email,
                    "password": test_password
                })
                
                if login_response.status_code == 200:
                    self.log_test("ENCRYPTION", "Password Verification", "PASS", 
                                "Password authentication working (likely hashed)")
                
            else:
                self.log_test("ENCRYPTION", "Password Storage", "INFO", 
                            f"Signup failed with status {response.status_code}")
                
        except Exception as e:
            self.log_test("ENCRYPTION", "Password Storage", "ERROR", str(e))
    
    def _test_transmission_encryption(self):
        """Test data transmission encryption"""
        # Check if HTTPS is enforced
        if self.base_url.startswith("https://"):
            self.log_test("ENCRYPTION", "Transmission Encryption", "PASS", 
                        "HTTPS in use for data transmission")
        else:
            self.log_test("ENCRYPTION", "Transmission Encryption", "FAIL", 
                        "HTTP in use - data transmitted in plain text", "HIGH")
        
        # Test HTTP to HTTPS redirect
        if self.base_url.startswith("http://"):
            try:
                https_url = self.base_url.replace("http://", "https://")
                response = self.session.get(https_url, timeout=5)
                
                if response.status_code == 200:
                    self.log_test("ENCRYPTION", "HTTPS Availability", "INFO", 
                                "HTTPS endpoint available - consider enforcing")
                else:
                    self.log_test("ENCRYPTION", "HTTPS Availability", "WARN", 
                                "HTTPS not available", "MEDIUM")
                    
            except Exception:
                self.log_test("ENCRYPTION", "HTTPS Availability", "WARN", 
                            "HTTPS not available or configured", "MEDIUM")
    
    def _test_sensitive_data_handling(self):
        """Test handling of sensitive data"""
        # Test JWT token exposure
        try:
            login_response = self.session.post(f"{self.base_url}/signin", json={
                "email": "test@test.com",
                "password": "wrongpassword"
            })
            
            if login_response.status_code != 200:
                self.log_test("ENCRYPTION", "Token Exposure", "PASS", 
                            "No token exposed in failed login")
            
            # Test for sensitive data in responses
            response = self.session.get(f"{self.base_url}/")
            sensitive_patterns = [
                r"password\s*[=:]\s*['\"][^'\"]+['\"]",
                r"secret\s*[=:]\s*['\"][^'\"]+['\"]",
                r"key\s*[=:]\s*['\"][^'\"]+['\"]",
                r"token\s*[=:]\s*['\"][^'\"]+['\"]"
            ]
            
            response_text = response.text
            for pattern in sensitive_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    self.log_test("ENCRYPTION", "Sensitive Data Exposure", "FAIL", 
                                f"Sensitive data pattern found: {pattern}", "HIGH")
                    break
            else:
                self.log_test("ENCRYPTION", "Sensitive Data Exposure", "PASS", 
                            "No obvious sensitive data patterns in responses")
                
        except Exception as e:
            self.log_test("ENCRYPTION", "Sensitive Data Handling", "ERROR", str(e))

    # ========================================================================
    # Data Leakage Testing
    # ========================================================================
    
    def test_data_leakage(self):
        """Test for data leakage vulnerabilities"""
        self.log_test("DATA_LEAKAGE", "Data Leakage Testing", "INFO", "Testing data leakage...")
        
        # Test for PII exposure
        self._test_pii_exposure()
        
        # Test for cross-user data access
        self._test_cross_user_data_access()
        
        # Test for data in error messages
        self._test_data_in_errors()
        
        # Test for data in logs/debug info
        self._test_debug_information_leakage()
    
    def _test_pii_exposure(self):
        """Test for Personally Identifiable Information exposure"""
        # Test endpoints that might expose PII
        pii_endpoints = [
            "/get_all_users",
            "/attendance/",
            "/all_users_leave_requests/",
            "/clock-records/test"
        ]
        
        for endpoint in pii_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    response_text = response.text
                    
                    # Check for PII patterns
                    pii_patterns = [
                        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
                        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN format
                        r"\b\d{10,15}\b",  # Phone numbers
                        r"\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b"  # Credit card format
                    ]
                    
                    pii_found = []
                    for pattern in pii_patterns:
                        matches = re.findall(pattern, response_text)
                        if matches:
                            pii_found.extend(matches[:2])  # Limit to first 2 matches
                    
                    if pii_found:
                        self.log_test("DATA_LEAKAGE", f"PII Exposure - {endpoint}", "FAIL", 
                                    f"PII detected: {pii_found[:2]}", "HIGH")
                    else:
                        self.log_test("DATA_LEAKAGE", f"PII Exposure - {endpoint}", "PASS", 
                                    "No obvious PII patterns detected")
                else:
                    self.log_test("DATA_LEAKAGE", f"PII Exposure - {endpoint}", "PASS", 
                                f"Endpoint properly protected (Status: {response.status_code})")
                                
            except Exception as e:
                self.log_test("DATA_LEAKAGE", f"PII Exposure - {endpoint}", "ERROR", str(e))
    
    def _test_cross_user_data_access(self):
        """Test for unauthorized cross-user data access"""
        # Test with different user IDs
        test_user_ids = [
            "507f1f77bcf86cd799439011",
            "507f191e810c19729de860ea", 
            "000000000000000000000001",
            "123456789012345678901234"
        ]
        
        for user_id in test_user_ids[:2]:  # Test first 2 IDs
            try:
                # Test leave history access
                response = self.session.get(f"{self.base_url}/leave-History/{user_id}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data and len(response_data) > 0:
                        self.log_test("DATA_LEAKAGE", f"Cross-User Access - {user_id}", "FAIL", 
                                    "User data accessible without authentication", "HIGH")
                    else:
                        self.log_test("DATA_LEAKAGE", f"Cross-User Access - {user_id}", "PASS", 
                                    "No data returned for unauthorized access")
                else:
                    self.log_test("DATA_LEAKAGE", f"Cross-User Access - {user_id}", "PASS", 
                                f"Access properly restricted (Status: {response.status_code})")
                                
            except Exception as e:
                self.log_test("DATA_LEAKAGE", f"Cross-User Access - {user_id}", "ERROR", str(e))
    
    def _test_data_in_errors(self):
        """Test for data exposure in error messages"""
        # Trigger various error conditions
        error_tests = [
            ("/signin", {"email": "nonexistent@test.com", "password": "test"}),
            ("/id", {"id": "invalid_id_format"}),
            ("/clock-records/invalid_user_id", {}),
            ("/leave-History/999999999999999999999999", {})
        ]
        
        for endpoint, data in error_tests:
            try:
                if data:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                else:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code >= 400:  # Error response
                    error_text = response.text.lower()
                    
                    # Check for sensitive information in errors
                    sensitive_info = [
                        "database",
                        "collection",
                        "mongo",
                        "connection",
                        "internal server error",
                        "stack trace",
                        "file path"
                    ]
                    
                    leaked_info = [info for info in sensitive_info if info in error_text]
                    
                    if leaked_info:
                        self.log_test("DATA_LEAKAGE", f"Error Information - {endpoint}", "FAIL", 
                                    f"Sensitive info in errors: {leaked_info}", "MEDIUM")
                    else:
                        self.log_test("DATA_LEAKAGE", f"Error Information - {endpoint}", "PASS", 
                                    "Clean error messages without sensitive data")
                        
            except Exception as e:
                self.log_test("DATA_LEAKAGE", f"Error Information - {endpoint}", "ERROR", str(e))
    
    def _test_debug_information_leakage(self):
        """Test for debug information leakage"""
        # Check common debug endpoints
        debug_endpoints = [
            "/debug",
            "/info",
            "/status",
            "/health",
            "/metrics",
            "/admin/debug"
        ]
        
        for endpoint in debug_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    debug_indicators = [
                        "debug",
                        "trace",
                        "stack",
                        "environment",
                        "config",
                        "variable"
                    ]
                    
                    response_text = response.text.lower()
                    found_indicators = [ind for ind in debug_indicators if ind in response_text]
                    
                    if found_indicators:
                        self.log_test("DATA_LEAKAGE", f"Debug Information - {endpoint}", "WARN", 
                                    f"Debug info exposed: {found_indicators}", "MEDIUM")
                    else:
                        self.log_test("DATA_LEAKAGE", f"Debug Information - {endpoint}", "INFO", 
                                    "Endpoint accessible but no obvious debug info")
                        
            except Exception as e:
                continue  # Debug endpoints are often not available

    # ========================================================================
    # Backup and Recovery Security
    # ========================================================================
    
    def test_backup_security(self):
        """Test backup and recovery security"""
        self.log_test("BACKUP", "Backup Security Testing", "INFO", "Testing backup security...")
        
        # Test for exposed backup files
        self._test_backup_file_exposure()
        
        # Test for database dumps
        self._test_database_dump_exposure()
    
    def _test_backup_file_exposure(self):
        """Test for exposed backup files"""
        backup_paths = [
            "/backup",
            "/backups",
            "/db_backup",
            "/dump",
            "/exports",
            "/.backup",
            "/backup.sql",
            "/database.bak",
            "/mongo_dump",
            "/data_export.json"
        ]
        
        for path in backup_paths[:5]:  # Test first 5 paths
            try:
                response = self.session.get(f"{self.base_url}{path}")
                
                if response.status_code == 200:
                    # Check if response looks like backup data
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if any(ct in content_type for ct in ['json', 'sql', 'dump', 'backup']):
                        self.log_test("BACKUP", f"Backup Exposure - {path}", "FAIL", 
                                    f"Backup file accessible: {content_type}", "HIGH")
                    else:
                        self.log_test("BACKUP", f"Backup Exposure - {path}", "INFO", 
                                    f"Path accessible but content unclear: {content_type}")
                else:
                    self.log_test("BACKUP", f"Backup Exposure - {path}", "PASS", 
                                f"Backup path properly protected (Status: {response.status_code})")
                                
            except Exception as e:
                self.log_test("BACKUP", f"Backup Exposure - {path}", "ERROR", str(e))
    
    def _test_database_dump_exposure(self):
        """Test for database dump exposure"""
        # Check for common database dump file patterns
        dump_extensions = ['.json', '.bson', '.sql', '.dump', '.backup']
        dump_names = ['users', 'database', 'mongo', 'attendance', 'employees']
        
        for name in dump_names[:2]:  # Test first 2 names
            for ext in dump_extensions[:2]:  # Test first 2 extensions
                dump_file = f"/{name}{ext}"
                
                try:
                    response = self.session.get(f"{self.base_url}{dump_file}")
                    
                    if response.status_code == 200 and len(response.content) > 100:
                        self.log_test("BACKUP", f"Database Dump - {dump_file}", "FAIL", 
                                    f"Potential database dump accessible: {len(response.content)} bytes", "CRITICAL")
                    else:
                        self.log_test("BACKUP", f"Database Dump - {dump_file}", "PASS", 
                                    "Database dump not accessible")
                        
                except Exception as e:
                    continue

    # ========================================================================
    # Main Test Runner
    # ========================================================================
    
    def run_phase3_tests(self):
        """Run all Phase 3 data security tests"""
        print("🔒 Starting Phase 3: Data Security Testing")
        print("=" * 70)
        
        print("\n🗄️ Testing Database Security...")
        self.test_database_security()
        
        print("\n🔐 Testing Data Encryption...")
        self.test_data_encryption()
        
        print("\n📊 Testing Data Leakage...")
        self.test_data_leakage()
        
        print("\n💾 Testing Backup Security...")
        self.test_backup_security()
        
        # Generate summary report
        self._generate_phase3_report()
    
    def _generate_phase3_report(self):
        """Generate Phase 3 security test report"""
        print("\n" + "="*70)
        print("📊 PHASE 3 DATA SECURITY TEST SUMMARY")
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
            print(f"\n🚨 CRITICAL DATA SECURITY ISSUES: {len(critical_issues)}")
            for issue in critical_issues[:5]:
                print(f"  • {issue['category']} - {issue['test_name']}: {issue['details']}")
        
        # Security score
        if total_tests > 0:
            security_score = (passed / total_tests) * 100
            print(f"\n🎯 Data Security Score: {security_score:.1f}%")
        
        # Data security recommendations
        self._generate_data_security_recommendations(failed, critical_issues)
        
        # Save detailed report
        with open("phase3_data_security_report.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\nDetailed report saved to: phase3_data_security_report.json")
        print("="*70)
    
    def _generate_data_security_recommendations(self, failed_tests, critical_issues):
        """Generate data security recommendations"""
        print(f"\n💡 DATA SECURITY RECOMMENDATIONS:")
        
        if failed_tests == 0:
            print("  🎉 Excellent! No data security issues detected.")
            print("  🔄 Continue monitoring and regular security assessments.")
        else:
            print("  🔧 Address the following data security priorities:")
            
            if any("DATABASE" in issue["category"] for issue in critical_issues):
                print("  1. 🗄️ Secure database configuration")
                print("     - Implement authentication on MongoDB")
                print("     - Restrict database network access")
                print("     - Enable database encryption at rest")
            
            if any("ENCRYPTION" in issue["category"] for issue in critical_issues):
                print("  2. 🔐 Implement data encryption")
                print("     - Enforce HTTPS for all communications")
                print("     - Encrypt sensitive data at rest")
                print("     - Use strong password hashing (bcrypt/scrypt)")
            
            if any("DATA_LEAKAGE" in issue["category"] for issue in critical_issues):
                print("  3. 📊 Prevent data leakage")
                print("     - Implement proper access controls")
                print("     - Sanitize error messages")
                print("     - Remove debug information from production")
            
            if any("BACKUP" in issue["category"] for issue in critical_issues):
                print("  4. 💾 Secure backup processes")
                print("     - Encrypt backup files")
                print("     - Secure backup storage location")
                print("     - Implement backup access controls")

if __name__ == "__main__":
    tester = Phase3DataSecurityTester()
    tester.run_phase3_tests()
