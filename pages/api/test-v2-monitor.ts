import type { NextApiRequest, NextApiResponse } from 'next';
import { TrafikverketMonitorV2 } from '../../lib/trafikverket-monitor-v2';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🚀 Testing TrafikverketMonitorV2...');

    const { email = 'test@example.com', fromDate = '2024-12-20', toDate = '2025-02-01' } = req.body;

    // Create V2 monitor instance
    const monitor = new TrafikverketMonitorV2(email, fromDate, toDate);

    // Test the session first
    console.log('🧪 Testing session connectivity...');
    const sessionTest = await monitor.testSession();
    
    console.log(`Session test result: ${sessionTest.message}`);

    if (!sessionTest.success) {
      return res.status(200).json({
        success: false,
        error: 'Session test failed',
        sessionTest,
        recommendations: [
          '🔄 Session may have expired - need fresh browser cookies',
          '💡 Capture new cURL commands from browser Network tab',
          '🔐 Ensure LoginValid cookie is current'
        ],
        timestamp: new Date().toISOString()
      });
    }

    // Get monitor status
    const status = monitor.getStatus();

    return res.status(200).json({
      success: true,
      message: `✅ V2 Monitor test successful! ${sessionTest.occasionCount} occasions found`,
      sessionTest,
      monitorStatus: status,
      features: [
        '✅ Real session format with working cookies',
        '🕐 Automatic LoginValid time extension', 
        '📍 Double-layer location filtering (Södertälje & Farsta only)',
        '🔍 Proper occasion-bundles API endpoint',
        '📧 SendGrid email notifications',
        '🎯 New slot detection with seen-slot tracking'
      ],
      nextSteps: [
        '🚀 Ready to start continuous monitoring',
        '📧 Configure SendGrid API key for email alerts',
        '⏰ Monitor will auto-extend session time before each check'
      ],
      apiStructure: {
        endpoint: '/Boka/occasion-bundles',
        method: 'POST',
        dataSize: '~1.9MB per response',
        sessionExtension: 'Automatic +1 hour before each call'
      },
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ V2 Monitor test failed:', error.message);
    
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      recommendations: [
        '🔄 Check if session cookies are still valid',
        '💡 May need to refresh session from browser',
        '🔐 Verify LoginValid cookie format'
      ],
      timestamp: new Date().toISOString()
    });
  }
} 