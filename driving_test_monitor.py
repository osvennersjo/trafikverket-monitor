#!/usr/bin/env python3

import requests
import json
import time
import datetime
from typing import Dict, List, Optional
import logging
import re
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrafikverketAPI:
    def __init__(self):
        self.base_url = "https://fp.trafikverket.se"
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Referer': 'https://fp.trafikverket.se/',
        })
        
    def discover_api_endpoints(self):
        """Discover working API endpoints"""
        logger.info("🔍 Discovering API endpoints...")
        
        # Known endpoints from successful projects
        endpoints = [
            "/api/licence-categories",
            "/api/locations", 
            "/api/occasions",
            "/Boka/api/locations",
            "/Boka/api/occasions",
            "/Boka/api/occasions/search",
            "/Boka/ng/api/occasions",
            "/Boka/ng/api/locations",
        ]
        
        working_endpoints = {}
        
        for endpoint in endpoints:
            url = urljoin(self.base_url, endpoint)
            try:
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ Working endpoint: {endpoint}")
                    working_endpoints[endpoint] = {
                        'url': url,
                        'method': 'GET',
                        'status': 200
                    }
                    try:
                        data = response.json()
                        working_endpoints[endpoint]['data'] = data
                    except:
                        pass
                        
                elif response.status_code == 405:  # Try POST
                    post_response = self.session.post(url, json={}, timeout=10)
                    if post_response.status_code not in [404, 403]:
                        logger.info(f"✅ Working POST endpoint: {endpoint}")
                        working_endpoints[endpoint] = {
                            'url': url,
                            'method': 'POST',
                            'status': post_response.status_code
                        }
                        
                elif response.status_code == 401:
                    logger.info(f"🔐 Protected endpoint: {endpoint}")
                    working_endpoints[endpoint] = {
                        'url': url,
                        'method': 'GET',
                        'status': 401,
                        'auth_required': True
                    }
                    
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                logger.debug(f"❌ Endpoint {endpoint} failed: {e}")
                
        return working_endpoints
        
    def get_locations(self, endpoints):
        """Get test center locations"""
        location_endpoints = [ep for ep in endpoints.keys() if 'location' in ep]
        
        for endpoint in location_endpoints:
            if endpoints[endpoint].get('data'):
                data = endpoints[endpoint]['data']
                logger.info(f"📍 Found locations data from {endpoint}")
                return self.parse_locations(data)
                
        return {}
        
    def parse_locations(self, data):
        """Parse locations and find Södertälje/Farsta"""
        locations = {}
        target_cities = ['södertälje', 'farsta']
        
        # Handle different data structures
        location_list = data
        if isinstance(data, dict):
            location_list = data.get('locations', data.get('data', data.get('results', [])))
            
        if not isinstance(location_list, list):
            return locations
            
        for location in location_list:
            if isinstance(location, dict):
                name = location.get('name', '').lower()
                location_id = location.get('id') or location.get('locationId')
                
                for city in target_cities:
                    if city in name:
                        locations[city] = {
                            'id': location_id,
                            'name': location.get('name'),
                            'data': location
                        }
                        logger.info(f"Found {city}: {location.get('name')} (ID: {location_id})")
                        
        return locations
        
    def search_occasions(self, endpoints, locations, from_date, to_date):
        """Search for available test occasions"""
        occasion_endpoints = [ep for ep in endpoints.keys() if 'occasion' in ep and endpoints[ep].get('status') == 200]
        
        location_ids = [loc['id'] for loc in locations.values() if loc['id']]
        
        search_params = {
            "licenceCategoryId": "5",  # B license
            "examTypeId": "5",         # Manual driving test
            "locationIds": location_ids,
            "fromDate": from_date,
            "toDate": to_date
        }
        
        for endpoint in occasion_endpoints:
            logger.info(f"🔍 Searching occasions via {endpoint}")
            
            try:
                if endpoints[endpoint]['method'] == 'POST':
                    response = self.session.post(endpoints[endpoint]['url'], json=search_params, timeout=15)
                else:
                    response = self.session.get(endpoints[endpoint]['url'], params=search_params, timeout=15)
                    
                if response.status_code == 200:
                    data = response.json()
                    slots = self.parse_occasions(data)
                    if slots:
                        logger.info(f"✅ Found {len(slots)} slots via {endpoint}")
                        return slots
                        
            except Exception as e:
                logger.error(f"Error searching {endpoint}: {e}")
                
        return []
        
    def parse_occasions(self, data):
        """Parse occasions data to extract available slots"""
        slots = []
        
        # Handle different response structures
        occasions = data
        if isinstance(data, dict):
            occasions = data.get('occasions', data.get('results', data.get('data', [])))
            
        if not isinstance(occasions, list):
            occasions = [occasions] if occasions else []
            
        for occasion in occasions:
            if isinstance(occasion, dict):
                date = occasion.get('date') or occasion.get('testDate')
                time = occasion.get('time') or occasion.get('testTime')
                location = occasion.get('location') or occasion.get('locationName')
                available = occasion.get('available', True)
                
                if date and time and available:
                    slots.append({
                        'date': date,
                        'time': time,
                        'location': location or 'Unknown',
                        'available': available
                    })
                    
        return slots


