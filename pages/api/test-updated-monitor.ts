import type { NextApiRequest, NextApiResponse } from 'next';
import { TrafikverketMonitor } from '../../lib/trafikverket-monitor';
import { EmailNotifier } from '../../lib/email-notifier';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🧪 Testing updated monitoring system...');

    const emailNotifier = new EmailNotifier({
      sendgridApiKey: process.env.SENDGRID_API_KEY || '',
      fromEmail: 'monitor@trafikverket-slots.com'
    });

    const monitor = new TrafikverketMonitor({
      email: 'test@example.com',
      fromDate: '2024-12-20',
      toDate: '2025-02-01',
      emailNotifier,
      checkInterval: 300000 // 5 minutes
    });

    // Test API endpoint discovery
    console.log('🔍 Testing API endpoint discovery...');
    const reflection = (monitor as any);
    const discoveryResult = await reflection.discoverApiEndpoints();
    
    const workingEndpoints = reflection.workingEndpoints;
    const endpointCount = Object.keys(workingEndpoints).length;
    
    console.log(`📊 Discovery Result: ${discoveryResult ? 'SUCCESS' : 'FAILED'}`);
    console.log(`📊 Working Endpoints: ${endpointCount}`);
    
    // Test slot searching
    console.log('🔍 Testing slot search...');
    const slots = await reflection.searchForSlots();
    
    console.log(`🎯 Slots Found: ${slots.length}`);
    
    const response = {
      success: true,
      discoveryResult,
      endpointCount,
      workingEndpoints: Object.keys(workingEndpoints).map(ep => ({
        endpoint: ep,
        method: workingEndpoints[ep].method,
        hasData: !!workingEndpoints[ep].data,
        requiresAuth: workingEndpoints[ep].requiresAuth || false
      })),
      slotsFound: slots.length,
      slots: slots.slice(0, 3), // Only return first 3 for brevity
      timestamp: new Date().toISOString(),
      message: discoveryResult ? 
        `✅ Updated monitoring system working! Found ${endpointCount} endpoints and ${slots.length} slots` :
        '❌ Updated monitoring system still has issues with endpoint discovery'
    };

    console.log('🧪 Test completed successfully');
    return res.status(200).json(response);

  } catch (error: any) {
    console.error('❌ Test failed:', error);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
} 