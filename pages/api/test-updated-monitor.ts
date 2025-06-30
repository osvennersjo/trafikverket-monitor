import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Debug endpoint disabled - use live monitoring instead
  return res.status(410).json({ 
    error: 'Debug endpoints have been removed. Please use the live monitoring system instead.',
    recommendation: 'Click "START LIVE MONITORING" button on the main page'
  });
} 