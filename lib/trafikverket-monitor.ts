import axios, { AxiosInstance } from 'axios';
import { EmailNotifier } from './email-notifier';

interface TestSlot {
  date: string;
  time: string;
  location: string;
  testType: string;
  available: boolean;
}

interface MonitoringConfig {
  email: string;
  fromDate: string;
  toDate: string;
  emailNotifier: EmailNotifier;
  checkInterval: number;
}

interface MonitoringStatus {
  isActive: boolean;
  email: string;
  fromDate: string;
  toDate: string;
  slotsFound: number;
  lastCheck: string;
}

export class TrafikverketMonitor {
  private config: MonitoringConfig;
  private httpClient: AxiosInstance;
  private intervalId: NodeJS.Timeout | null = null;
  private lastKnownSlots: Set<string> = new Set();
  private workingEndpoints: any = {};
  private locationIds: { [key: string]: any } = {};
  private status: MonitoringStatus;

  constructor(config: MonitoringConfig) {
    this.config = config;
    this.status = {
      isActive: false,
      email: config.email,
      fromDate: config.fromDate,
      toDate: config.toDate,
      slotsFound: 0,
      lastCheck: ''
    };

    this.httpClient = axios.create({
      baseURL: 'https://fp.trafikverket.se',
      timeout: 5000, // Reduced from 15s to 5s to prevent function timeouts
      headers: {
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
      }
    });
  }

  async start(): Promise<boolean> {
    console.log('🚀 Starting Trafikverket monitoring...');
    
    // Discover working API endpoints
    const endpointsDiscovered = await this.discoverApiEndpoints();
    if (!endpointsDiscovered) {
      console.error('❌ No working API endpoints found');
      return false;
    }

    // Find location IDs for Södertälje and Farsta
    const locationsFound = await this.findLocationIds();
    if (!locationsFound) {
      console.warn('⚠️ Could not find target locations, will monitor all locations');
    }

    // Start monitoring interval
    this.status.isActive = true;
    this.startMonitoringLoop();

    console.log('✅ Monitoring started successfully');
    return true;
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.status.isActive = false;
    console.log('🛑 Monitoring stopped');
  }

  isActive(): boolean {
    return this.status.isActive;
  }

  getStatus(): MonitoringStatus {
    return { ...this.status };
  }

  private async discoverApiEndpoints(): Promise<boolean> {
    console.log('🔍 Discovering API endpoints...');

    // Prioritized endpoints - test most promising ones first
    const endpointsToTest = [
      // Main occasion search endpoint (highest priority)
      { path: '/Boka/occasion-bundles', method: 'POST', priority: 1 },
      
      // Most promising XHR endpoints
      { path: '/boka/ng/api/search-information', method: 'GET', priority: 2 },
      { path: '/boka/ng/api/is-system-updating', method: 'GET', priority: 2 },
      { path: '/boka/ng/api/get-navigation-model', method: 'GET', priority: 3 },
      
      // Lower priority endpoints
      { path: '/boka/ng/api/information', method: 'GET', priority: 4 },
      { path: '/boka/ng/api/is-authorized', method: 'GET', priority: 4 },
      
      // Fallback to old endpoints (lowest priority)
      { path: '/boka/api/2.0/occasions', method: 'POST', priority: 5 },
    ];

    // Sort by priority and limit to prevent timeouts
    const prioritizedEndpoints = endpointsToTest
      .sort((a, b) => a.priority - b.priority)
      .slice(0, 5); // Test only top 5 to prevent timeout

    let foundEndpoints = 0;
    const maxTimePerRequest = 2000; // 2 seconds max per request

    for (const endpoint of prioritizedEndpoints) {
      try {
        console.log(`🔍 Testing ${endpoint.method} ${endpoint.path}...`);
        
        let response;
        
        // Create a timeout promise
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Request timeout')), maxTimePerRequest);
        });
        
        // Create request promise
        const requestPromise = this.makeRequest(endpoint);
        
        // Race the request against the timeout
        response = await Promise.race([requestPromise, timeoutPromise]);
        
        // Check if response contains actual data (not HTML redirect)
        const responseText = JSON.stringify(response.data);
        const isHtmlResponse = responseText.includes('<!doctype html>') || responseText.includes('<html');
        
        if ((response.status === 200 || response.status === 201) && !isHtmlResponse) {
          console.log(`✅ Found working ${endpoint.method} endpoint: ${endpoint.path}`);
          this.workingEndpoints[endpoint.path] = {
            url: endpoint.path,
            method: endpoint.method,
            data: response.data,
            priority: endpoint.priority
          };
          foundEndpoints++;
        } else if (isHtmlResponse) {
          console.log(`❌ ${endpoint.method} ${endpoint.path}: Returns HTML (redirect)`);
        }
      } catch (error: any) {
        const status = error.response?.status;
        const message = error.response?.data?.message || error.message;
        
        if (message === 'Request timeout') {
          console.log(`⏰ ${endpoint.method} ${endpoint.path}: Timeout (${maxTimePerRequest}ms)`);
        } else {
          console.log(`❌ Failed ${endpoint.method} ${endpoint.path}: ${status} - ${message}`);
        }
        
        // For occasion-bundles, authentication error is expected but means endpoint exists
        if (endpoint.path === '/Boka/occasion-bundles' && (status === 401 || status === 403)) {
          console.log(`ℹ️  Occasion-bundles endpoint exists but requires authentication (expected)`);
          this.workingEndpoints[endpoint.path] = {
            url: endpoint.path,
            method: 'POST',
            requiresAuth: true,
            data: null,
            priority: endpoint.priority
          };
          foundEndpoints++;
        }
      }

