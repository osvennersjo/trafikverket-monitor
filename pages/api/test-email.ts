import { NextApiRequest, NextApiResponse } from 'next';
import { EmailNotifier } from '../../lib/email-notifier';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({ error: 'Email address is required' });
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ error: 'Invalid email format' });
    }

    const emailNotifier = new EmailNotifier({
      sendgridApiKey: process.env.SENDGRID_API_KEY || '',
      fromEmail: process.env.FROM_EMAIL || ''
    });

    // Test SendGrid connection first
    const connectionTest = await emailNotifier.testConnection();
    if (!connectionTest) {
      return res.status(500).json({ 
        error: 'SendGrid connection failed',
        details: 'Check your SENDGRID_API_KEY environment variable'
      });
    }

    // Send test email
    const subject = '🧪 Trafikverket Monitor Test Email';
    const testMessage = `🎉 Congratulations! Your email configuration is working perfectly!

📧 This is a test email to verify that:
✅ Your email address (${email}) is valid
✅ SendGrid API is properly configured
✅ FROM_EMAIL environment variable is set
✅ Email notifications will work when driving test slots are found

🚗 Next steps:
1. Start monitoring for driving test slots
2. Wait for notifications when slots become available
3. Book your test quickly!

🎵 Sean Paul says: "Just gimme the light... and soon you'll have your körkort!"

---
🔧 Trafikverket Monitor Test System
Made with ❤️ for future drivers`;

    await emailNotifier.sendEmail(email, subject, testMessage);

    res.status(200).json({
      success: true,
      message: 'Test email sent successfully!',
      email: email,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Test email failed:', error);
    
    let errorMessage = 'Failed to send test email';
    let details = '';
    
    if (error instanceof Error) {
      if (error.message.includes('SendGrid')) {
        details = 'SendGrid API error - check your API key and FROM_EMAIL settings';
      } else if (error.message.includes('401')) {
        details = 'Unauthorized - check your SendGrid API key';
      } else if (error.message.includes('403')) {
        details = 'Forbidden - check your SendGrid account status and FROM_EMAIL verification';
      } else {
        details = error.message;
      }
    }

    res.status(500).json({
      error: errorMessage,
      details: details,
      timestamp: new Date().toISOString()
    });
  }
} 