#!/usr/bin/env python3

import sys
import importlib
import requests
from urllib.parse import urljoin

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("🔍 Testing Dependencies...")
    
    required_modules = ['requests', 'json', 'time', 'datetime', 'logging', 're', 'urllib']
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing modules: {missing_modules}")
        print("Install with: pip install -r driving_test_requirements.txt")
        return False
    else:
        print("✅ All dependencies installed!")
        return True

def test_network_connectivity():
    """Test network connectivity to Trafikverket"""
    print("\n🌐 Testing Network Connectivity...")
    
    test_urls = [
        "https://fp.trafikverket.se",
        "https://www.trafikverket.se"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    for url in test_urls:
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {url} - Accessible")
            else:
                print(f"  ⚠️ {url} - Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url} - Error: {e}")
            return False
    
    print("✅ Network connectivity OK!")
    return True

def test_basic_api_access():
    """Test basic API access"""
    print("\n🔍 Testing Basic API Access...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
        'Referer': 'https://fp.trafikverket.se/',
    })
    
    # Test some basic endpoints
    test_endpoints = [
        "/api/locations",
        "/api/licence-categories", 
        "/Boka/api/locations",
        "/api/occasions"
    ]
    
    base_url = "https://fp.trafikverket.se"
    working_endpoints = []
    
    for endpoint in test_endpoints:
        url = urljoin(base_url, endpoint)
        try:
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ {endpoint} - Working!")
                working_endpoints.append(endpoint)
                
                # Try to parse JSON
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"     📄 JSON list with {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"     📄 JSON object with keys: {list(data.keys())[:3]}...")
                except:
                    print(f"     📄 Non-JSON response ({len(response.content)} bytes)")
                    
            elif response.status_code == 401:
                print(f"  🔐 {endpoint} - Requires authentication")
            elif response.status_code == 403:
                print(f"  🚫 {endpoint} - Forbidden")
            elif response.status_code == 404:
                print(f"  ❌ {endpoint} - Not found")
            elif response.status_code == 405:
                print(f"  ➡️  {endpoint} - Method not allowed (try POST)")
            else:
                print(f"  ❓ {endpoint} - Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    if working_endpoints:
        print(f"\n✅ Found {len(working_endpoints)} working endpoints!")
        return True
    else:
        print(f"\n⚠️ No working endpoints found - you may need to run api_discovery.py")
        return False

def test_scripts_exist():
    """Test if main scripts exist and are readable"""
    print("\n📁 Testing Script Files...")
    
    required_files = [
        'driving_test_monitor.py',
        'api_discovery.py',
        'driving_test_requirements.txt'
    ]
    
    all_exist = True
    
    for file in required_files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                if len(content) > 100:  # Basic sanity check
                    print(f"  ✅ {file} - OK ({len(content)} chars)")
                else:
                    print(f"  ⚠️ {file} - Too short ({len(content)} chars)")
                    all_exist = False
        except FileNotFoundError:
            print(f"  ❌ {file} - NOT FOUND")
            all_exist = False
        except Exception as e:
            print(f"  ❌ {file} - Error: {e}")
            all_exist = False
    
    return all_exist

def run_comprehensive_test():
    """Run all tests"""
    print("🚗 Trafikverket Monitor - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Script Files", test_scripts_exist),
        ("Network Connectivity", test_network_connectivity),
        ("API Access", test_basic_api_access),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! You're ready to go!")
        print("\n🚀 Next steps:")
        print("1. Run: python api_discovery.py")
        print("2. Run: python driving_test_monitor.py")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print("- Install dependencies: pip install -r driving_test_requirements.txt")
        print("- Check internet connection")
        print("- Verify you're in the correct directory")
    
    return all_passed

if __name__ == "__main__":
    run_comprehensive_test() 