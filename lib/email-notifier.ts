import sgMail from '@sendgrid/mail';

export class EmailNotifier {
  private isConfigured: boolean = false;

  constructor() {
    this.initializeSendGrid();
  }

  private initializeSendGrid(): void {
    const apiKey = process.env.SENDGRID_API_KEY;
    
    if (apiKey) {
      sgMail.setApiKey(apiKey);
      this.isConfigured = true;
      console.log('📧 SendGrid configured successfully');
    } else {
      console.warn('⚠️ SendGrid API key not found in environment variables');
      this.isConfigured = false;
    }
  }

  async sendNotification(email: string, slots: any[], locations: string[]): Promise<boolean> {
    if (!this.isConfigured) {
      console.error('❌ EmailNotifier not configured - missing SendGrid API key');
      return false;
    }

    try {
      const locationStr = locations.join(' or ');
      const slotCount = slots.length;
      
      // Create slot details
      const slotDetails = slots.map(slot => {
        const date = new Date(slot.startTime);
        const dateStr = date.toLocaleDateString('sv-SE');
        const timeStr = date.toLocaleTimeString('sv-SE', { 
          hour: '2-digit', 
          minute: '2-digit' 
        });
        
        return `📅 ${dateStr} at ${timeStr} in ${slot.location}`;
      }).join('\n');

      const subject = `🚗 ${slotCount} driving test slot${slotCount > 1 ? 's' : ''} available in ${locationStr}!`;
      
      const htmlContent = `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; overflow: hidden;">
          <div style="padding: 30px; text-align: center;">
            <h1 style="margin: 0 0 20px 0; font-size: 28px;">🚗 DRIVING TEST ALERT!</h1>
            <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 20px; margin: 20px 0;">
              <h2 style="margin: 0 0 15px 0; color: #FFD700;">
                ${slotCount} slot${slotCount > 1 ? 's' : ''} available in ${locationStr}!
              </h2>
              <div style="text-align: left; background: rgba(255,255,255,0.9); color: #333; padding: 15px; border-radius: 5px; margin: 15px 0;">
                ${slotDetails.split('\n').map(slot => `<div style="margin: 5px 0;">${slot}</div>`).join('')}
              </div>
            </div>
            
            <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; margin: 20px 0;">
              <p style="margin: 5px 0; font-size: 16px;">⚡ <strong>Book NOW at:</strong></p>
              <a href="https://fp.trafikverket.se" style="color: #FFD700; text-decoration: none; font-size: 18px; font-weight: bold;">
                fp.trafikverket.se
              </a>
            </div>
            
            <div style="margin: 25px 0; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
              <p style="margin: 0; font-style: italic; font-size: 18px;">
                "me want buy moto, me want build house"
              </p>
              <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">- Sean Paul motivation 🎵</p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.3);">
              <p style="margin: 0; font-size: 14px; opacity: 0.8;">
                Powered by Trafikverket Monitor ⚡ SendGrid
              </p>
            </div>
          </div>
        </div>
      `;

      const textContent = `
🚗 DRIVING TEST ALERT!

${slotCount} slot${slotCount > 1 ? 's' : ''} available in ${locationStr}!

${slotDetails}

⚡ Book NOW at: https://fp.trafikverket.se

"me want buy moto, me want build house" - Sean Paul 🎵

Powered by Trafikverket Monitor
      `.trim();

      const msg = {
        to: email,
        from: {
          email: 'osvennersjo@gmail.com',
          name: 'Trafikverket Monitor'
        },
        subject: subject,
        text: textContent,
        html: htmlContent,
        trackingSettings: {
          clickTracking: {
            enable: false
          }
        }
      };

      await sgMail.send(msg);
      
      console.log(`✅ Email notification sent successfully to ${email}`);
      console.log(`📧 Subject: ${subject}`);
      console.log(`🎯 Slots: ${slotCount} in ${locationStr}`);
      
      return true;

    } catch (error: any) {
      console.error('❌ Failed to send email notification:', error);
      
      if (error.response) {
        console.error('📧 SendGrid error details:', {
          status: error.response.status,
          body: error.response.body
        });
      }
      
      return false;
    }
  }

  async sendTestEmail(email: string): Promise<{ success: boolean; details?: string }> {
    if (!this.isConfigured) {
      return {
        success: false,
        details: 'SendGrid not configured - missing API key'
      };
    }

    try {
      const subject = '🧪 Test Email from Trafikverket Monitor';
      
      const htmlContent = `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 10px; overflow: hidden;">
          <div style="padding: 30px; text-align: center;">
            <h1 style="margin: 0 0 20px 0; font-size: 28px;">🧪 Test Email Success!</h1>
            
            <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 20px; margin: 20px 0;">
              <h2 style="margin: 0 0 15px 0; color: #FFD700;">✅ Email Configuration Working!</h2>
              <p style="margin: 10px 0; font-size: 16px;">
                Your email setup is working perfectly. You'll receive notifications when driving test slots become available in Södertälje or Farsta.
              </p>
            </div>
            
            <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; margin: 20px 0;">
              <p style="margin: 5px 0; font-size: 16px;">🎯 <strong>Monitoring Features:</strong></p>
              <div style="text-align: left; margin: 10px 0;">
                <div style="margin: 5px 0;">📍 Södertälje & Farsta locations</div>
                <div style="margin: 5px 0;">⏰ 5-minute check intervals</div>
                <div style="margin: 5px 0;">🚀 24/7 live monitoring</div>
                <div style="margin: 5px 0;">⚡ Automatic session extension</div>
                <div style="margin: 5px 0;">📧 Instant SendGrid notifications</div>
              </div>
            </div>
            
            <div style="margin: 25px 0; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
              <p style="margin: 0; font-style: italic; font-size: 18px;">
                "five million and footi nooti shawties! baby girl"
              </p>
              <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">- Sean Paul motivation 🎵</p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.3);">
              <p style="margin: 0; font-size: 14px; opacity: 0.8;">
                Test email sent via SendGrid ⚡ Ready to monitor!
              </p>
            </div>
          </div>
        </div>
      `;

      const textContent = `
🧪 Test Email Success!

✅ Email Configuration Working!

Your email setup is working perfectly. You'll receive notifications when driving test slots become available in Södertälje or Farsta.

🎯 Monitoring Features:
📍 Södertälje & Farsta locations
⏰ 5-minute check intervals  
🚀 24/7 live monitoring
⚡ Automatic session extension
📧 Instant SendGrid notifications

"five million and footi nooti shawties! baby girl" - Sean Paul 🎵

Test email sent via SendGrid ⚡ Ready to monitor!
      `.trim();

      const msg = {
        to: email,
        from: {
          email: 'osvennersjo@gmail.com',
          name: 'Trafikverket Monitor'
        },
        subject: subject,
        text: textContent,
        html: htmlContent,
        trackingSettings: {
          clickTracking: {
            enable: false
          }
        }
      };

      await sgMail.send(msg);
      
      console.log(`✅ Test email sent successfully to ${email}`);
      return {
        success: true,
        details: 'Test email sent successfully via SendGrid'
      };

    } catch (error: any) {
      console.error('❌ Failed to send test email:', error);
      
      let errorDetails = 'Unknown SendGrid error';
      
      if (error.response) {
        errorDetails = `SendGrid error ${error.response.status}: ${JSON.stringify(error.response.body)}`;
      } else if (error.message) {
        errorDetails = error.message;
      }
      
      return {
        success: false,
        details: errorDetails
      };
    }
  }
} 