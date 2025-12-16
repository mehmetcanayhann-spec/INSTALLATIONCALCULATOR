import requests
import sys
import json
from datetime import datetime

class RacingFencePricingAPITester:
    def __init__(self, base_url="https://meter-price-tool.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200 and "Racing Fence Installation Pricing API" in response.text
            self.log_test("Root API Endpoint", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Root API Endpoint", False, str(e))
            return False

    def test_countries_endpoint(self):
        """Test countries endpoint"""
        try:
            response = requests.get(f"{self.api_url}/countries", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                countries = data.get("countries", [])
                expected_countries = ["United Kingdom", "Germany", "United States", "Australia"]
                has_expected = all(country in countries for country in expected_countries)
                success = success and has_expected and len(countries) > 20
                
            self.log_test("Countries Endpoint", success, f"Status: {response.status_code}, Countries count: {len(countries) if success else 0}")
            return success, countries if success else []
        except Exception as e:
            self.log_test("Countries Endpoint", False, str(e))
            return False, []

    def test_calculate_endpoint_or_fence(self):
        """Test calculation endpoint with OR fence type"""
        try:
            payload = {
                "user_name": "Test User",
                "project_name": "Test Project OR",
                "country": "United Kingdom",
                "fence_type": "OR",
                "meters": 272.0,
                "gates": 4
            }
            
            response = requests.post(f"{self.api_url}/calculate", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                calc = data.get("calculation", {})
                breakdown = calc.get("breakdown", {})
                
                # Verify calculation formula
                # work_days = (meters/daily_capacity) + (gates × 0.25) + 1
                # For OR: daily_capacity = 136
                expected_work_days = (272 / 136) + (4 * 0.25) + 1  # 2 + 1 + 1 = 4
                actual_work_days = breakdown.get("work_days", 0)
                
                # Verify labor calculation
                # UK min wage = 12.21, hourly_rate = 2 * 12.21 = 24.42
                # daily_labor = 8 workers * 24.42 * 8 hours = 1564.48
                # total_labor = 1564.48 * 4 days = 6257.92
                expected_labor = 8 * (2 * 12.21) * 8 * 4  # 6257.92
                actual_labor = breakdown.get("labor_cost", 0)
                
                # Verify tools cost: 200 base + 100 * work_days
                expected_tools = 200 + (100 * 4)  # 600
                actual_tools = breakdown.get("tools_cost", 0)
                
                # Verify supervision: 250 * work_days
                expected_supervision = 250 * 4  # 1000
                actual_supervision = breakdown.get("supervision_cost", 0)
                
                # Flight ticket should be 500
                flight_ticket = breakdown.get("flight_ticket", 0)
                
                # Verify markup calculations
                raw_total = breakdown.get("raw_total", 0)
                markup_30 = breakdown.get("markup_30", 0)
                markup_40 = breakdown.get("markup_40", 0)
                
                formula_correct = (
                    abs(actual_work_days - expected_work_days) < 0.01 and
                    abs(actual_labor - expected_labor) < 1.0 and
                    abs(actual_tools - expected_tools) < 1.0 and
                    abs(actual_supervision - expected_supervision) < 1.0 and
                    flight_ticket == 500 and
                    abs(markup_30 - (raw_total * 1.30)) < 1.0 and
                    abs(markup_40 - (raw_total * 1.40)) < 1.0
                )
                
                success = success and formula_correct
                details = f"Work days: {actual_work_days} (expected: {expected_work_days}), Labor: £{actual_labor} (expected: £{expected_labor})"
                
            self.log_test("Calculate OR Fence", success, details if success else f"Status: {response.status_code}")
            return success, data if success else {}
        except Exception as e:
            self.log_test("Calculate OR Fence", False, str(e))
            return False, {}

    def test_calculate_endpoint_pr_fence(self):
        """Test calculation endpoint with PR fence type"""
        try:
            payload = {
                "user_name": "Test User PR",
                "project_name": "Test Project PR",
                "country": "Germany",
                "fence_type": "PR",
                "meters": 256.0,
                "gates": 2
            }
            
            response = requests.post(f"{self.api_url}/calculate", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                calc = data.get("calculation", {})
                breakdown = calc.get("breakdown", {})
                
                # For PR: daily_capacity = 128
                expected_work_days = (256 / 128) + (2 * 0.25) + 1  # 2 + 0.5 + 1 = 3.5
                actual_work_days = breakdown.get("work_days", 0)
                
                formula_correct = abs(actual_work_days - expected_work_days) < 0.01
                success = success and formula_correct
                
            self.log_test("Calculate PR Fence", success, f"Work days: {actual_work_days} (expected: {expected_work_days})" if success else f"Status: {response.status_code}")
            return success, data if success else {}
        except Exception as e:
            self.log_test("Calculate PR Fence", False, str(e))
            return False, {}

    def test_invalid_country(self):
        """Test calculation with invalid country"""
        try:
            payload = {
                "user_name": "Test User",
                "project_name": "Test Project",
                "country": "Invalid Country",
                "fence_type": "OR",
                "meters": 100.0,
                "gates": 1
            }
            
            response = requests.post(f"{self.api_url}/calculate", json=payload, timeout=10)
            success = response.status_code == 400
            
            self.log_test("Invalid Country Handling", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Invalid Country Handling", False, str(e))
            return False

    def test_calculations_endpoint(self):
        """Test calculations archive endpoint"""
        try:
            response = requests.get(f"{self.api_url}/calculations", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = isinstance(data, list)
                
            self.log_test("Calculations Archive", success, f"Status: {response.status_code}, Records: {len(data) if success else 0}")
            return success, data if success else []
        except Exception as e:
            self.log_test("Calculations Archive", False, str(e))
            return False, []

    def test_zero_minimum_wage_countries(self):
        """Test calculation with countries that have 0 minimum wage (should default to 15.00)"""
        try:
            payload = {
                "user_name": "Test User Sweden",
                "project_name": "Test Project Sweden",
                "country": "Sweden",
                "fence_type": "OR",
                "meters": 136.0,
                "gates": 0
            }
            
            response = requests.post(f"{self.api_url}/calculate", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                calc = data.get("calculation", {})
                breakdown = calc.get("breakdown", {})
                
                # Should use 15.00 as minimum wage for Sweden (which has 0 in the list)
                # work_days = (136/136) + (0*0.25) + 1 = 2
                # labor = 8 * (2 * 15) * 8 * 2 = 3840
                expected_labor = 8 * (2 * 15.00) * 8 * 2
                actual_labor = breakdown.get("labor_cost", 0)
                
                formula_correct = abs(actual_labor - expected_labor) < 1.0
                success = success and formula_correct
                
            self.log_test("Zero Min Wage Country (Sweden)", success, f"Labor cost: £{actual_labor} (expected: £{expected_labor})" if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Zero Min Wage Country (Sweden)", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Racing Fence Pricing API Tests")
        print("=" * 50)
        
        # Test basic connectivity
        if not self.test_root_endpoint():
            print("❌ Root endpoint failed - stopping tests")
            return False
            
        # Test countries endpoint
        countries_success, countries = self.test_countries_endpoint()
        if not countries_success:
            print("❌ Countries endpoint failed - stopping tests")
            return False
            
        # Test calculation endpoints
        self.test_calculate_endpoint_or_fence()
        self.test_calculate_endpoint_pr_fence()
        self.test_zero_minimum_wage_countries()
        
        # Test error handling
        self.test_invalid_country()
        
        # Test archive endpoint
        self.test_calculations_endpoint()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Tests Summary: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = RacingFencePricingAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': tester.tests_run,
            'passed_tests': tester.tests_passed,
            'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
            'results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())