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
      timeout: 15000,
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

    const endpointsToTest = [
      '/api/licence-categories',
      '/api/locations',
      '/api/occasions',
      '/Boka/api/locations',
      '/Boka/api/occasions',
      '/Boka/api/occasions/search',
      '/Boka/ng/api/occasions',
      '/Boka/ng/api/locations',
    ];

    let foundEndpoints = 0;

    for (const endpoint of endpointsToTest) {
      try {
        const response = await this.httpClient.get(endpoint);
        
        if (response.status === 200) {
          console.log(`✅ Found working endpoint: ${endpoint}`);
          this.workingEndpoints[endpoint] = {
            url: endpoint,
            method: 'GET',
            data: response.data
          };
          foundEndpoints++;
        }
      } catch (error: any) {
        if (error.response?.status === 405) {
          // Try POST
          try {
            const postResponse = await this.httpClient.post(endpoint, {});
            if (postResponse.status !== 404 && postResponse.status !== 403) {
              console.log(`✅ Found working POST endpoint: ${endpoint}`);
              this.workingEndpoints[endpoint] = {
                url: endpoint,
                method: 'POST',
                data: postResponse.data
              };
              foundEndpoints++;
            }
          } catch (postError) {
            // Ignore POST errors
          }
        }
      }

      // Add delay between requests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    console.log(`📊 Found ${foundEndpoints} working endpoints`);
    return foundEndpoints > 0;
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

    const locationIds = Object.values(this.locationIds).map((loc: any) => loc.id).filter(Boolean);

    for (const endpoint of occasionEndpoints) {
      try {
        const endpointData = this.workingEndpoints[endpoint];
        
        let response;
        if (endpointData.method === 'POST') {
          const searchParams = {
            licenceCategoryId: "5", // B license
            examTypeId: "5",        // Manual driving test
            locationIds: locationIds.length > 0 ? locationIds : [],
            fromDate: this.config.fromDate,
            toDate: this.config.toDate
          };
          
          response = await this.httpClient.post(endpoint, searchParams);
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
      } catch (error) {
        console.error(`Error searching ${endpoint}:`, error);
      }
    }

    return [];
  }

  private parseOccasionsResponse(data: any): TestSlot[] {
    const slots: TestSlot[] = [];

    let occasions = data;
    if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
      occasions = data.occasions || data.results || data.data || [];
    }

    if (!Array.isArray(occasions)) {
      occasions = occasions ? [occasions] : [];
    }

    occasions.forEach((occasion: any) => {
      if (typeof occasion === 'object' && occasion !== null) {
        const date = occasion.date || occasion.testDate;
        const time = occasion.time || occasion.testTime;
        const location = occasion.location || occasion.locationName;
        const available = occasion.available !== false; // Default to true

        if (date && time && available && location) {
          // CRITICAL: Only allow Södertälje or Farsta locations
          const locationLower = location.toLowerCase();
          const isValidLocation = locationLower.includes('södertälje') || 
                                 locationLower.includes('farsta') ||
                                 locationLower.includes('sodertalje'); // Alternative spelling

          if (isValidLocation) {
            console.log(`✅ Valid location found: ${location}`);
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
        }
      }
    });

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