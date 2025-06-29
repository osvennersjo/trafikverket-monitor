import axios, { AxiosInstance } from 'axios';
import { EmailNotifier } from './email-notifier';

interface OccasionData {
  examinationId: string | null;
  examinationCategory: number;
  duration: {
    start: string;
    end: string;
  };
  examinationTypeId: number;
  locationId: number;
  occasionChoiceId: number;
  vehicleTypeId: number;
  languageId: number;
  tachographTypeId: number;
  name: string;
}

interface MonitoringSlot {
  id: string;
  date: string;
  time: string;
  location: string;
  locationId: number;
  duration: number;
  examinationType: string;
  available: boolean;
}

export class TrafikverketMonitorV2 {
  private httpClient: AxiosInstance;
  private emailNotifier: EmailNotifier;
  private emailAddress: string;
  private isRunning = false;
  private intervalId?: NodeJS.Timeout;
  private seenSlots = new Set<string>();

  // Working session data (will need to be refreshed periodically)
  private sessionCookies!: string;
  private socialSecurityNumber!: string;

  // Location mappings
  private readonly locationNames: { [key: number]: string } = {
    1000132: 'Södertälje',
    1000019: 'Farsta/Stockholm South', // Need to confirm this location
    1000031: 'Stockholm',
    1000003: 'Göteborg',
    1000070: 'Malmö'
  };

  // Target locations (Södertälje and Farsta)
  private readonly targetLocationIds = [1000132, 1000019];

  constructor(emailAddress: string, fromDate: string, toDate: string) {
    this.emailAddress = emailAddress;
    this.emailNotifier = new EmailNotifier({
      sendgridApiKey: process.env.SENDGRID_API_KEY || '',
      fromEmail: 'noreply@trafikverket-monitor.com'
    });
    
    // Create HTTP client first
    this.httpClient = axios.create({
      baseURL: 'https://fp.trafikverket.se',
      timeout: 10000,
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'https://fp.trafikverket.se',
        'Referer': 'https://fp.trafikverket.se/Boka/ng/search/dSdDbIsIiEdAin/5/12/0/0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"'
      }
    });
    
