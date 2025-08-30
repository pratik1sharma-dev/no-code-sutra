"""
Security testing script for the Railway backend
"""
import requests
import time
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your Railway URL when deployed
DEMO_CREDENTIALS = {
    "admin": {"username": "admin", "password": "admin123"},
    "user": {"username": "user", "password": "user123"}
}

class SecurityTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.tokens = {}
    
    def test_health_endpoint(self):
        """Test basic health endpoint"""
        print("🔍 Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            assert response.status_code == 200
            print("✅ Health endpoint working")
            return True
        except Exception as e:
            print(f"❌ Health endpoint failed: {e}")
            return False
    
    def test_authentication(self):
        """Test JWT authentication"""
        print("\n🔍 Testing authentication...")
        
        # Test login with valid credentials
        for role, creds in DEMO_CREDENTIALS.items():
            try:
                response = self.session.post(
                    f"{self.base_url}/api/auth/login",
                    json=creds
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data["access_token"]
                    print(f"✅ Login successful for {role}")
                else:
                    print(f"❌ Login failed for {role}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Login error for {role}: {e}")
        
        # Test login with invalid credentials
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "invalid", "password": "invalid"}
            )
            assert response.status_code == 401
            print("✅ Invalid credentials properly rejected")
        except Exception as e:
            print(f"❌ Invalid credentials test failed: {e}")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        print("\n🔍 Testing rate limiting...")
        
        # Test auth endpoint rate limiting (10 requests per 5 minutes)
        print("Testing auth rate limiting...")
        for i in range(12):  # Exceed the limit
            try:
                response = self.session.post(
                    f"{self.base_url}/api/auth/login",
                    json={"username": "test", "password": "test"}
                )
                
                if response.status_code == 429:
                    print(f"✅ Rate limiting triggered after {i+1} requests")
                    break
                elif i == 11:
                    print("⚠️ Rate limiting not triggered (might be disabled)")
                    
            except Exception as e:
                print(f"❌ Rate limiting test error: {e}")
                break
    
    def test_security_headers(self):
        """Test security headers"""
        print("\n🔍 Testing security headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            headers = response.headers
            
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Content-Security-Policy",
                "Referrer-Policy"
            ]
            
            for header in security_headers:
                if header in headers:
                    print(f"✅ {header}: {headers[header]}")
                else:
                    print(f"❌ Missing security header: {header}")
                    
        except Exception as e:
            print(f"❌ Security headers test failed: {e}")
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🔍 Testing CORS configuration...")
        
        try:
            # Test preflight request
            response = self.session.options(
                f"{self.base_url}/api/workflows/generate",
                headers={
                    "Origin": "https://malicious-site.com",
                    "Access-Control-Request-Method": "POST"
                }
            )
            
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            if cors_origin and cors_origin != "*":
                print(f"✅ CORS properly configured: {cors_origin}")
            else:
                print("⚠️ CORS might be too permissive")
                
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
    
    def test_input_validation(self):
        """Test input validation and XSS protection"""
        print("\n🔍 Testing input validation...")
        
        malicious_payloads = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "javascript:alert('xss')"
        ]
        
        for payload in malicious_payloads:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/workflows/generate",
                    json={"prompt": payload}
                )
                
                if response.status_code == 400:
                    print(f"✅ Malicious payload blocked: {payload[:20]}...")
                elif response.status_code == 429:
                    print(f"✅ Rate limited (expected): {payload[:20]}...")
                else:
                    print(f"⚠️ Payload not blocked: {payload[:20]}...")
                    
            except Exception as e:
                print(f"❌ Input validation test error: {e}")
    
    def test_authenticated_endpoints(self):
        """Test endpoints that require authentication"""
        print("\n🔍 Testing authenticated endpoints...")
        
        # Test without authentication
        try:
            response = self.session.post(
                f"{self.base_url}/api/workflows/save",
                json={"id": "test", "name": "test", "data": {}}
            )
            
            if response.status_code in [401, 403]:
                print("✅ Protected endpoint requires authentication")
            else:
                print(f"⚠️ Protected endpoint accessible without auth: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Authentication test error: {e}")
        
        # Test with authentication
        if "admin" in self.tokens:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/workflows/save",
                    json={"id": "test", "name": "test", "data": {}},
                    headers={"Authorization": f"Bearer {self.tokens['admin']}"}
                )
                
                if response.status_code == 200:
                    print("✅ Authenticated request successful")
                else:
                    print(f"⚠️ Authenticated request failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Authenticated request error: {e}")
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🛡️ Starting Security Tests for Railway Backend\n")
        
        tests = [
            self.test_health_endpoint,
            self.test_authentication,
            self.test_rate_limiting,
            self.test_security_headers,
            self.test_cors_configuration,
            self.test_input_validation,
            self.test_authenticated_endpoints
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed: {e}")
                results.append(False)
        
        print(f"\n📊 Test Results: {sum(1 for r in results if r)} passed, {len(results) - sum(1 for r in results if r)} failed")
        print("🛡️ Security testing complete!")

if __name__ == "__main__":
    print("🔧 Security Testing Script")
    print("Make sure your backend is running before starting tests")
    print(f"Testing against: {BASE_URL}")
    
    input("Press Enter to start tests...")
    
    tester = SecurityTester(BASE_URL)
    tester.run_all_tests()
