#!/usr/bin/env python3

import requests
import json
import time
from urllib.parse import urljoin
import re

class TrafikverketAPIDiscovery:
    def __init__(self):
        self.base_url = "https://fp.trafikverket.se"
        self.session = requests.Session()
        self.results = {}
        self.setup_session()
        
    def setup_session(self):
        """Setup session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Referer': 'https://fp.trafikverket.se/',
            'Cache-Control': 'no-cache'
        })

    def test_endpoint(self, endpoint, method='GET', data=None, params=None):
        """Test a single endpoint"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params or {}, timeout=15)
            elif method == 'POST':
                response = self.session.post(url, json=data or {}, timeout=15)
            else:
                return None
                
            result = {
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'response_size': len(response.content),
                'content_type': response.headers.get('content-type', '')
            }
            
            # Try to parse JSON
            try:
                json_data = response.json()
                result['json_response'] = json_data
                result['has_json'] = True
                
                # Analyze JSON structure
                if isinstance(json_data, list):
                    result['response_type'] = 'list'
                    result['item_count'] = len(json_data)
                    if json_data and isinstance(json_data[0], dict):
                        result['sample_keys'] = list(json_data[0].keys())
                elif isinstance(json_data, dict):
                    result['response_type'] = 'dict'
                    result['keys'] = list(json_data.keys())
                    
            except:
                result['has_json'] = False
                result['text_preview'] = response.text[:200]
                
            return result
            
        except Exception as e:
            return {'error': str(e), 'url': url}

    def discover_all_endpoints(self):
        """Comprehensive endpoint discovery"""
        print("🔍 Starting comprehensive API discovery...")
        print("=" * 60)
        
        # Known endpoints from successful GitHub projects
        endpoints_to_test = [
            # Basic API endpoints
            "/api/licence-categories",
            "/api/locations", 
            "/api/occasions",
            "/api/exam-types",
            
            # Booking system endpoints
            "/Boka/api/licence-categories",
            "/Boka/api/locations",
            "/Boka/api/occasions",
            "/Boka/api/occasions/search",
            "/Boka/api/occasions/available",
            "/Boka/api/exam-types",
            
            # Angular/NG endpoints
            "/Boka/ng/api/licence-categories",
            "/Boka/ng/api/locations",
            "/Boka/ng/api/occasions",
            "/Boka/ng/api/search",
            "/Boka/ng/api/availability",
            
            # Alternative patterns
            "/forarprov/api/occasions",
            "/forarprov/api/locations",
            "/api/v1/occasions",
            "/api/v2/occasions",
            "/api/v1/locations",
            "/api/v2/locations",
            
            # REST patterns
            "/rest/occasions",
            "/rest/locations",
            "/services/occasions",
            "/services/locations",
        ]
        
        working_endpoints = {}
        protected_endpoints = {}
        
        for endpoint in endpoints_to_test:
            print(f"\n📍 Testing: {endpoint}")
            
            # Test GET
            result = self.test_endpoint(endpoint, 'GET')
            if result:
                if result.get('status_code') == 200:
                    print(f"  ✅ GET: Success!")
                    if result.get('has_json'):
                        print(f"     📄 JSON Response: {result.get('response_type')} with {result.get('item_count', len(result.get('keys', [])))} items/keys")
                        if result.get('sample_keys'):
                            print(f"     🔑 Sample keys: {result['sample_keys'][:5]}")
                    working_endpoints[endpoint] = result
                    
                elif result.get('status_code') == 401:
                    print(f"  🔐 GET: Requires authentication")
                    protected_endpoints[endpoint] = result
                    
                elif result.get('status_code') == 405:
                    # Method not allowed, try POST
                    print(f"  ➡️  GET not allowed, trying POST...")
                    post_result = self.test_endpoint(endpoint, 'POST')
                    if post_result and post_result.get('status_code') not in [404, 403]:
                        print(f"  ✅ POST: Status {post_result.get('status_code')}")
                        working_endpoints[endpoint] = post_result
                    else:
                        print(f"  ❌ POST: Status {post_result.get('status_code') if post_result else 'Error'}")
                        
                else:
                    print(f"  ❌ GET: Status {result.get('status_code')}")
                    
            time.sleep(1)  # Be respectful
            
        return working_endpoints, protected_endpoints

    def test_specific_scenarios(self, working_endpoints):
        """Test specific scenarios for driving test booking"""
        print("\n🎯 Testing specific driving test scenarios...")
        print("=" * 60)
        
        # Test search scenarios
        search_endpoints = [ep for ep in working_endpoints.keys() if 'search' in ep or 'occasion' in ep]
        
        test_scenarios = [
            {
                'name': 'B License Manual Test Search',
                'data': {
                    "licenceCategoryId": "5",
                    "examTypeId": "5",
                    "locationIds": [],
                    "fromDate": "2025-01-15",
                    "toDate": "2025-02-15"
                }
            },
            {
                'name': 'General Occasions Query',
                'params': {
                    "category": "5",
                    "type": "manual",
                    "from": "2025-01-15"
                }
            }
        ]
        
        for endpoint in search_endpoints:
            print(f"\n📍 Testing scenarios on: {endpoint}")
            
            for scenario in test_scenarios:
                print(f"  🔍 {scenario['name']}")
                
                if 'data' in scenario:
                    result = self.test_endpoint(endpoint, 'POST', data=scenario['data'])
                else:
                    result = self.test_endpoint(endpoint, 'GET', params=scenario.get('params'))
                    
                if result:
                    if result.get('status_code') == 200:
                        print(f"    ✅ Success! Response size: {result.get('response_size')} bytes")
                        if result.get('has_json'):
                            json_data = result.get('json_response')
                            if isinstance(json_data, list):
                                print(f"    📊 Found {len(json_data)} results")
                            elif isinstance(json_data, dict):
                                print(f"    📊 Response keys: {list(json_data.keys())}")
                    else:
                        print(f"    ❌ Status: {result.get('status_code')}")
                        
                time.sleep(1)

    def analyze_location_data(self, working_endpoints):
        """Analyze location data to find Södertälje and Farsta"""
        print("\n📍 Analyzing location data...")
        print("=" * 60)
        
        location_endpoints = [ep for ep in working_endpoints.keys() if 'location' in ep]
        
        target_locations = ['södertälje', 'farsta']
        found_locations = {}
        
        for endpoint in location_endpoints:
            result = working_endpoints[endpoint]
            if result.get('has_json'):
                json_data = result.get('json_response')
                
                # Extract location list
                locations = json_data
                if isinstance(json_data, dict):
                    locations = json_data.get('locations', json_data.get('data', json_data.get('results', [])))
                    
                if isinstance(locations, list):
                    print(f"\n📍 Analyzing {len(locations)} locations from {endpoint}")
                    
                    for location in locations:
                        if isinstance(location, dict):
                            name = location.get('name', '').lower()
                            location_id = location.get('id') or location.get('locationId')
                            
                            for target in target_locations:
                                if target in name:
                                    found_locations[target] = {
                                        'id': location_id,
                                        'name': location.get('name'),
                                        'endpoint': endpoint,
                                        'full_data': location
                                    }
                                    print(f"  ✅ Found {target}: {location.get('name')} (ID: {location_id})")
                                    
        return found_locations

    def save_results(self, working_endpoints, protected_endpoints, locations):
        """Save discovery results to JSON file"""
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'working_endpoints': working_endpoints,
            'protected_endpoints': protected_endpoints,
            'found_locations': locations,
            'summary': {
                'total_working': len(working_endpoints),
                'total_protected': len(protected_endpoints),
                'locations_found': list(locations.keys())
            }
        }
        
        filename = 'trafikverket_api_discovery.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Results saved to: {filename}")
        return results

    def run_full_discovery(self):
        """Run complete API discovery process"""
        print("🚗 Trafikverket API Discovery Tool")
        print("=" * 60)
        
        # Step 1: Discover endpoints
        working_endpoints, protected_endpoints = self.discover_all_endpoints()
        
        print(f"\n📊 Discovery Summary:")
        print(f"  ✅ Working endpoints: {len(working_endpoints)}")
        print(f"  🔐 Protected endpoints: {len(protected_endpoints)}")
        
        if working_endpoints:
            print(f"\n✅ Working endpoints found:")
            for endpoint, info in working_endpoints.items():
                method = info.get('method', 'GET')
                status = info.get('status_code')
                response_type = info.get('response_type', 'unknown')
                print(f"  {endpoint} ({method}) -> {status} [{response_type}]")
                
            # Step 2: Test specific scenarios
            self.test_specific_scenarios(working_endpoints)
            
            # Step 3: Analyze locations
            locations = self.analyze_location_data(working_endpoints)
            
            # Step 4: Save results
            results = self.save_results(working_endpoints, protected_endpoints, locations)
            
            print(f"\n🎯 Next Steps:")
            if locations:
                print(f"  ✅ Found target locations: {list(locations.keys())}")
                print(f"  🔄 You can now run the main monitor script")
            else:
                print(f"  ⚠️  Target locations not found automatically")
                print(f"  💡 Check the JSON file for all available locations")
                
            print(f"\n🚀 To start monitoring:")
            print(f"  python driving_test_monitor.py")
            
        else:
            print(f"\n❌ No working endpoints found")
            print(f"💡 Possible reasons:")
            print(f"  - API endpoints have changed")
            print(f"  - Authentication is required for all endpoints")
            print(f"  - Rate limiting or IP blocking")
            print(f"  - Network issues")

if __name__ == "__main__":
    discovery = TrafikverketAPIDiscovery()
    discovery.run_full_discovery() 