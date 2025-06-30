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

    // Ensure SendGrid API key is available
    if (!process.env.SENDGRID_API_KEY) {
      return res.status(500).json({
        success: false,
        error: 'SendGrid API key not configured',
        details: 'Set SENDGRID_API_KEY environment variable in Netlify deployment settings',
        timestamp: new Date().toISOString()
      });
    }

    // Create EmailNotifier instance
    const emailNotifier = new EmailNotifier();

    // Send test email using the new method
    const result = await emailNotifier.sendTestEmail(email);

    if (result.success) {
      res.status(200).json({
        success: true,
        message: 'Test email sent successfully!',
        email: email,
        provider: 'SendGrid',
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(500).json({
        success: false,
        error: 'Failed to send test email',
        details: result.details,
        timestamp: new Date().toISOString()
      });
    }

  } catch (error) {
    console.error('Test email failed:', error);
    
    let errorMessage = 'Failed to send test email';
    let details = '';
    
    if (error instanceof Error) {
      if (error.message.includes('SendGrid')) {
        details = 'SendGrid API error - check your API key';
      } else if (error.message.includes('401')) {
        details = 'Unauthorized - check your SendGrid API key';
      } else if (error.message.includes('403')) {
        details = 'Forbidden - check your SendGrid account status';
      } else {
        details = error.message;
      }
    }

    res.status(500).json({
      success: false,
      error: errorMessage,
      details: details,
      timestamp: new Date().toISOString()
    });
  }
} 