      // Small delay to prevent rate limiting, but much shorter
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.log(`📊 Found ${foundEndpoints} working endpoints (tested ${prioritizedEndpoints.length})`);
    
    if (foundEndpoints === 0) {
      console.log('❌ No working endpoints found - monitoring cannot start');
      console.log('💡 This usually means the API structure has changed or authentication is required');
    }
    
    return foundEndpoints > 0;
  }

  private async makeRequest(endpoint: any): Promise<any> {
    if (endpoint.method === 'GET') {
      return await this.httpClient.get(endpoint.path);
    } else {
      // For the main occasion-bundles endpoint, use proper payload structure
      if (endpoint.path === '/Boka/occasion-bundles') {
        const payload = {
          bookingSession: {
            socialSecurityNumber: '', // We'll try without SSN first
            licenceId: 5, // B license
            bookingModeId: 0
          },
          occasionBundleQuery: {
            startDate: this.config.fromDate,
            endDate: this.config.toDate,
            locationId: null, // Search all locations initially
            examinationTypeId: 5, // B license
            tachographTypeId: 1,
            occasionChoiceId: 1,
            searchedMonths: 0
          }
        };
        return await this.httpClient.post(endpoint.path, payload);
      } else {
        // For other POST endpoints, try with empty payload
        return await this.httpClient.post(endpoint.path, {});
      }
    }
  }

  private async findLocationIds(): Promise<boolean> {
    console.log('📍 Finding location IDs for Södertälje and Farsta...');

    const locationEndpoints = Object.keys(this.workingEndpoints)
      .filter(ep => ep.includes('location'));

    for (const endpoint of locationEndpoints) {
      const endpointData = this.workingEndpoints[endpoint];
      if (endpointData.data) {
        const locations = this.extractLocationsFromResponse(endpointData.data);
        
        if (locations.length > 0) {
          console.log(`📍 Analyzing ${locations.length} locations from ${endpoint}`);
          
          const targetCities = ['södertälje', 'farsta'];
          
          for (const location of locations) {
            const name = (location.name || '').toLowerCase();
            const locationId = location.id || location.locationId;
            
            for (const city of targetCities) {
              if (name.includes(city)) {
                this.locationIds[city] = {
                  id: locationId,
                  name: location.name,
                  data: location
                };
                console.log(`✅ Found ${city}: ${location.name} (ID: ${locationId})`);
              }
            }
          }
          
          if (Object.keys(this.locationIds).length > 0) {
            return true;
          }
        }
      }
    }

    return false;
  }

  private extractLocationsFromResponse(data: any): any[] {
    if (Array.isArray(data)) {
      return data;
    }
    
    if (typeof data === 'object' && data !== null) {
      // Try common property names
      const possibleArrays = [
        data.locations,
        data.data,
        data.results,
        data.items
      ];
      
      for (const arr of possibleArrays) {
        if (Array.isArray(arr)) {
          return arr;
        }
      }
    }
    
    return [];
  }

  private startMonitoringLoop(): void {
    // Run initial check
    this.checkForSlots();

    // Set up interval
    this.intervalId = setInterval(() => {
      this.checkForSlots();
    }, this.config.checkInterval);
  }

  private async checkForSlots(): Promise<void> {
    try {
      console.log('🔍 Checking for available slots...');
      this.status.lastCheck = new Date().toISOString();

      const slots = await this.searchForSlots();
      
      if (slots.length > 0) {
        const currentSlotIds = new Set<string>();
        
        // Create unique IDs for current slots
        slots.forEach(slot => {
          const slotId = `${slot.date}_${slot.time}_${slot.location}`;
          currentSlotIds.add(slotId);
        });

        // Find new slots
        const newSlotIds = Array.from(currentSlotIds).filter(id => !this.lastKnownSlots.has(id));
        
        if (newSlotIds.length > 0) {
          const newSlots = slots.filter(slot => {
            const slotId = `${slot.date}_${slot.time}_${slot.location}`;
            return newSlotIds.includes(slotId);
          });

          console.log(`🎉 Found ${newSlots.length} new slots!`);
          await this.sendNotification(newSlots);
          this.status.slotsFound += newSlots.length;
        }

        this.lastKnownSlots = currentSlotIds;
      } else {
        console.log('ℹ️ No available slots found');
      }
    } catch (error) {
      console.error('Error checking for slots:', error);
    }
  }

  private async searchForSlots(): Promise<TestSlot[]> {
    const occasionEndpoints = Object.keys(this.workingEndpoints)
      .filter(ep => ep.includes('occasion'));

    for (const endpoint of occasionEndpoints) {
      try {
        const endpointData = this.workingEndpoints[endpoint];
        
        let response;
        if (endpointData.method === 'POST') {
          if (endpoint === '/Boka/occasion-bundles') {
            // Use the correct payload structure for the main endpoint
            const payload = {
              bookingSession: {
                socialSecurityNumber: '', // Empty for now - might need auth later
                licenceId: 5, // B license
                bookingModeId: 0
              },
              occasionBundleQuery: {
                startDate: this.config.fromDate,
                endDate: this.config.toDate,
                locationId: null, // Search all locations - we'll filter in parsing
                examinationTypeId: 5, // B license
                tachographTypeId: 1,
                occasionChoiceId: 1,
                searchedMonths: 0
              }
            };
            response = await this.httpClient.post(endpoint, payload);
          } else {
            // Fallback for old-style endpoints
            const searchParams = {
              licenceCategoryId: "5", // B license
              examTypeId: "5",        // Manual driving test
              fromDate: this.config.fromDate,
              toDate: this.config.toDate
            };
            response = await this.httpClient.post(endpoint, searchParams);
          }
        } else {
          const params = {
            licenceCategory: "5",
            examType: "5",
            fromDate: this.config.fromDate,
            toDate: this.config.toDate
          };
          response = await this.httpClient.get(endpoint, { params });
        }

        if (response.status === 200) {
          const slots = this.parseOccasionsResponse(response.data);
          if (slots.length > 0) {
            console.log(`✅ Found ${slots.length} slots via ${endpoint}`);
            return slots;
          }
        }
      } catch (error: any) {
        const status = error.response?.status;
        const message = error.response?.data?.message || error.message;
        console.error(`Error searching ${endpoint}: ${status} - ${message}`);
        
        // For the main endpoint, authentication errors are expected without proper session
        if (endpoint === '/Boka/occasion-bundles' && (status === 401 || status === 403)) {
          console.log('ℹ️ Authentication required for occasion-bundles - this is expected');
          console.log('💡 The system may need Bank ID authentication to access actual booking data');
        }
      }
    }

    console.log('⚠️ No slots found from any endpoint');
    return [];
  }

  private parseOccasionsResponse(data: any): TestSlot[] {
    const slots: TestSlot[] = [];

    console.log('📊 Parsing response data...');
    console.log(`Response type: ${typeof data}, keys: ${data && typeof data === 'object' ? Object.keys(data).join(', ') : 'none'}`);

    let occasions = data;
    
    // Handle different response structures from different endpoints
    if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
      // Try different possible structures
      occasions = data.occasions || 
                 data.occasionBundles || 
                 data.results || 
                 data.data || 
                 data.items ||
                 data.appointments ||
                 data.slots || 
                 [];

      // If still not an array, check nested structures
      if (!Array.isArray(occasions) && typeof occasions === 'object') {
        const possibleArrays = Object.values(occasions).filter(val => Array.isArray(val));
        if (possibleArrays.length > 0) {
          occasions = possibleArrays[0]; // Take the first array found
        }
      }
    }

    if (!Array.isArray(occasions)) {
      occasions = occasions ? [occasions] : [];
    }

    console.log(`📊 Found ${occasions.length} occasions to process`);

    occasions.forEach((occasion: any) => {
      if (typeof occasion === 'object' && occasion !== null) {
        // Try different field names for different API versions
        const date = occasion.date || 
                    occasion.testDate || 
                    occasion.startDate ||
                    occasion.occasionDate ||
                    occasion.dateTime?.split('T')[0];
                    
        const time = occasion.time || 
                    occasion.testTime || 
                    occasion.startTime ||
                    occasion.dateTime?.split('T')[1]?.substring(0, 5);
                    
        const location = occasion.location || 
                        occasion.locationName || 
                        occasion.locationDescription ||
                        occasion.testCenter ||
                        occasion.centerName;
                        
        const available = occasion.available !== false && 
                         occasion.isAvailable !== false &&
                         occasion.status !== 'booked' &&
                         occasion.status !== 'unavailable';

        if (date && time && available && location) {
          // CRITICAL: Only allow Södertälje or Farsta locations
          const locationLower = location.toLowerCase();
          const isValidLocation = locationLower.includes('södertälje') || 
                                 locationLower.includes('farsta') ||
                                 locationLower.includes('sodertalje'); // Alternative spelling

          if (isValidLocation) {
            console.log(`✅ Valid location found: ${location} on ${date} at ${time}`);
            slots.push({
              date,
              time,
              location,
              testType: 'Manual B License',
              available
            });
          } else {
            console.log(`❌ Ignoring slot at invalid location: ${location}`);
          }
        } else {
          console.log(`⚠️ Incomplete slot data: date=${date}, time=${time}, location=${location}, available=${available}`);
        }
      }
    });

    console.log(`🎯 Final result: ${slots.length} valid slots found`);
    return slots;
  }

  private async sendNotification(slots: TestSlot[]): Promise<void> {
    try {
      // CRITICAL SAFETY CHECK: Filter locations one more time before sending email
      const validSlots = slots.filter(slot => {
        const locationLower = slot.location.toLowerCase();
        const isValid = locationLower.includes('södertälje') || 
                       locationLower.includes('farsta') ||
                       locationLower.includes('sodertalje'); // Alternative spelling
        
        if (!isValid) {
          console.log(`🚨 SAFETY CHECK: Prevented email for invalid location: ${slot.location}`);
        }
        return isValid;
      });

      if (validSlots.length === 0) {
        console.log('🛡️ No valid slots after safety check - no email sent');
        return;
      }

      const subject = `🚗 New Driving Test Slots Available in Södertälje/Farsta!`;
      
      let emailBody = `Great news! We found ${validSlots.length} new driving test slots available in your target locations:\n\n`;
      
      validSlots.forEach(slot => {
        emailBody += `📅 Date: ${slot.date}\n`;
        emailBody += `🕐 Time: ${slot.time}\n`;
        emailBody += `📍 Location: ${slot.location}\n`;
        emailBody += `🚗 Test Type: ${slot.testType}\n`;
        emailBody += `🔗 Book at: https://fp.trafikverket.se/Boka/ng/search/EREEoARaaGevAi/5/0/0/0\n\n`;
        emailBody += `${'-'.repeat(50)}\n\n`;
      });

      emailBody += `🏃‍♂️ Book quickly before someone else takes these slots!\n\n`;
      emailBody += `Good luck with your driving test! 🍀\n\n`;
      emailBody += `PS: While you're waiting, why not listen to some Sean Paul? 🎵`;

      await this.config.emailNotifier.sendEmail(
        this.config.email,
        subject,
        emailBody
      );

      console.log(`📧 Email notification sent to ${this.config.email} for ${validSlots.length} valid slots`);
    } catch (error) {
      console.error('Failed to send email notification:', error);
    }
  }
} 