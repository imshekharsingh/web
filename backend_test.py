import requests
import sys
import json
from datetime import datetime

class HomeShareAPITester:
    def __init__(self, base_url="https://homeshare-india.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            self.test_results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response_preview": response.text[:100] if not success else "OK"
            })

            return success, response.json() if success and response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": "ERROR",
                "success": False,
                "response_preview": str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_get_properties(self):
        """Test getting all properties"""
        return self.run_test("Get All Properties", "GET", "properties", 200)

    def test_get_properties_with_filters(self):
        """Test getting properties with filters"""
        params = {"city": "Mumbai", "limit": 5}
        return self.run_test("Get Properties with City Filter", "GET", "properties", 200, params=params)

    def test_get_cities(self):
        """Test getting available cities"""
        return self.run_test("Get Available Cities", "GET", "properties/search/cities", 200)

    def test_get_property_by_id(self, property_id):
        """Test getting a specific property by ID"""
        return self.run_test(f"Get Property by ID", "GET", f"properties/{property_id}", 200)

    def test_get_nonexistent_property(self):
        """Test getting a non-existent property"""
        fake_id = "non-existent-id-12345"
        return self.run_test("Get Non-existent Property", "GET", f"properties/{fake_id}", 404)

    def test_create_property(self):
        """Test creating a new property"""
        property_data = {
            "title": "Test Property",
            "description": "A test property for API testing",
            "price_per_night": 2000,
            "property_type": "apartment",
            "location": {
                "city": "Test City",
                "state": "Test State",
                "area": "Test Area",
                "pincode": "123456"
            },
            "images": ["https://example.com/image1.jpg"],
            "amenities": ["WiFi", "AC"],
            "max_guests": 2,
            "bedrooms": 1,
            "bathrooms": 1,
            "host_name": "Test Host"
        }
        return self.run_test("Create Property", "POST", "properties", 200, data=property_data)

def main():
    print("🏠 HomeShare India API Testing")
    print("=" * 50)
    
    # Setup
    tester = HomeShareAPITester()
    
    # Test basic endpoints
    print("\n📋 Testing Basic Endpoints...")
    tester.test_root_endpoint()
    
    # Test property endpoints
    print("\n🏘️ Testing Property Endpoints...")
    success, properties_data = tester.test_get_properties()
    
    # Get a property ID for detailed testing
    property_id = None
    if success and properties_data and len(properties_data) > 0:
        property_id = properties_data[0].get('id')
        print(f"   Using property ID for detailed testing: {property_id}")
    
    # Test property filters
    tester.test_get_properties_with_filters()
    
    # Test cities endpoint
    tester.test_get_cities()
    
    # Test specific property if we have an ID
    if property_id:
        tester.test_get_property_by_id(property_id)
    
    # Test non-existent property
    tester.test_get_nonexistent_property()
    
    # Test property creation
    print("\n➕ Testing Property Creation...")
    tester.test_create_property()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the details above.")
        print("\nFailed tests:")
        for result in tester.test_results:
            if not result['success']:
                print(f"  - {result['name']}: {result['response_preview']}")
        return 1

if __name__ == "__main__":
    sys.exit(main())