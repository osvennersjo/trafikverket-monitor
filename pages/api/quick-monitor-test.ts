import type { NextApiRequest, NextApiResponse } from 'next';
import { TrafikverketMonitor } from '../../lib/trafikverket-monitor';
import { EmailNotifier } from '../../lib/email-notifier';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('⚡ Quick monitoring system test...');

    const emailNotifier = new EmailNotifier({
      sendgridApiKey: process.env.SENDGRID_API_KEY || '',
      fromEmail: 'monitor@trafikverket-slots.com'
    });

    const monitor = new TrafikverketMonitor({
      email: 'test@example.com',
      fromDate: '2024-12-20',
      toDate: '2025-01-15', // Shorter date range
      emailNotifier,
      checkInterval: 300000
    });

    // Quick test with timeout protection
    const testTimeout = 8000; // 8 seconds max
    const startTime = Date.now();
    
    const testPromise = async () => {
      console.log('🔍 Quick endpoint discovery...');
      const reflection = (monitor as any);
      
      // Test just the priority endpoints quickly
      let discoveryResult = false;
      let endpointCount = 0;
      let error = null;
      
      try {
        discoveryResult = await reflection.discoverApiEndpoints();
        const workingEndpoints = reflection.workingEndpoints || {};
        endpointCount = Object.keys(workingEndpoints).length;
        
        console.log(`📊 Quick discovery: ${discoveryResult ? 'SUCCESS' : 'FAILED'}`);
        console.log(`📊 Endpoints found: ${endpointCount}`);
        
        return {
          success: true,
          discoveryResult,
          endpointCount,
          workingEndpoints: Object.keys(workingEndpoints),
          duration: Date.now() - startTime,
          message: `⚡ Quick test: ${endpointCount} endpoints found in ${Date.now() - startTime}ms`
        };
      } catch (err: any) {
        error = err;
        return {
          success: false,
          error: err.message,
          duration: Date.now() - startTime,
          message: `❌ Quick test failed: ${err.message}`
        };
      }
    };

    // Race against timeout
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Quick test timed out')), testTimeout);
    });

    const result = await Promise.race([testPromise(), timeoutPromise]) as any;
    
    console.log('⚡ Quick test completed');
    return res.status(200).json({
      ...result,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Quick test failed:', error.message);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      message: 'Quick test failed',
      timestamp: new Date().toISOString()
    });
  }
} 