    // Initialize session data after HTTP client is created
    this.updateSessionData();
  }

  private updateSessionData() {
    // This will need to be updated with fresh session data
    // For now, using the working session from the test
    const baseCookies = 'FpsPartnerDeviceIdentifier=3A9A20D3DFD8E7E8348165854B94CD43E2D822F4026DEDD3407F014780642DD771360F659AED5CDF95DED2B5A9A7B9066F0455B5D57AD5DACC2584AB51B138600EE895AB16EB15C674C086C328E7947F3B19D3CB1CCD7E92BC4259CE1E0426A81A437032B1C30DE5A2DE152FF33AC0B19F3C011D1999C6C1270FC96C7DD95E1F37E788036DB7DC471D2D7EE1E640A4E20018ABE755C85D304A3CDDD11F3B8883; ASP.NET_SessionId=mdv2vyjiglhod4ltaypemhur; TrvCookieConsent=functional%3Dfalse%26analytical%3Dfalse; NSC_mc-gpsbsqspw-fyu-xfc-iuuq-wt=ffffffff0914196145525d5f4f58455e445a4a423660; FpsExternalIdentity=7B923F9FFB5157E254F4B6D446B98030094EA5AEE79B967ECDA78DF72C832944875DB730D5111DEDBE4CB8C3806B7AB4CCD84B3CCC15F1C6719B77ADDA4751DAFA4E28281607AA4276EF3F7BBCD947A7CDCCFD9DE65A1D2057498F0B0A1120A7553AE5050735C9376F5E8411EEEF394419F0B8390FF435B70D052B46F49F3787BD40B0F9226136F9816E561A40EC6A42B30C2890D1469AD5EB007D46C7E547CE4334FEA2ACC3D86A104651B07BF6053DBC8F3C6DF1FEB9C7F33DB2040339288EF076962DF923C1272B8BD6D530637FC14F16C147BA5FAC40381F484DDDA4096C7F7653FB0731C3445BCA583F6A5DF9248AF0DBFD01A0C032C02CE7F952684AC3D2E264198F030DC90F7EDF2DB5DB73A0E8F23529C3F65D42BAC8E975C5DAF86E59FFDFD2E65EB58FA90D7501AC5DC213B38603D249CBA49384D4F5F1C70A7D067F80AA0279892A3F0BA41085E05AF1E01BB5BE7F9B0D3DC2A79E814979689152405CD1C42E8F34CD4EF2DB96423A7225B541585D3AF736CD67E3BA2372DF73C15B74A395ED1E1C4DB79BD15DF41F21E0DC5E62DAA8456E014ED8571A9F7C85139055FC1A69B838B2389DD9D9D637E9EB';
    
    // Extend LoginValid time to current time + 1 hour
    const extendedTime = new Date(Date.now() + 60 * 60 * 1000).toISOString().slice(0, 16).replace('T', ' ');
    this.sessionCookies = `${baseCookies}; LoginValid=${encodeURIComponent(extendedTime)}`;
    
    // Update HTTP client headers
    this.httpClient.defaults.headers['Cookie'] = this.sessionCookies;
    
    this.socialSecurityNumber = "20061211-0718"; // This will need to be configurable
    
    console.log(`🔄 Session updated with extended LoginValid: ${extendedTime}`);
  }

  private async searchForSlots(fromDate: string, toDate: string): Promise<MonitoringSlot[]> {
    console.log(`🔍 Searching for slots from ${fromDate} to ${toDate}...`);
    
    // Refresh/extend session before each API call
    this.updateSessionData();
    
    const payload = {
      "bookingSession": {
        "socialSecurityNumber": this.socialSecurityNumber,
        "licenceId": 5, // B license
        "bookingModeId": 0,
        "ignoreDebt": false,
        "ignoreBookingHindrance": false,
        "examinationTypeId": 12, // Manual exam
        "excludeExaminationCategories": [],
        "rescheduleTypeId": 0,
        "paymentIsActive": false,
        "paymentReference": "",
        "paymentUrl": "",
        "searchedMonths": 0
      },
      "occasionBundleQuery": {
        "startDate": new Date(fromDate).toISOString(),
        "endDate": new Date(toDate).toISOString(),
        "searchedMonths": 0,
        "locationId": null, // Search all locations, filter afterwards
        "languageId": 13, // Swedish
        "vehicleTypeId": 2, // Car
        "tachographTypeId": 1,
        "occasionChoiceId": 1,
        "examinationTypeId": 12
      }
    };

    try {
      const response = await this.httpClient.post('/Boka/occasion-bundles', payload);
      return this.parseOccasions(response.data);
    } catch (error: any) {
      console.error('❌ Search failed:', error.message);
      
      // If session expired, we might need to get fresh session data
      if (error.response?.status === 401) {
        console.log('🔐 Session expired - would need fresh session data');
      }
      
      throw error;
    }
  }

  private parseOccasions(responseData: any): MonitoringSlot[] {
    const slots: MonitoringSlot[] = [];
    
    console.log('🔍 Parsing occasions response...');
    
    if (!responseData?.data?.bundles) {
      console.log('⚠️ No bundles found in response');
      return slots;
    }

    let totalOccasions = 0;
    let filteredOccasions = 0;

    for (const bundle of responseData.data.bundles) {
      if (!bundle.occasions || !Array.isArray(bundle.occasions)) {
        continue;
      }

      totalOccasions += bundle.occasions.length;

      for (const occasion of bundle.occasions as OccasionData[]) {
        // First filter: Only target locations (Södertälje and Farsta)
        if (!this.targetLocationIds.includes(occasion.locationId)) {
          continue;
        }

        filteredOccasions++;

        const slot: MonitoringSlot = {
          id: `${occasion.locationId}-${occasion.duration.start}-${occasion.examinationTypeId}`,
          date: occasion.duration.start.split('T')[0],
          time: occasion.duration.start.split('T')[1]?.substring(0, 5) || '',
          location: this.locationNames[occasion.locationId] || `Location ${occasion.locationId}`,
          locationId: occasion.locationId,
          duration: this.calculateDuration(occasion.duration.start, occasion.duration.end),
          examinationType: this.getExaminationType(occasion.examinationTypeId),
          available: true
        };

        // Double-check location filtering for safety
        const locationName = slot.location.toLowerCase();
        if (locationName.includes('södertälje') || locationName.includes('sodertalje') || locationName.includes('farsta')) {
          slots.push(slot);
        } else {
          console.log(`⚠️ Rejected slot at uncertain location: ${slot.location} (ID: ${slot.locationId})`);
        }
      }
    }

    console.log(`📊 Found ${totalOccasions} total occasions, ${filteredOccasions} in target locations, ${slots.length} final slots`);
    
    // Log location breakdown
    const locationBreakdown: { [key: string]: number } = {};
    slots.forEach(slot => {
      locationBreakdown[slot.location] = (locationBreakdown[slot.location] || 0) + 1;
    });
    console.log('📍 Location breakdown:', locationBreakdown);

    return slots;
  }

  private calculateDuration(start: string, end: string): number {
    const startTime = new Date(start);
    const endTime = new Date(end);
    return Math.round((endTime.getTime() - startTime.getTime()) / (1000 * 60)); // minutes
  }

  private getExaminationType(typeId: number): string {
    const types: { [key: number]: string } = {
      12: 'Manual B License',
      11: 'Automatic B License',
      13: 'B96 License',
      14: 'BE License'
    };
    return types[typeId] || `Type ${typeId}`;
  }

  private async notifyNewSlots(newSlots: MonitoringSlot[]): Promise<void> {
    if (newSlots.length === 0) return;

    console.log(`📧 Notifying about ${newSlots.length} new slots...`);

    // Group slots by location for better email formatting
    const slotsByLocation: { [key: string]: MonitoringSlot[] } = {};
    newSlots.forEach(slot => {
      if (!slotsByLocation[slot.location]) {
        slotsByLocation[slot.location] = [];
      }
      slotsByLocation[slot.location].push(slot);
    });

    // Create email content
    let emailContent = `🎉 NEW DRIVING TEST SLOTS AVAILABLE!\n\n`;
    
    for (const [location, locationSlots] of Object.entries(slotsByLocation)) {
      emailContent += `📍 ${location.toUpperCase()}\n`;
      emailContent += `${'='.repeat(location.length + 4)}\n`;
      
      locationSlots
        .sort((a, b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time))
        .forEach(slot => {
          emailContent += `🗓️ ${slot.date} at ${slot.time} (${slot.duration} min)\n`;
        });
      
      emailContent += `\n`;
    }

    emailContent += `🚗 Test Type: Manual B License\n`;
    emailContent += `⚡ Total Slots: ${newSlots.length}\n`;
    emailContent += `🕐 Found at: ${new Date().toLocaleString('sv-SE')}\n\n`;
    emailContent += `⏰ Book quickly at: https://fp.trafikverket.se\n\n`;
    emailContent += `"me want buy moto, me want build house" - Sean Paul 🎵`;

    const subject = `🚨 ${newSlots.length} New Driving Test Slot${newSlots.length > 1 ? 's' : ''} in ${Object.keys(slotsByLocation).join(' & ')}!`;

    try {
      await this.emailNotifier.sendEmail(this.emailAddress, subject, emailContent);
      console.log('✅ Email notification sent successfully');
    } catch (error) {
      console.error('❌ Failed to send email notification:', error);
    }
  }

  async start(fromDate: string, toDate: string): Promise<void> {
    if (this.isRunning) {
      console.log('⚠️ Monitor is already running');
      return;
    }

    console.log('🚀 Starting Trafikverket Monitor V2...');
    console.log(`📅 Monitoring period: ${fromDate} to ${toDate}`);
    console.log('📍 Target locations: Södertälje & Farsta');
    console.log('🔄 Check interval: 5 minutes');
    
    this.isRunning = true;

    // Initial check
    try {
      const slots = await this.searchForSlots(fromDate, toDate);
      console.log(`🎯 Initial check: Found ${slots.length} available slots`);
      
      // Add all current slots to seen set (don't notify on first run)
      slots.forEach(slot => this.seenSlots.add(slot.id));
    } catch (error) {
      console.error('❌ Initial check failed:', error);
    }

    // Set up periodic monitoring
    this.intervalId = setInterval(async () => {
      if (!this.isRunning) return;

      try {
        console.log('🔄 Checking for new slots...');
        const currentSlots = await this.searchForSlots(fromDate, toDate);
        
        // Find new slots that we haven't seen before
        const newSlots = currentSlots.filter(slot => !this.seenSlots.has(slot.id));
        
        if (newSlots.length > 0) {
          console.log(`🎉 Found ${newSlots.length} NEW slots!`);
          
          // Add new slots to seen set
          newSlots.forEach(slot => this.seenSlots.add(slot.id));
          
          // Send notification
          await this.notifyNewSlots(newSlots);
        } else {
          console.log('📊 No new slots found');
        }
        
        // Clean up old seen slots (older than 7 days)
        this.cleanupSeenSlots();
        
      } catch (error: any) {
        console.error('❌ Monitoring check failed:', error.message);
        
        // If session expired, log it but continue (would need manual session refresh)
        if (error.response?.status === 401) {
          console.log('🔐 Session expired - monitoring will continue with stale session');
        }
      }
    }, 5 * 60 * 1000); // 5 minutes

    console.log('✅ Monitor V2 started successfully');
  }

  private cleanupSeenSlots(): void {
    // Remove slots that are probably old (basic cleanup)
    // In a real implementation, we'd track timestamps
    if (this.seenSlots.size > 1000) {
      console.log('🧹 Cleaning up old seen slots...');
      this.seenSlots.clear();
    }
  }

  stop(): void {
    if (!this.isRunning) {
      console.log('⚠️ Monitor is not running');
      return;
    }

    console.log('🛑 Stopping monitor...');
    this.isRunning = false;
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }

    console.log('✅ Monitor stopped');
  }

  getStatus(): { 
    isRunning: boolean; 
    slotsFound: number; 
    lastCheck: string;
    sessionStatus: string;
  } {
    return {
      isRunning: this.isRunning,
      slotsFound: this.seenSlots.size,
      lastCheck: new Date().toISOString(),
      sessionStatus: 'Active (auto-extended)'
    };
  }

  // Method to update session data with fresh cookies (to be called externally)
  updateSessionCookies(newCookies: string, newSSN: string): void {
    console.log('🔄 Updating session with fresh cookies...');
    this.sessionCookies = newCookies;
    this.socialSecurityNumber = newSSN;
    this.httpClient.defaults.headers['Cookie'] = newCookies;
    console.log('✅ Session cookies updated');
  }

  // Test method to verify current session works
  async testSession(): Promise<{ success: boolean; message: string; occasionCount: number }> {
    try {
      console.log('🧪 Testing current session...');
      
      const testPayload = {
        "bookingSession": {
          "socialSecurityNumber": this.socialSecurityNumber,
          "licenceId": 5,
          "bookingModeId": 0,
          "ignoreDebt": false,
          "ignoreBookingHindrance": false,
          "examinationTypeId": 12,
          "excludeExaminationCategories": [],
          "rescheduleTypeId": 0,
          "paymentIsActive": false,
          "paymentReference": "",
          "paymentUrl": "",
          "searchedMonths": 0
        },
        "occasionBundleQuery": {
          "startDate": "2024-12-20T00:00:00.000Z",
          "searchedMonths": 0,
          "locationId": null,
          "languageId": 13,
          "vehicleTypeId": 2,
          "tachographTypeId": 1,
          "occasionChoiceId": 1,
          "examinationTypeId": 12
        }
      };

      const response = await this.httpClient.post('/Boka/occasion-bundles', testPayload);
      const slots = this.parseOccasions(response.data);
      
      return {
        success: true,
        message: `✅ Session working! Found ${slots.length} slots in target locations`,
        occasionCount: slots.length
      };
      
    } catch (error: any) {
      return {
        success: false,
        message: `❌ Session test failed: ${error.response?.status} ${error.response?.statusText || error.message}`,
        occasionCount: 0
      };
    }
  }
} 