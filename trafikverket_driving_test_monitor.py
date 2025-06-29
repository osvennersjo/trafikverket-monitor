#!/usr/bin/env python3

import requests
import json
import time
import datetime
from typing import Dict, List, Optional, Tuple
import logging
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
import schedule

@dataclass
class TestSlot:
    date: str
    time: str
    location: str
    test_type: str
    available: bool
    booking_url: Optional[str] = None

class TrafikverketAPIDiscovery:
    def __init__(self):
        self.base_url = "https://fp.trafikverket.se"
        self.session = requests.Session()
        self.discovered_endpoints = {}
        self.working_endpoints = {}
        self.setup_session()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trafikverket_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_session(self):
        """Setup session with realistic headers to avoid detection"""
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

    def discover_api_endpoints(self) -> Dict[str, Dict]:
        """Discover API endpoints based on successful GitHub projects and common patterns"""
        
        self.logger.info("🔍 Starting API endpoint discovery...")
        
        # Endpoints found in successful projects
        potential_endpoints = {
            # From go-trafikverket project
            "licence_categories": "/api/licence-categories",
            "locations": "/api/locations", 
            "occasions": "/api/occasions",
            "exam_types": "/api/exam-types",
            
            # Booking system patterns
            "boka_occasions": "/Boka/api/occasions",
            "boka_locations": "/Boka/api/locations",
            "boka_search": "/Boka/api/occasions/search",
            "boka_available": "/Boka/api/occasions/available",
            
            # Angular/modern web app patterns
            "ng_occasions": "/Boka/ng/api/occasions",
            "ng_locations": "/Boka/ng/api/locations",
            "ng_search": "/Boka/ng/api/search",
            "ng_availability": "/Boka/ng/api/availability",
            
            # Alternative patterns
            "forarprov_occasions": "/forarprov/api/occasions",
            "forarprov_locations": "/forarprov/api/locations",
            "api_v1_occasions": "/api/v1/occasions",
            "api_v2_occasions": "/api/v2/occasions",
        }
        
        discovered = {}
        
        for name, endpoint in potential_endpoints.items():
            self.logger.info(f"Testing endpoint: {endpoint}")
            
            full_url = urljoin(self.base_url, endpoint)
            
            try:
                # Try GET first
                response = self.session.get(full_url, timeout=15)
                
                result = {
                    "url": full_url,
                    "status_code": response.status_code,
                    "content_type": response.headers.get('content-type', ''),
                    "response_size": len(response.content),
                    "headers": dict(response.headers)
                }
                
                if response.status_code == 200:
                    result["method"] = "GET"
                    result["working"] = True
                    try:
                        result["json_response"] = response.json()
                        self.logger.info(f"✅ Found working GET endpoint: {endpoint}")
                    except:
                        result["text_preview"] = response.text[:200]
                        
                elif response.status_code == 405:  # Method not allowed, try POST
                    post_response = self.session.post(full_url, json={}, timeout=15)
                    if post_response.status_code not in [404, 403]:
                        result["method"] = "POST"
                        result["post_status"] = post_response.status_code
                        result["working"] = True
                        self.logger.info(f"✅ Found working POST endpoint: {endpoint}")
                        
                elif response.status_code == 401:
                    result["method"] = "GET"
                    result["auth_required"] = True
                    result["working"] = True
                    self.logger.info(f"🔐 Found protected endpoint: {endpoint}")
                    
                elif response.status_code == 403:
                    result["method"] = "GET"
                    result["forbidden"] = True
                    self.logger.info(f"🚫 Found forbidden endpoint: {endpoint}")
                    
                discovered[name] = result
                time.sleep(1)  # Be respectful to the server
                
            except Exception as e:
                self.logger.debug(f"❌ Endpoint {endpoint} failed: {e}")
                continue
                
        self.discovered_endpoints = discovered
        return discovered

    def analyze_booking_page_network(self):
        """Analyze the booking page and extract API calls from JavaScript"""
        
        self.logger.info("🕵️ Analyzing booking page for API patterns...")
        
        try:
            # Load the main booking page
            booking_url = "https://fp.trafikverket.se/Boka/ng/search/EREEoARaaGevAi/5/0/0/0"
            response = self.session.get(booking_url, timeout=20)
            
            if response.status_code != 200:
                self.logger.error(f"Failed to load booking page: {response.status_code}")
                return []
            
            content = response.text
            
            # Extract potential API endpoints from JavaScript
            api_patterns = [
                # Standard API patterns
                r'["\']([^"\']*\/api\/[^"\']*)["\']',
                r'baseURL["\']?\s*:\s*["\']([^"\']+)',
                r'apiEndpoint["\']?\s*:\s*["\']([^"\']+)',
                
                # Fetch/Axios patterns  
                r'fetch\s*\(\s*["\']([^"\']*api[^"\']*)',
                r'axios\.\w+\s*\(\s*["\']([^"\']*api[^"\']*)',
                r'\$http\.\w+\s*\(\s*["\']([^"\']*api[^"\']*)',
                
                # Angular service patterns
                r'this\.http\.\w+\s*\(\s*["\']([^"\']*)',
                r'HttpClient\.\w+\s*\(\s*["\']([^"\']*)',
                
                # URL construction patterns
                r'["\']([^"\']*Boka[^"\']*api[^"\']*)["\']',
                r'["\']([^"\']*occasions[^"\']*)["\']',
                r'["\']([^"\']*locations[^"\']*)["\']',
            ]
            
            found_endpoints = set()
            
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Clean and validate the endpoint
                    if any(keyword in match.lower() for keyword in ['api', 'occasions', 'locations', 'search']):
                        if match.startswith('/'):
                            found_endpoints.add(match)
                        elif 'fp.trafikverket.se' in match:
                            parsed = urlparse(match)
                            found_endpoints.add(parsed.path)
            
            return list(found_endpoints)
            
        except Exception as e:
            self.logger.error(f"Error analyzing booking page: {e}")
            return []

    def test_specific_api_calls(self):
        """Test specific API calls based on the booking URL structure"""
        
        self.logger.info("🎯 Testing specific API calls...")
        
        # Based on URL: /Boka/ng/search/EREEoARaaGevAi/5/0/0/0
        # Where 5 = license category B
        test_cases = [
            {
                "name": "License Categories",
                "url": "/api/licence-categories",
                "method": "GET",
                "description": "Get available license categories"
            },
            {
                "name": "Locations",
                "url": "/api/locations", 
                "method": "GET",
                "description": "Get test center locations"
            },
            {
                "name": "Boka Locations",
                "url": "/Boka/api/locations",
                "method": "GET",
                "description": "Get locations from booking system"
            },
            {
                "name": "Occasions Search",
                "url": "/Boka/api/occasions/search",
                "method": "POST",
                "description": "Search for available test occasions",
                "data": {
                    "licenceCategoryId": "5",  # B license
                    "examTypeId": "5",         # Manual driving test
                    "locationIds": [],         # Will be filled with Södertälje/Farsta IDs
                    "fromDate": datetime.date.today().isoformat(),
                    "toDate": (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
                }
            },
            {
                "name": "NG Occasions",
                "url": "/Boka/ng/api/occasions",
                "method": "GET",
                "description": "Angular API for occasions",
                "params": {
                    "licenceCategory": "5",
                    "examType": "5"
                }
            },
            {
                "name": "Available Occasions",
                "url": "/Boka/api/occasions/available",
                "method": "GET",
                "description": "Get available occasions",
                "params": {
                    "categoryId": "5",
                    "examTypeId": "5"
                }
            }
        ]
        
        results = {}
        
        for test in test_cases:
            self.logger.info(f"Testing: {test['name']} - {test['description']}")
            
            full_url = urljoin(self.base_url, test['url'])
            
            try:
                if test['method'] == 'GET':
                    params = test.get('params', {})
                    response = self.session.get(full_url, params=params, timeout=15)
                else:
                    data = test.get('data', {})
                    response = self.session.post(full_url, json=data, timeout=15)
                
                result = {
                    "url": full_url,
                    "method": test['method'],
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "response_size": len(response.content)
                }
                
                if response.status_code == 200:
                    self.logger.info(f"✅ {test['name']}: SUCCESS!")
                    try:
                        json_data = response.json()
                        result["json_response"] = json_data
                        result["working"] = True
                        
                        # Log some details about the response
                        if isinstance(json_data, list):
                            self.logger.info(f"   📄 Response: List with {len(json_data)} items")
                        elif isinstance(json_data, dict):
                            self.logger.info(f"   📄 Response: Dict with keys: {list(json_data.keys())}")
                            
                    except:
                        result["text_response"] = response.text[:500]
                        
                elif response.status_code == 401:
                    self.logger.info(f"🔐 {test['name']}: Requires authentication")
                    result["auth_required"] = True
                    
                elif response.status_code == 403:
                    self.logger.info(f"🚫 {test['name']}: Forbidden")
                    result["forbidden"] = True
                    
                else:
                    self.logger.info(f"❌ {test['name']}: HTTP {response.status_code}")
                    result["error_response"] = response.text[:200]
                    
                results[test['name']] = result
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error testing {test['name']}: {e}")
                results[test['name']] = {"error": str(e)}
                
        return results

    def find_location_ids(self, locations_data: List[Dict]) -> Dict[str, str]:
        """Find location IDs for Södertälje and Farsta"""
        
        location_mapping = {}
        target_locations = ['södertälje', 'farsta']
        
        for location in locations_data:
            location_name = location.get('name', '').lower()
            location_id = location.get('id') or location.get('locationId')
            
            for target in target_locations:
                if target in location_name:
                    location_mapping[target] = {
                        'id': location_id,
                        'name': location.get('name'),
                        'full_data': location
                    }
                    self.logger.info(f"Found location: {location.get('name')} (ID: {location_id})")
        
        return location_mapping


class TrafikverketDrivingTestMonitor:
    def __init__(self):
        self.api_discovery = TrafikverketAPIDiscovery()
        self.working_api_endpoint = None
        self.location_ids = {}
        self.logger = self.api_discovery.logger
        
    def initialize_api(self) -> bool:
        """Discover and initialize the working API"""
        
        self.logger.info("🚀 Initializing Trafikverket API...")
        
        # Step 1: Discover endpoints
        discovered = self.api_discovery.discover_api_endpoints()
        
        # Step 2: Analyze booking page
        page_endpoints = self.api_discovery.analyze_booking_page_network()
        
        # Step 3: Test specific API calls
        api_tests = self.api_discovery.test_specific_api_calls()
        
        # Find working endpoints
        working_endpoints = []
        
        # Check discovery results
        for name, info in discovered.items():
            if info.get('working'):
                working_endpoints.append((name, info))
                
        # Check API test results
        for name, info in api_tests.items():
            if info.get('working'):
                working_endpoints.append((name, info))
        
        if working_endpoints:
            self.logger.info(f"🎉 Found {len(working_endpoints)} working endpoints!")
            
            # Try to find locations endpoint
            for name, info in working_endpoints:
                if 'location' in name.lower():
                    locations_response = info.get('json_response')
                    if locations_response:
                        self.location_ids = self.api_discovery.find_location_ids(locations_response)
                        
            # Find occasions endpoint
            for name, info in working_endpoints:
                if 'occasion' in name.lower() and info.get('working'):
                    self.working_api_endpoint = info
                    self.logger.info(f"Using API endpoint: {name}")
                    break
                    
            return True
        else:
            self.logger.error("❌ No working API endpoints found")
            return False

    def search_available_slots(self, from_date: str, to_date: str) -> List[TestSlot]:
        """Search for available driving test slots"""
        
        if not self.working_api_endpoint:
            self.logger.error("No working API endpoint available")
            return []
            
        self.logger.info(f"🔍 Searching for slots from {from_date} to {to_date}")
        
        # Prepare search parameters
        location_ids = []
        if 'södertälje' in self.location_ids:
            location_ids.append(self.location_ids['södertälje']['id'])
        if 'farsta' in self.location_ids:
            location_ids.append(self.location_ids['farsta']['id'])
            
        if not location_ids:
            self.logger.warning("No location IDs found for Södertälje or Farsta")
            
        search_params = {
            "licenceCategoryId": "5",  # B license
            "examTypeId": "5",         # Manual driving test
            "locationIds": location_ids,
            "fromDate": from_date,
            "toDate": to_date
        }
        
        try:
            # Make API call
            if self.working_api_endpoint['method'] == 'POST':
                response = self.api_discovery.session.post(
                    self.working_api_endpoint['url'],
                    json=search_params,
                    timeout=20
                )
            else:
                response = self.api_discovery.session.get(
                    self.working_api_endpoint['url'],
                    params=search_params,
                    timeout=20
                )
            
            if response.status_code == 200:
                data = response.json()
                return self.parse_slots_response(data)
            else:
                self.logger.error(f"API call failed: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching slots: {e}")
            return []

    def parse_slots_response(self, data: Dict) -> List[TestSlot]:
        """Parse the API response and extract available slots"""
        
        slots = []
        
        try:
            # Handle different response formats
            occasions = data
            if isinstance(data, dict):
                occasions = data.get('occasions', data.get('results', data.get('data', [])))
            
            if not isinstance(occasions, list):
                occasions = [occasions] if occasions else []
            
            for occasion in occasions:
                if not isinstance(occasion, dict):
                    continue
                    
                # Extract slot information
                date = occasion.get('date') or occasion.get('testDate')
                time = occasion.get('time') or occasion.get('testTime')
                location = occasion.get('location') or occasion.get('locationName')
                available = occasion.get('available', True)
                
                if date and time:
                    slot = TestSlot(
                        date=date,
                        time=time,
                        location=location or "Unknown",
                        test_type="Manual B License",
                        available=available,
                        booking_url=occasion.get('bookingUrl')
                    )
                    slots.append(slot)
                    
        except Exception as e:
            self.logger.error(f"Error parsing slots response: {e}")
            
        return slots

    def monitor_continuously(self, from_date: str, to_date: str, check_interval_minutes: int = 5):
        """Continuously monitor for new available slots"""
        
        self.logger.info(f"🔄 Starting continuous monitoring (every {check_interval_minutes} minutes)")
        
        last_known_slots = set()
        
        def check_for_slots():
            try:
                current_slots = self.search_available_slots(from_date, to_date)
                
                if current_slots:
                    # Create unique identifiers for slots
                    current_slot_ids = set()
                    for slot in current_slots:
                        slot_id = f"{slot.date}_{slot.time}_{slot.location}"
                        current_slot_ids.add(slot_id)
                    
                    # Find new slots
                    new_slot_ids = current_slot_ids - last_known_slots
                    
                    if new_slot_ids:
                        new_slots = [slot for slot in current_slots 
                                   if f"{slot.date}_{slot.time}_{slot.location}" in new_slot_ids]
                        
                        self.logger.info(f"🎉 Found {len(new_slots)} new available slots!")
                        
                        for slot in new_slots:
                            print(f"\n🚗 NEW SLOT AVAILABLE!")
                            print(f"📅 Date: {slot.date}")
                            print(f"🕐 Time: {slot.time}")
                            print(f"📍 Location: {slot.location}")
                            print(f"🎯 Test Type: {slot.test_type}")
                            if slot.booking_url:
                                print(f"🔗 Book here: {slot.booking_url}")
                            print(f"🌐 Book at: https://fp.trafikverket.se/Boka/ng/search/EREEoARaaGevAi/5/0/0/0")
                            print("-" * 50)
                    else:
                        self.logger.info(f"No new slots found. Total available: {len(current_slots)}")
                    
                    last_known_slots.update(current_slot_ids)
                else:
                    self.logger.info("No available slots found")
                    
            except Exception as e:
                self.logger.error(f"Error during monitoring: {e}")
        
        # Schedule regular checks
        schedule.every(check_interval_minutes).minutes.do(check_for_slots)
        
        # Run initial check
        check_for_slots()
        
        # Start monitoring loop
        self.logger.info("Monitoring started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")


def main():
    print("🚗 Trafikverket Driving Test Monitor")
    print("=" * 50)
    print("Monitoring for manual B license driving tests in Södertälje or Farsta")
    print()
    
    # Get date range from user
    print("Enter the date range to monitor:")
    
    try:
        from_date_str = input("From date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not from_date_str:
            from_date = datetime.date.today()
        else:
            from_date = datetime.datetime.strptime(from_date_str, "%Y-%m-%d").date()
            
        to_date_str = input("To date (YYYY-MM-DD) or press Enter for +30 days: ").strip()
        if not to_date_str:
            to_date = from_date + datetime.timedelta(days=30)
        else:
            to_date = datetime.datetime.strptime(to_date_str, "%Y-%m-%d").date()
            
        interval_str = input("Check interval in minutes (default 5): ").strip()
        interval = int(interval_str) if interval_str else 5
        
    except ValueError as e:
        print(f"Invalid input: {e}")
        return
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return
    
    print(f"\n🎯 Monitoring from {from_date} to {to_date}")
    print(f"🔄 Checking every {interval} minutes")
    print(f"📍 Locations: Södertälje, Farsta")
    print(f"🚗 Test type: Manual B license")
    print()
    
    # Initialize monitor
    monitor = TrafikverketDrivingTestMonitor()
    
    # Discover and initialize API
    if monitor.initialize_api():
        # Start monitoring
        monitor.monitor_continuously(
            from_date.isoformat(),
            to_date.isoformat(),
            interval
        )
    else:
        print("❌ Failed to initialize API. Please check the logs for details.")
        print("💡 You may need to manually inspect the website and update the API endpoints.")

if __name__ == "__main__":
    main() 