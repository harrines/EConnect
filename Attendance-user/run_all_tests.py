#!/usr/bin/env python3
"""
E-Connect Master Test Runner
Executes all test suites for comprehensive deployment testing
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MasterTestRunner:
    def __init__(self):
        self.test_results = {}
        self.overall_status = "UNKNOWN"
        
    def run_command(self, command, description, timeout=300):
        """Run a command and capture its output"""
        print(f"\n{Colors.CYAN}🔄 {description}...{Colors.END}")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ {description} completed successfully ({duration:.1f}s){Colors.END}")
                return True, result.stdout, result.stderr
            else:
                print(f"{Colors.RED}❌ {description} failed ({duration:.1f}s){Colors.END}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                return False, result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ {description} timed out after {timeout}s{Colors.END}")
            return False, "", "Timeout"
        except Exception as e:
            print(f"{Colors.RED}❌ {description} error: {str(e)}{Colors.END}")
            return False, "", str(e)

    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print(f"{Colors.BOLD}{Colors.BLUE}🔍 Checking Prerequisites{Colors.END}")
        
        prerequisites = [
            ("python --version", "Python installation"),
            ("python -c \"import requests; print('requests OK')\"", "Python requests library"),
            ("python -c \"import pymongo; print('pymongo OK')\"", "Python pymongo library"),
            ("python -c \"import pytz; print('pytz OK')\"", "Python pytz library"),
        ]
        
        all_good = True
        for command, description in prerequisites:
            success, stdout, stderr = self.run_command(command, f"Checking {description}", timeout=10)
            if not success:
                all_good = False
                print(f"   {Colors.RED}Missing: {description}{Colors.END}")
            else:
                print(f"   {Colors.GREEN}✓ {description}: {stdout.strip()}{Colors.END}")
        
        return all_good

    def check_services(self):
        """Check if required services are running"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Checking Required Services{Colors.END}")
        
        services = [
            ("python -c \"import requests; r=requests.get('http://localhost:8000/test', timeout=5); print('Backend:', r.status_code == 200)\"", "Backend Server (Port 8000)"),
            ("python -c \"import requests; r=requests.get('http://localhost:5173', timeout=5); print('Frontend:', r.status_code == 200)\"", "Frontend Server (Port 5173)"),
            ("python -c \"from pymongo import MongoClient; c=MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000); print('MongoDB:', c.admin.command('ping'))\"", "MongoDB (Port 27017)"),
        ]
        
        all_services_running = True
        for command, description in services:
            success, stdout, stderr = self.run_command(command, f"Checking {description}", timeout=10)
            if success and "True" in stdout:
                print(f"   {Colors.GREEN}✓ {description} is running{Colors.END}")
            else:
                all_services_running = False
                print(f"   {Colors.RED}✗ {description} is not accessible{Colors.END}")
                if stderr:
                    print(f"     Error: {stderr}")
        
        return all_services_running

    def run_backend_tests(self):
        """Run backend API tests"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🔧 Running Backend API Tests{Colors.END}")
        
        success, stdout, stderr = self.run_command(
            "python backend/test_backend_api.py",
            "Backend API Test Suite",
            timeout=180
        )
        
        self.test_results['backend'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        # Try to parse the test report
        try:
            if os.path.exists("backend_test_report.json"):
                with open("backend_test_report.json", 'r') as f:
                    report = json.load(f)
                    success_rate = report.get('summary', {}).get('success_rate', 0)
                    print(f"   Backend Test Success Rate: {success_rate:.1f}%")
                    self.test_results['backend']['success_rate'] = success_rate
        except Exception as e:
            print(f"   Could not parse backend test report: {e}")
        
        return success

    def run_frontend_tests(self):
        """Run frontend tests"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🎨 Running Frontend Tests{Colors.END}")
        
        # Check if selenium is available
        selenium_check, _, _ = self.run_command(
            "python -c \"import selenium; print('Selenium available')\"",
            "Checking Selenium availability",
            timeout=10
        )
        
        if not selenium_check:
            print(f"{Colors.YELLOW}⚠️ Selenium not available, skipping automated frontend tests{Colors.END}")
            print(f"   Install with: pip install selenium")
            print(f"   And download ChromeDriver from: https://chromedriver.chromium.org/")
            self.test_results['frontend'] = {
                'success': False,
                'output': '',
                'error': 'Selenium not available',
                'skipped': True
            }
            return False
        
        success, stdout, stderr = self.run_command(
            "python test_frontend.py",
            "Frontend Test Suite",
            timeout=180
        )
        
        self.test_results['frontend'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        # Try to parse the test report
        try:
            if os.path.exists("frontend_test_report.json"):
                with open("frontend_test_report.json", 'r') as f:
                    report = json.load(f)
                    success_rate = report.get('summary', {}).get('success_rate', 0)
                    print(f"   Frontend Test Success Rate: {success_rate:.1f}%")
                    self.test_results['frontend']['success_rate'] = success_rate
        except Exception as e:
            print(f"   Could not parse frontend test report: {e}")
        
        return success

    def run_integration_tests(self):
        """Run integration tests"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🔗 Running Integration Tests{Colors.END}")
        
        success, stdout, stderr = self.run_command(
            "python test_integration.py",
            "Integration Test Suite",
            timeout=300
        )
        
        self.test_results['integration'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        # Try to parse the test report
        try:
            if os.path.exists("integration_test_report.json"):
                with open("integration_test_report.json", 'r') as f:
                    report = json.load(f)
                    success_rate = report.get('summary', {}).get('success_rate', 0)
                    print(f"   Integration Test Success Rate: {success_rate:.1f}%")
                    self.test_results['integration']['success_rate'] = success_rate
        except Exception as e:
            print(f"   Could not parse integration test report: {e}")
        
        return success

    def run_performance_tests(self):
        """Run basic performance tests"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}⚡ Running Performance Tests{Colors.END}")
        
        # Simple load test
        performance_script = """
import requests
import time
import concurrent.futures
import statistics

def test_endpoint(url):
    start = time.time()
    try:
        response = requests.get(url, timeout=10)
        return time.time() - start, response.status_code == 200
    except:
        return time.time() - start, False

def load_test():
    url = "http://localhost:8000/test"
    results = []
    success_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_endpoint, url) for _ in range(50)]
        for future in concurrent.futures.as_completed(futures):
            duration, success = future.result()
            results.append(duration)
            if success:
                success_count += 1
    
    avg_time = statistics.mean(results)
    max_time = max(results)
    min_time = min(results)
    success_rate = (success_count / len(results)) * 100
    
    print(f"Load Test Results:")
    print(f"  Requests: {len(results)}")
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"  Average Response Time: {avg_time:.3f}s")
    print(f"  Min Response Time: {min_time:.3f}s")
    print(f"  Max Response Time: {max_time:.3f}s")
    
    return success_rate > 95 and avg_time < 1.0

if __name__ == "__main__":
    success = load_test()
    exit(0 if success else 1)
"""
        
        # Write and run performance test
        with open("temp_performance_test.py", "w") as f:
            f.write(performance_script)
        
        success, stdout, stderr = self.run_command(
            "python temp_performance_test.py",
            "Performance Test Suite",
            timeout=120
        )
        
        # Clean up
        try:
            os.remove("temp_performance_test.py")
        except:
            pass
        
        self.test_results['performance'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        return success

    def generate_final_report(self):
        """Generate final deployment readiness report"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Generating Final Report{Colors.END}")
        
        # Calculate overall status
        test_suites = ['backend', 'integration', 'performance']
        passed_tests = 0
        total_tests = 0
        
        for suite in test_suites:
            if suite in self.test_results:
                total_tests += 1
                if self.test_results[suite]['success']:
                    passed_tests += 1
        
        # Include frontend if it was tested
        if 'frontend' in self.test_results and not self.test_results['frontend'].get('skipped', False):
            total_tests += 1
            if self.test_results['frontend']['success']:
                passed_tests += 1
        
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Determine deployment readiness
        if overall_success_rate >= 90:
            self.overall_status = "READY"
            status_color = Colors.GREEN
            status_icon = "🎉"
        elif overall_success_rate >= 75:
            self.overall_status = "CAUTION"
            status_color = Colors.YELLOW
            status_icon = "⚠️"
        else:
            self.overall_status = "NOT_READY"
            status_color = Colors.RED
            status_icon = "🚨"
        
        # Generate comprehensive report
        report = {
            "timestamp": datetime.now(IST).isoformat(),
            "overall_status": self.overall_status,
            "overall_success_rate": overall_success_rate,
            "test_results": self.test_results,
            "deployment_checklist": {
                "backend_api": self.test_results.get('backend', {}).get('success', False),
                "frontend_ui": self.test_results.get('frontend', {}).get('success', False),
                "integration": self.test_results.get('integration', {}).get('success', False),
                "performance": self.test_results.get('performance', {}).get('success', False),
            },
            "recommendations": self.get_recommendations()
        }
        
        # Save report
        with open("deployment_readiness_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{status_color}{status_icon} DEPLOYMENT READINESS REPORT {status_icon}{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Overall Status: {status_color}{self.overall_status}{Colors.END}")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"Timestamp: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
        
        print(f"\n{Colors.BOLD}Test Suite Results:{Colors.END}")
        for suite, result in self.test_results.items():
            if result.get('skipped'):
                print(f"  {Colors.YELLOW}⏭️ {suite.title()}: SKIPPED{Colors.END}")
            elif result['success']:
                success_rate = result.get('success_rate', 'N/A')
                print(f"  {Colors.GREEN}✅ {suite.title()}: PASSED ({success_rate}%){Colors.END}")
            else:
                print(f"  {Colors.RED}❌ {suite.title()}: FAILED{Colors.END}")
        
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        print(f"\n{Colors.BLUE}📁 Detailed reports saved to:{Colors.END}")
        print(f"  • deployment_readiness_report.json")
        print(f"  • backend_test_report.json")
        print(f"  • frontend_test_report.json")
        print(f"  • integration_test_report.json")
        
        return self.overall_status

    def get_recommendations(self):
        """Get deployment recommendations based on test results"""
        recommendations = []
        
        if not self.test_results.get('backend', {}).get('success', False):
            recommendations.append("❌ Fix backend API issues before deployment")
        
        if not self.test_results.get('integration', {}).get('success', False):
            recommendations.append("❌ Resolve integration test failures")
        
        if not self.test_results.get('performance', {}).get('success', False):
            recommendations.append("⚠️ Optimize performance for production load")
        
        if self.test_results.get('frontend', {}).get('skipped', False):
            recommendations.append("⚠️ Install Selenium for frontend testing")
        
        if self.overall_status == "READY":
            recommendations.extend([
                "✅ All critical tests passing - System ready for deployment",
                "🔧 Ensure production environment matches test environment",
                "📊 Set up monitoring and logging in production",
                "🔐 Verify SSL certificates for production domain",
                "💾 Ensure database backups are configured"
            ])
        elif self.overall_status == "CAUTION":
            recommendations.extend([
                "⚠️ Review failed tests and consider fixes",
                "🧪 Run additional manual testing",
                "📋 Document known issues for production monitoring"
            ])
        else:
            recommendations.extend([
                "🚨 Do not deploy - critical issues found",
                "🔧 Fix all failing tests before deployment",
                "🧪 Re-run full test suite after fixes"
            ])
        
        return recommendations

    def run_all_tests(self):
        """Run complete test suite"""
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 E-Connect Deployment Testing Suite{Colors.END}")
        print(f"Starting comprehensive testing at {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
        print("="*70)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print(f"{Colors.RED}❌ Prerequisites not met. Cannot continue.{Colors.END}")
            return "NOT_READY"
        
        # Check services
        if not self.check_services():
            print(f"{Colors.RED}❌ Required services not running. Cannot continue.{Colors.END}")
            print(f"\n{Colors.YELLOW}Please ensure:{Colors.END}")
            print(f"  • Backend server: python backend/Server.py")
            print(f"  • Frontend server: cd frontend && npm run dev")
            print(f"  • MongoDB: mongod")
            return "NOT_READY"
        
        # Run test suites
        self.run_backend_tests()
        self.run_frontend_tests()
        self.run_integration_tests()
        self.run_performance_tests()
        
        # Generate final report
        return self.generate_final_report()

def main():
    """Main entry point"""
    print(f"{Colors.PURPLE}🧪 Starting E-Connect Master Test Suite...{Colors.END}")
    
    runner = MasterTestRunner()
    status = runner.run_all_tests()
    
    print(f"\n{Colors.BLUE}🏁 Testing completed with status: {status}{Colors.END}")
    
    # Exit with appropriate code
    if status == "READY":
        sys.exit(0)
    elif status == "CAUTION":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
