interface EmailConfig {
  sendgridApiKey: string;
  fromEmail: string;
}

export class EmailNotifier {
  private config: EmailConfig;

  constructor(config: EmailConfig) {
    this.config = config;
  }

  async sendEmail(to: string, subject: string, text: string): Promise<void> {
    try {
      if (!this.config.sendgridApiKey) {
        console.log('🎉 DRIVING TEST SLOT FOUND! 🎉');
        console.log(`📧 Email would be sent to: ${to}`);
        console.log(`📋 Subject: ${subject}`);
        console.log(`📝 Message: ${text}`);
        console.log('🎵 Sean Paul says: "Just gimme the light... and your körkort!"');
        
        // No SendGrid API key configured
        return;
      }

      const htmlContent = this.convertTextToHtml(text);

      const emailData = {
        personalizations: [
          {
            to: [{ email: to }],
            subject: subject
          }
        ],
        from: {
          email: this.config.fromEmail,
          name: "Trafikverket Monitor"
        },
        content: [
          {
            type: "text/plain",
            value: text
          },
          {
            type: "text/html",
            value: htmlContent
          }
        ]
      };

      const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.sendgridApiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(emailData)
      });

      if (response.ok) {
        console.log(`✅ Email sent successfully to ${to} via SendGrid`);
      } else {
        const error = await response.text();
        console.error('❌ SendGrid API error:', error);
        throw new Error(`SendGrid API error: ${response.status}`);
      }
      
    } catch (error) {
      console.error('❌ Failed to send email:', error);
      throw error;
    }
  }

  private convertTextToHtml(text: string): string {
    // Convert plain text to HTML with basic formatting
    let html = text
      .replace(/\n/g, '<br>')
      .replace(/📅/g, '📅')
      .replace(/🕐/g, '🕐')
      .replace(/📍/g, '📍')
      .replace(/🚗/g, '🚗')
      .replace(/🔗/g, '🔗')
      .replace(/🏃‍♂️/g, '🏃‍♂️')
      .replace(/🍀/g, '🍀')
      .replace(/🎵/g, '🎵');

    // Wrap in basic HTML structure
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trafikverket Slot Alert</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
          }
          .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          }
          h1 {
            color: #2c5530;
            text-align: center;
            margin-bottom: 30px;
          }
          .slot-info {
            background-color: #e8f5e8;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #4caf50;
          }
          .cta {
            background-color: #4caf50;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            font-weight: bold;
            margin: 20px 0;
          }
          .sean-paul-section {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin-top: 30px;
            text-align: center;
            border: 1px solid #ffeaa7;
          }
          hr {
            border: none;
            border-top: 1px solid #eee;
            margin: 20px 0;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>🚗 Driving Test Slots Available!</h1>
          <div style="font-size: 16px;">
            ${html}
          </div>
          
          <div class="sean-paul-section">
            <h3>🎵 Sean Paul says:</h3>
            <p><em>"Just gimme the light and pass the doh... and your körkort!"</em></p>
            <p>🎶 Good luck with your test! 🎶</p>
          </div>
          
          <hr>
          <p style="text-align: center; color: #666; font-size: 14px;">
            This notification was sent by the Trafikverket Monitor.<br>
            Made with ❤️ for future drivers.
          </p>
        </div>
      </body>
      </html>
    `;
  }

  async testConnection(): Promise<boolean> {
    try {
      if (!this.config.sendgridApiKey) {
        console.log('ℹ️ SendGrid API key not configured - test skipped');
        return true; // Don't fail if email is not configured
      }

      // Test SendGrid API connection with a simple request
      const response = await fetch('https://api.sendgrid.com/v3/user/profile', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.config.sendgridApiKey}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        console.log('✅ SendGrid connection test successful');
        return true;
      } else {
        console.error('❌ SendGrid connection test failed:', response.status);
        return false;
      }
    } catch (error) {
      console.error('❌ SendGrid connection test failed:', error);
      return false;
    }
  }
} 