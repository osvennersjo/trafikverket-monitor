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
      error: null,
      connectivity: {}
    };

    // First test basic connectivity to Trafikverket
    debugInfo.steps.push('Testing basic connectivity to Trafikverket...');
    try {
      const axios = require('axios');
      const connectivityResponse = await axios.get('https://fp.trafikverket.se', {
        timeout: 10000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
      });
      debugInfo.connectivity.mainSite = {
        status: connectivityResponse.status,
        accessible: true
      };
      debugInfo.steps.push(`✅ Trafikverket main site accessible (${connectivityResponse.status})`);
    } catch (connectError: any) {
      debugInfo.connectivity.mainSite = {
        status: connectError.response?.status || 'NETWORK_ERROR',
        accessible: false,
        error: connectError.message
      };
      debugInfo.steps.push(`❌ Cannot reach Trafikverket main site: ${connectError.message}`);
    }

    try {
      debugInfo.steps.push('Starting endpoint discovery...');
      
      // Access private method using type assertion for debugging
      const discoverMethod = (testMonitor as any).discoverApiEndpoints.bind(testMonitor);
      
      try {
        const endpointsFound = await discoverMethod();
        debugInfo.steps.push(`Endpoint discovery result: ${endpointsFound}`);
        debugInfo.endpoints = (testMonitor as any).workingEndpoints;
        debugInfo.endpointCount = Object.keys((testMonitor as any).workingEndpoints || {}).length;

        if (endpointsFound) {
          debugInfo.steps.push('Starting location discovery...');
          
          try {
            const findLocationsMethod = (testMonitor as any).findLocationIds.bind(testMonitor);
            const locationsFound = await findLocationsMethod();
            
            debugInfo.steps.push(`Location discovery result: ${locationsFound}`);
            debugInfo.locations = (testMonitor as any).locationIds;
            debugInfo.locationCount = Object.keys((testMonitor as any).locationIds || {}).length;

            // Try a test search
            debugInfo.steps.push('Testing slot search...');
            
            try {
              const searchMethod = (testMonitor as any).searchForSlots.bind(testMonitor);
              const testSlots = await searchMethod();
              
              debugInfo.steps.push(`Found ${testSlots.length} test slots`);
              debugInfo.testSlots = testSlots;
            } catch (searchError: any) {
              debugInfo.searchError = {
                message: searchError.message,
                stack: searchError.stack,
                response: searchError.response?.data || null,
                status: searchError.response?.status || null
              };
              debugInfo.steps.push(`Search failed: ${searchError.message}`);
            }
          } catch (locationError: any) {
            debugInfo.locationError = {
              message: locationError.message,
              stack: locationError.stack,
              response: locationError.response?.data || null,
              status: locationError.response?.status || null
            };
            debugInfo.steps.push(`Location discovery failed: ${locationError.message}`);
          }
        } else {
          debugInfo.steps.push('No endpoints found - skipping further tests');
        }
      } catch (discoveryError: any) {
        debugInfo.discoveryError = {
          message: discoveryError.message,
          stack: discoveryError.stack,
          response: discoveryError.response?.data || null,
          status: discoveryError.response?.status || null
        };
        debugInfo.steps.push(`Endpoint discovery failed: ${discoveryError.message}`);
      }

    } catch (error: any) {
      debugInfo.error = {
        message: error.message,
        stack: error.stack,
        response: error.response?.data || null,
        status: error.response?.status || null
      };
      debugInfo.steps.push(`Major error occurred: ${error.message}`);
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