import { NextApiRequest, NextApiResponse } from 'next';
import { monitoringInstance } from './start-monitoring';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    if (monitoringInstance && monitoringInstance.isActive()) {
      const status = monitoringInstance.getStatus();
      res.status(200).json(status);
    } else {
      res.status(200).json({
        isActive: false,
        email: '',
        fromDate: '',
        toDate: '',
        slotsFound: 0,
        lastCheck: ''
      });
    }
  } catch (error) {
    console.error('Error getting status:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
} 