def monitor_driving_tests():
    """Main monitoring function"""
    print("🚗 Trafikverket Driving Test Monitor")
    print("=" * 50)
    
    # Get user input
    try:
        from_date_str = input("From date (YYYY-MM-DD) or Enter for today: ").strip()
        from_date = datetime.datetime.strptime(from_date_str, "%Y-%m-%d").date() if from_date_str else datetime.date.today()
        
        to_date_str = input("To date (YYYY-MM-DD) or Enter for +7 days: ").strip()  
        to_date = datetime.datetime.strptime(to_date_str, "%Y-%m-%d").date() if to_date_str else from_date + datetime.timedelta(days=7)
        
        interval_str = input("Check interval in minutes (default 5): ").strip()
        interval = int(interval_str) if interval_str else 5
        
    except (ValueError, KeyboardInterrupt) as e:
        print(f"Invalid input or cancelled: {e}")
        return
        
    print(f"\n🎯 Monitoring from {from_date} to {to_date}")
    print(f"📍 Looking for: Södertälje, Farsta")
    print(f"🚗 Test type: Manual B license")
    print(f"🔄 Check interval: {interval} minutes\n")
    
    # Initialize API
    api = TrafikverketAPI()
    
    # Discover endpoints
    endpoints = api.discover_api_endpoints()
    
    if not endpoints:
        print("❌ No API endpoints found!")
        return
        
    # Get locations
    locations = api.get_locations(endpoints)
    
    if not locations:
        print("⚠️ Could not find Södertälje or Farsta locations")
        print("Available endpoints found:")
        for ep, info in endpoints.items():
            print(f"  {ep}: HTTP {info['status']}")
        return
        
    print(f"✅ Found locations: {list(locations.keys())}")
    
    # Start monitoring
    last_slots = set()
    
    while True:
        try:
            logger.info("🔍 Checking for available slots...")
            
            slots = api.search_occasions(
                endpoints, 
                locations, 
                from_date.isoformat(),
                to_date.isoformat()
            )
            
            if slots:
                # Check for new slots
                current_slots = set()
                for slot in slots:
                    slot_id = f"{slot['date']}_{slot['time']}_{slot['location']}"
                    current_slots.add(slot_id)
                    
                new_slots = current_slots - last_slots
                
                if new_slots:
                    print("\n🎉 NEW AVAILABLE SLOTS FOUND!")
                    print("=" * 40)
                    
                    for slot in slots:
                        slot_id = f"{slot['date']}_{slot['time']}_{slot['location']}"
                        if slot_id in new_slots:
                            print(f"📅 Date: {slot['date']}")
                            print(f"🕐 Time: {slot['time']}")
                            print(f"📍 Location: {slot['location']}")
                            print(f"🔗 Book at: https://fp.trafikverket.se/Boka/ng/search/EREEoARaaGevAi/5/0/0/0")
                            print("-" * 30)
                            
                    # Send notification (you can add email/webhook here)
                    
                else:
                    print(f"ℹ️ {len(slots)} slots available (no new ones)")
                    
                last_slots = current_slots
                
            else:
                print("ℹ️ No available slots found")
                
            # Wait for next check
            print(f"💤 Waiting {interval} minutes...")
            time.sleep(interval * 60)
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")
            time.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    monitor_driving_tests() 