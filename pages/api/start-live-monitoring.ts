import type { NextApiRequest, NextApiResponse } from 'next';
import { TrafikverketMonitorV2 } from '../../lib/trafikverket-monitor-v2';

// Global monitor instance
let globalMonitor: TrafikverketMonitorV2 | null = null;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { email, fromDate, toDate, action } = req.body;

    if (action === 'start') {
      // Stop any existing monitor first
      if (globalMonitor) {
        globalMonitor.stop();
        console.log('🛑 Stopped existing monitor');
      }

      console.log('🚀 Starting live monitoring...');
      console.log(`📧 Email: ${email}`);
      console.log(`📅 Date range: ${fromDate} to ${toDate}`);

      // Ensure SendGrid API key is available
      if (!process.env.SENDGRID_API_KEY) {
        return res.status(500).json({
          success: false,
          error: 'SendGrid API key not configured',
          recommendation: 'Set SENDGRID_API_KEY environment variable in Netlify deployment settings',
          timestamp: new Date().toISOString()
        });
      }

      // Create new V2 monitor instance
      globalMonitor = new TrafikverketMonitorV2(email, fromDate, toDate);

      // Test session first
      const sessionTest = await globalMonitor.testSession();
      if (!sessionTest.success) {
        return res.status(400).json({
          success: false,
          error: 'Session test failed - need fresh cookies',
          sessionTest,
          recommendation: 'Get fresh session cookies from browser Network tab',
          timestamp: new Date().toISOString()
        });
      }

      // Start monitoring
      await globalMonitor.start(fromDate, toDate);

      return res.status(200).json({
        success: true,
        message: '🚀 Live monitoring started successfully!',
        status: {
          isActive: true,
          email: email,
          fromDate: fromDate,
          toDate: toDate,
          sessionWorking: true,
          occasionsFound: sessionTest.occasionCount,
          checkInterval: '5 minutes',
          timeExtension: 'Automatic',
          emailProvider: 'SendGrid',
          locations: ['Södertälje', 'Farsta']
        },
        features: [
          '✅ 24/7 continuous monitoring active',
          '⏰ Automatic session time extension',
          '📧 Instant email notifications via SendGrid',
          '🎯 5-minute check intervals',
          '📍 Södertälje & Farsta locations only',
          '🔍 New slot detection with duplicate prevention'
        ],
        timestamp: new Date().toISOString()
      });

    } else if (action === 'stop') {
      if (globalMonitor) {
        globalMonitor.stop();
        globalMonitor = null;
        console.log('🛑 Live monitoring stopped');

        return res.status(200).json({
          success: true,
          message: '🛑 Live monitoring stopped successfully',
          status: {
            isActive: false,
            stoppedAt: new Date().toISOString()
          },
          timestamp: new Date().toISOString()
        });
      } else {
        return res.status(400).json({
          success: false,
          error: 'No active monitoring to stop',
          timestamp: new Date().toISOString()
        });
      }

    } else if (action === 'status') {
      if (globalMonitor) {
        const status = globalMonitor.getStatus();
        return res.status(200).json({
          success: true,
          status: {
            isActive: status.isRunning,
            slotsFound: status.slotsFound,
            lastCheck: status.lastCheck,
            sessionStatus: status.sessionStatus
          },
          timestamp: new Date().toISOString()
        });
      } else {
        return res.status(200).json({
          success: true,
          status: {
            isActive: false,
            message: 'No active monitoring'
          },
          timestamp: new Date().toISOString()
        });
      }
    }

    return res.status(400).json({
      success: false,
      error: 'Invalid action. Use start, stop, or status',
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Live monitoring error:', error.message);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      recommendation: 'Check session cookies or try restarting',
      timestamp: new Date().toISOString()
    });
  }
} 