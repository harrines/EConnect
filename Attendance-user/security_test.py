#!/usr/bin/env python3
"""
Security Test Suite for E-Connect Role-Based Access Control
Tests the security fixes for the broken access bug
"""
import requests
import json
import time
from datetime import datetime

class SecurityTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.test_results = []

    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")

    def signin_as_admin(self, email="admin@test.com", password="admin123"):
        """Sign in as admin and get token"""
        try:
            response = requests.post(f"{self.base_url}/admin_signin", json={
                "email": email,
                "password": password
            })
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("jwt", {}).get("access_token")
                self.log_test("Admin Login", "PASS", "Admin login successful")
                return True
            else:
                self.log_test("Admin Login", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Login", "ERROR", str(e))
            return False

    def signin_as_user(self, email="user@test.com", password="user123"):
        """Sign in as regular user and get token"""
        try:
            response = requests.post(f"{self.base_url}/signin", json={
                "email": email,
                "password": password
            })
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("jwt", {}).get("access_token")
                self.log_test("User Login", "PASS", "User login successful")
                return True
            else:
                self.log_test("User Login", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Login", "ERROR", str(e))
            return False

    def test_admin_endpoint_without_auth(self, endpoint):
        """Test admin endpoint without authentication"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}")
            if response.status_code == 403:
                self.log_test(f"No Auth - {endpoint}", "PASS", "Access denied as expected")
                return True
            else:
                self.log_test(f"No Auth - {endpoint}", "FAIL", f"Expected 403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"No Auth - {endpoint}", "ERROR", str(e))
            return False

    def test_admin_endpoint_with_user_token(self, endpoint):
        """Test admin endpoint with user token (should be denied)"""
        if not self.user_token:
            self.log_test(f"User Token - {endpoint}", "SKIP", "No user token available")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            if response.status_code == 403:
                self.log_test(f"User Token - {endpoint}", "PASS", "Access denied as expected")
                return True
            else:
                self.log_test(f"User Token - {endpoint}", "FAIL", f"Expected 403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"User Token - {endpoint}", "ERROR", str(e))
            return False

    def test_admin_endpoint_with_admin_token(self, endpoint):
        """Test admin endpoint with admin token (should be allowed)"""
        if not self.admin_token:
            self.log_test(f"Admin Token - {endpoint}", "SKIP", "No admin token available")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            if response.status_code == 200:
                self.log_test(f"Admin Token - {endpoint}", "PASS", "Access granted as expected")
                return True
            else:
                self.log_test(f"Admin Token - {endpoint}", "FAIL", f"Expected 200, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"Admin Token - {endpoint}", "ERROR", str(e))
            return False

    def test_jwt_token_content(self):
        """Test if JWT tokens contain role information"""
        if not self.admin_token:
            self.log_test("JWT Role Content", "SKIP", "No admin token to test")
            return False

        try:
            import jwt
            import base64
            
            # Decode JWT without verification (just to check content)
            parts = self.admin_token.split('.')
            if len(parts) == 3:
                # Add padding if needed
                payload_part = parts[1]
                payload_part += '=' * (4 - len(payload_part) % 4)
                
                payload = json.loads(base64.b64decode(payload_part))
                if 'role' in payload:
                    self.log_test("JWT Role Content", "PASS", f"Role found: {payload['role']}")
                    return True
                else:
                    self.log_test("JWT Role Content", "FAIL", "No role in JWT payload")
                    return False
            else:
                self.log_test("JWT Role Content", "FAIL", "Invalid JWT format")
                return False
        except Exception as e:
            self.log_test("JWT Role Content", "ERROR", str(e))
            return False

    def run_comprehensive_test(self):
        """Run comprehensive security test suite"""
        print("🔒 Starting E-Connect Security Test Suite")
        print("=" * 50)

        # Admin endpoints to test
        admin_endpoints = [
            "/attendance/",
            "/all_users_leave_requests/?selectedOption=pending",
            "/manager_leave_requests/?selectedOption=pending",
            "/admin_page_remote_work_requests",
            "/get_all_users",
            "/admin_leave_notification_reminder"
        ]

        # Test 1: Authentication Tests
        print("\n📝 Testing Authentication...")
        admin_login_success = self.signin_as_admin()
        user_login_success = self.signin_as_user()

        # Test 2: JWT Content Test
        print("\n🔑 Testing JWT Token Content...")
        self.test_jwt_token_content()

        # Test 3: Endpoint Security Tests
        print("\n🛡️ Testing Endpoint Security...")
        for endpoint in admin_endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            
            # Test without authentication
            self.test_admin_endpoint_without_auth(endpoint)
            
            # Test with user token (should be denied)
            if user_login_success:
                self.test_admin_endpoint_with_user_token(endpoint)
            
            # Test with admin token (should be allowed)
            if admin_login_success:
                self.test_admin_endpoint_with_admin_token(endpoint)

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("📊 SECURITY TEST REPORT")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")

        success_rate = (passed_tests / (total_tests - skipped_tests)) * 100 if total_tests > skipped_tests else 0
        print(f"Success Rate: {success_rate:.1f}%")

        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['details']}")

        # Save detailed report
        report_filename = f"security_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "errors": error_tests,
                    "skipped": skipped_tests,
                    "success_rate": success_rate
                },
                "tests": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")

        return success_rate >= 80  # Consider 80%+ success rate as passing

if __name__ == "__main__":
    tester = SecurityTester()
    
    print("🚀 E-Connect Role-Based Access Control Security Test")
    print("This test validates that the broken access bug has been fixed.")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Security tests PASSED! The broken access bug appears to be fixed.")
        exit(0)
    else:
        print("\n⚠️  Security tests show issues. Review the failed tests above.")
        exit(1)
