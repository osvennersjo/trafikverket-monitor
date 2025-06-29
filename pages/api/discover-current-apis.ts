import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const discoveryResults: any = {
    timestamp: new Date().toISOString(),
    baseUrls: {},
    endpointPatterns: [],
    recommendations: []
  };

  // Test different base URLs
  const baseUrlsToTest = [
    'https://fp.trafikverket.se',
    'https://www.trafikverket.se',
    'https://boka.trafikverket.se',
    'https://api.trafikverket.se',
    'https://booking.trafikverket.se',
    'https://data.trafikverket.se'
  ];

  for (const baseUrl of baseUrlsToTest) {
    const urlResult: any = {
      accessible: false,
      status: null,
      redirects: false,
      finalUrl: null,
      error: null
    };

    try {
      const response = await axios.get(baseUrl, {
        timeout: 10000,
        maxRedirects: 5,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
      });

      urlResult.accessible = true;
      urlResult.status = response.status;
      urlResult.finalUrl = response.request?.responseURL || baseUrl;
      urlResult.redirects = baseUrl !== urlResult.finalUrl;

      // Check if it mentions booking or API
      const content = response.data?.toString() || '';
      urlResult.mentionsBooking = content.toLowerCase().includes('book') || content.toLowerCase().includes('boka');
      urlResult.mentionsApi = content.toLowerCase().includes('api');
      
    } catch (error: any) {
      urlResult.error = error.message;
      urlResult.status = error.response?.status || 'NETWORK_ERROR';
    }

    discoveryResults.baseUrls[baseUrl] = urlResult;
  }

  // Test modern API patterns
  const modernPatterns = [
    '/api/v1/occasions',
    '/api/v2/occasions', 
    '/api/v1/locations',
    '/api/v2/locations',
    '/api/booking/occasions',
    '/api/booking/locations',
    '/booking/api/occasions',
    '/booking/api/locations',
    '/rest/api/occasions',
    '/rest/api/locations',
    '/graphql',
    '/.well-known/api',
    '/api',
    '/api/',
    '/swagger',
    '/openapi.json'
  ];

  // Test patterns against accessible base URLs
  const accessibleUrls = Object.keys(discoveryResults.baseUrls)
    .filter(url => discoveryResults.baseUrls[url].accessible);

  for (const baseUrl of accessibleUrls) {
    for (const pattern of modernPatterns) {
      try {
        const fullUrl = baseUrl + pattern;
        const response = await axios.get(fullUrl, {
          timeout: 5000,
          headers: {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*'
          }
        });

        if (response.status === 200) {
          discoveryResults.endpointPatterns.push({
            url: fullUrl,
            status: response.status,
            hasData: !!response.data,
            responseType: typeof response.data,
            responseSize: JSON.stringify(response.data).length,
            contentType: response.headers['content-type']
          });
        }
      } catch (error: any) {
        // Only log interesting non-404 errors
        if (error.response?.status && ![404, 403, 405].includes(error.response.status)) {
          discoveryResults.endpointPatterns.push({
            url: baseUrl + pattern,
            status: error.response.status,
            error: error.message,
            hasData: false
          });
        }
      }

      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  // Generate recommendations
  if (discoveryResults.baseUrls['https://fp.trafikverket.se']?.accessible) {
    discoveryResults.recommendations.push({
      type: 'investigation',
      message: 'fp.trafikverket.se is accessible. Visit the booking page manually and inspect network requests to find current API endpoints.',
      action: 'Open browser dev tools on https://fp.trafikverket.se/boka and look at Network tab'
    });
  }

  if (discoveryResults.baseUrls['https://data.trafikverket.se']?.accessible) {
    discoveryResults.recommendations.push({
      type: 'data_portal',
      message: 'data.trafikverket.se is accessible - this might be their official data/API portal',
      action: 'Investigate https://data.trafikverket.se for official API documentation'
    });
  }

  const workingEndpoints = discoveryResults.endpointPatterns.filter((ep: any) => ep.status === 200);
  if (workingEndpoints.length === 0) {
    discoveryResults.recommendations.push({
      type: 'manual_investigation',
      message: 'No working API endpoints found automatically. Manual investigation needed.',
      action: 'Use browser dev tools to inspect actual booking requests on the Trafikverket website'
    });
  }

  // Summary
  discoveryResults.summary = {
    accessibleBaseUrls: accessibleUrls.length,
    workingEndpoints: workingEndpoints.length,
    totalTestedEndpoints: discoveryResults.endpointPatterns.length,
    needsManualInvestigation: workingEndpoints.length === 0
  };

  res.status(200).json(discoveryResults);
} 