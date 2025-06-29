import { NextApiRequest, NextApiResponse } from 'next';
import { monitoringInstance } from './start-monitoring';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    if (monitoringInstance) {
      monitoringInstance.stop();
      res.status(200).json({ success: true, message: 'Monitoring stopped' });
    } else {
      res.status(200).json({ success: true, message: 'No monitoring was active' });
    }
  } catch (error) {
    console.error('Error stopping monitoring:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
} 