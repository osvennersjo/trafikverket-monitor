import { NextApiRequest, NextApiResponse } from 'next';
import { TrafikverketMonitor } from '../../lib/trafikverket-monitor';
import { EmailNotifier } from '../../lib/email-notifier';

interface StartMonitoringRequest {
  email: string;
  fromDate: string;
  toDate: string;
}

let monitoringInstance: TrafikverketMonitor | null = null;

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { email, fromDate, toDate }: StartMonitoringRequest = req.body;

    // Validate input
    if (!email || !fromDate || !toDate) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    if (new Date(fromDate) >= new Date(toDate)) {
      return res.status(400).json({ error: 'From date must be before to date' });
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ error: 'Invalid email format' });
    }

    // Stop existing monitoring if running
    if (monitoringInstance) {
      monitoringInstance.stop();
    }

    // Ensure SendGrid API key is available
    if (!process.env.SENDGRID_API_KEY) {
      return res.status(500).json({
        error: 'SendGrid API key not configured',
        recommendation: 'Set SENDGRID_API_KEY environment variable in Netlify deployment settings'
      });
    }

    // Create email notifier with SendGrid
    const emailNotifier = new EmailNotifier();

    // Create and start monitoring
    monitoringInstance = new TrafikverketMonitor({
      email,
      fromDate,
      toDate,
      emailNotifier,
      checkInterval: 5 * 60 * 1000, // 5 minutes
    });

    const success = await monitoringInstance.start();

    if (success) {
      res.status(200).json({ 
        success: true, 
        message: 'Monitoring started successfully',
        email,
        fromDate,
        toDate
      });
    } else {
      res.status(500).json({ 
        error: 'Failed to start monitoring - could not connect to Trafikverket API endpoints. The website structure may have changed or there may be connectivity issues.' 
      });
    }

  } catch (error) {
    console.error('Error starting monitoring:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

// Export the monitoring instance for other API routes to access
export { monitoringInstance }; 