import { NextApiRequest, NextApiResponse } from 'next';
import { TrafikverketMonitor } from '../../lib/trafikverket-monitor';
import { EmailNotifier } from '../../lib/email-notifier';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🔧 Starting debug monitoring test...');

    // Create a temporary monitor instance for testing
    const emailNotifier = new EmailNotifier({
      sendgridApiKey: process.env.SENDGRID_API_KEY || '',
      fromEmail: process.env.FROM_EMAIL || 'monitor@trafikverket-monitor.app',
    });

    const testMonitor = new TrafikverketMonitor({
      email: 'test@example.com',
      fromDate: new Date().toISOString().split('T')[0],
      toDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days from now
      emailNotifier,
      checkInterval: 5 * 60 * 1000,
    });

    // Test the discovery process step by step
    const debugInfo: any = {
      timestamp: new Date().toISOString(),
      steps: [],
      endpoints: {},
      locations: {},
      error: null
    };

    try {
      debugInfo.steps.push('Starting endpoint discovery...');
      
      // Access private method using type assertion for debugging
      const discoverMethod = (testMonitor as any).discoverApiEndpoints.bind(testMonitor);
      const endpointsFound = await discoverMethod();
      
      debugInfo.steps.push(`Endpoint discovery result: ${endpointsFound}`);
      debugInfo.endpoints = (testMonitor as any).workingEndpoints;

      if (endpointsFound) {
        debugInfo.steps.push('Starting location discovery...');
        
        const findLocationsMethod = (testMonitor as any).findLocationIds.bind(testMonitor);
        const locationsFound = await findLocationsMethod();
        
        debugInfo.steps.push(`Location discovery result: ${locationsFound}`);
        debugInfo.locations = (testMonitor as any).locationIds;

        // Try a test search
        debugInfo.steps.push('Testing slot search...');
        
        const searchMethod = (testMonitor as any).searchForSlots.bind(testMonitor);
        const testSlots = await searchMethod();
        
        debugInfo.steps.push(`Found ${testSlots.length} test slots`);
        debugInfo.testSlots = testSlots;
      }

    } catch (error: any) {
      debugInfo.error = {
        message: error.message,
        stack: error.stack,
        response: error.response?.data || null,
        status: error.response?.status || null
      };
      debugInfo.steps.push(`Error occurred: ${error.message}`);
    }

    // Clean up
    testMonitor.stop();

    res.status(200).json({
      success: true,
      debug: debugInfo
    });

  } catch (error: any) {
    console.error('Debug test failed:', error);
    res.status(500).json({ 
      error: 'Debug test failed',
      details: error.message,
      stack: error.stack
    });
  }
} 