import type { NextApiRequest, NextApiResponse } from 'next';
import { TrafikverketMonitor } from '../../lib/trafikverket-monitor';
import { EmailNotifier } from '../../lib/email-notifier';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🧪 Testing updated monitoring system...');

    // Test EmailNotifier creation first
    console.log('📧 Creating EmailNotifier...');
    const emailNotifier = new EmailNotifier({
      sendgridApiKey: process.env.SENDGRID_API_KEY || '',
      fromEmail: 'monitor@trafikverket-slots.com'
    });
    console.log('✅ EmailNotifier created successfully');

    // Test TrafikverketMonitor creation
    console.log('🚗 Creating TrafikverketMonitor...');
    const monitor = new TrafikverketMonitor({
      email: 'test@example.com',
      fromDate: '2024-12-20',
      toDate: '2025-02-01',
      emailNotifier,
      checkInterval: 300000 // 5 minutes
    });
    console.log('✅ TrafikverketMonitor created successfully');

    // Test API endpoint discovery with detailed logging
    console.log('🔍 Testing API endpoint discovery...');
    const reflection = (monitor as any);
    
    let discoveryResult = false;
    let discoveryError = null;
    try {
      discoveryResult = await reflection.discoverApiEndpoints();
      console.log(`📊 Discovery completed: ${discoveryResult ? 'SUCCESS' : 'FAILED'}`);
    } catch (error: any) {
      discoveryError = error;
      console.error('❌ Discovery failed with error:', error.message || error);
    }
    
    const workingEndpoints = reflection.workingEndpoints || {};
    const endpointCount = Object.keys(workingEndpoints).length;
    
    console.log(`📊 Working Endpoints: ${endpointCount}`);
    console.log('📊 Endpoint details:', Object.keys(workingEndpoints));
    
    // Test slot searching with detailed logging
    console.log('🔍 Testing slot search...');
    let slots = [];
    let searchError = null;
    try {
      slots = await reflection.searchForSlots();
      console.log(`🎯 Slots Found: ${slots.length}`);
    } catch (error: any) {
      searchError = error;
      console.error('❌ Slot search failed with error:', error.message || error);
    }
    
    const response = {
      success: true,
      discoveryResult,
      discoveryError: discoveryError ? {
        message: discoveryError.message || 'Unknown discovery error',
        stack: discoveryError.stack,
        name: discoveryError.name
      } : null,
      searchError: searchError ? {
        message: searchError.message || 'Unknown search error',
        stack: searchError.stack,
        name: searchError.name
      } : null,
      endpointCount,
      workingEndpoints: Object.keys(workingEndpoints).map(ep => ({
        endpoint: ep,
        method: workingEndpoints[ep].method,
        hasData: !!workingEndpoints[ep].data,
        requiresAuth: workingEndpoints[ep].requiresAuth || false,
        dataKeys: workingEndpoints[ep].data ? Object.keys(workingEndpoints[ep].data).slice(0, 5) : []
      })),
      slotsFound: slots.length,
      slots: slots.slice(0, 3), // Only return first 3 for brevity
      timestamp: new Date().toISOString(),
      message: discoveryResult ? 
        `✅ Updated monitoring system working! Found ${endpointCount} endpoints and ${slots.length} slots` :
        `⚠️ Updated monitoring system partially working - ${endpointCount} endpoints found but ${discoveryError ? 'discovery failed' : 'discovery succeeded'}`
    };

    console.log('🧪 Test completed successfully');
    console.log('📊 Final response:', JSON.stringify(response, null, 2));
    
    return res.status(200).json(response);

  } catch (error: any) {
    console.error('❌ Test failed with error:', error);
    console.error('❌ Error type:', typeof error);
    console.error('❌ Error message:', error?.message);
    console.error('❌ Error stack:', error?.stack);
    console.error('❌ Error name:', error?.name);
    
    const errorResponse = { 
      success: false, 
      error: error?.message || 'Unknown error occurred',
      errorType: typeof error,
      errorName: error?.name || 'Unknown',
      errorStack: error?.stack || 'No stack trace',
      timestamp: new Date().toISOString()
    };
    
    console.log('📊 Error response:', JSON.stringify(errorResponse, null, 2));
    
    return res.status(500).json(errorResponse);
  }
} 