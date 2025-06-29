import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🔐 Testing different authentication methods...');

    const basePayload = {
      bookingSession: {
        socialSecurityNumber: '',
        licenceId: 5,
        bookingModeId: 0
      },
      occasionBundleQuery: {
        startDate: '2024-12-20',
        endDate: '2025-01-15',
        locationId: null,
        examinationTypeId: 5,
        tachographTypeId: 1,
        occasionChoiceId: 1,
        searchedMonths: 0
      }
    };

    // Different authentication approaches to test
    const authMethods = [
      {
        name: 'No authentication (baseline)',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'application/json, text/plain, */*',
          'Content-Type': 'application/json'
        }
      },
      {
        name: 'With common session headers',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'application/json, text/plain, */*',
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      },
      {
        name: 'With dummy session cookie',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'application/json, text/plain, */*',
          'Content-Type': 'application/json',
          'Cookie': 'ASP.NET_SessionId=dummy123456789; .ASPXAUTH=dummyauth'
        }
      },
      {
        name: 'With security headers',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'application/json, text/plain, */*',
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'Sec-Fetch-Dest': 'empty',
          'Sec-Fetch-Mode': 'cors',
          'Sec-Fetch-Site': 'same-origin',
          'Referer': 'https://fp.trafikverket.se/boka/'
        }
      },
      {
        name: 'Try GET first (session setup)',
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
      }
    ];

    const results = [];

    for (const method of authMethods) {
      try {
        console.log(`🔐 Testing: ${method.name}`);
        
        const httpClient = axios.create({
          baseURL: 'https://fp.trafikverket.se',
          timeout: 5000,
          headers: method.headers
        });

        let response;
        if (method.method === 'GET') {
          // Try GET to see if we can establish a session
          response = await httpClient.get('/Boka/occasion-bundles');
        } else {
          response = await httpClient.post('/Boka/occasion-bundles', basePayload);
        }
        
        const responseText = JSON.stringify(response.data);
        const isHtml = responseText.includes('<!doctype html>');
        
        results.push({
          name: method.name,
          success: true,
          status: response.status,
          responseType: typeof response.data,
          isHtml: isHtml,
          responseSize: responseText.length,
          hasSlots: !isHtml && response.data && (response.data.occasions || response.data.occasionBundles),
          message: isHtml ? '📄 Returns HTML page' : '✅ Returns JSON data',
          responsePreview: responseText.substring(0, 200) + '...'
        });
        
      } catch (error: any) {
        const status = error.response?.status;
        const responseData = error.response?.data;
        
        results.push({
          name: method.name,
          success: false,
          status: status,
          responseData: typeof responseData === 'string' ? responseData.substring(0, 100) : responseData,
          message: status === 400 ? '❌ Bad Request' : 
                  status === 401 ? '🔐 Unauthorized' :
                  status === 403 ? '🔐 Forbidden' :
                  status === 404 ? '❌ Not Found' :
                  `❌ Error ${status}`,
          authRequired: status === 401 || status === 403
        });
        
        console.log(`❌ ${method.name}: ${status}`);
      }
      
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 300));
    }

    const summary = {
      total: results.length,
      successful: results.filter(r => r.success).length,
      unauthorized: results.filter(r => r.status === 401 || r.status === 403).length,
      badRequest: results.filter(r => r.status === 400).length,
      jsonResponses: results.filter(r => r.success && !r.isHtml).length,
      results: results
    };

    console.log('🔐 Authentication method test completed');
    console.log(`Results: ${summary.successful}/${summary.total} successful, ${summary.jsonResponses} JSON responses`);

    return res.status(200).json({
      success: true,
      summary,
      results,
      recommendations: [
        summary.jsonResponses > 0 ? '✅ Found working authentication method!' : null,
        summary.unauthorized > 0 ? '🔐 Endpoint requires proper authentication' : null,
        summary.badRequest === summary.total ? '⚠️ All methods return 400 - likely needs real session' : null,
        '💡 Try inspecting browser Network tab during manual booking to capture real headers/cookies'
      ].filter(Boolean),
      conclusion: summary.jsonResponses > 0 ? 
        '✅ Found working authentication approach!' :
        summary.unauthorized > 0 ?
        '🔐 Authentication required - need real session cookies' :
        '⚠️ All methods blocked - endpoint heavily protected',
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Authentication method test failed:', error.message);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
} 