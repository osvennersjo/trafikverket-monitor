import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🧪 Testing different payload variations...');

    const httpClient = axios.create({
      baseURL: 'https://fp.trafikverket.se',
      timeout: 5000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Referer': 'https://fp.trafikverket.se/',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
      }
    });

    // Test different payload variations
    const payloadVariations = [
      {
        name: 'Original payload',
        payload: {
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
        }
      },
      {
        name: 'With test SSN format',
        payload: {
          bookingSession: {
            socialSecurityNumber: '199001011234', // Test format (fake)
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
        }
      },
      {
        name: 'Minimal payload',
        payload: {
          bookingSession: {
            socialSecurityNumber: '',
            licenceId: 5
          },
          occasionBundleQuery: {
            startDate: '2024-12-20',
            endDate: '2025-01-15'
          }
        }
      },
      {
        name: 'Different date format',
        payload: {
          bookingSession: {
            socialSecurityNumber: '',
            licenceId: 5,
            bookingModeId: 0
          },
          occasionBundleQuery: {
            startDate: '2024-12-20T00:00:00',
            endDate: '2025-01-15T23:59:59',
            locationId: null,
            examinationTypeId: 5,
            tachographTypeId: 1,
            occasionChoiceId: 1,
            searchedMonths: 0
          }
        }
      },
      {
        name: 'With locationId specified',
        payload: {
          bookingSession: {
            socialSecurityNumber: '',
            licenceId: 5,
            bookingModeId: 0
          },
          occasionBundleQuery: {
            startDate: '2024-12-20',
            endDate: '2025-01-15',
            locationId: 1, // Try with a location ID instead of null
            examinationTypeId: 5,
            tachographTypeId: 1,
            occasionChoiceId: 1,
            searchedMonths: 0
          }
        }
      }
    ];

    const results = [];

    for (const variation of payloadVariations) {
      try {
        console.log(`🧪 Testing: ${variation.name}`);
        const response = await httpClient.post('/Boka/occasion-bundles', variation.payload);
        
        results.push({
          name: variation.name,
          success: true,
          status: response.status,
          responseType: typeof response.data,
          hasData: !!response.data,
          message: '✅ Success!'
        });
        
      } catch (error: any) {
        const status = error.response?.status;
        const responseData = error.response?.data;
        
        results.push({
          name: variation.name,
          success: false,
          status: status,
          responseData: responseData,
          message: status === 400 ? '❌ Bad Request' : 
                  status === 401 ? '🔐 Unauthorized' :
                  status === 403 ? '🔐 Forbidden' :
                  `❌ Error ${status}`
        });
        
        console.log(`❌ ${variation.name}: ${status} - ${responseData}`);
      }
      
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    const summary = {
      total: results.length,
      successful: results.filter(r => r.success).length,
      badRequest: results.filter(r => r.status === 400).length,
      unauthorized: results.filter(r => r.status === 401 || r.status === 403).length,
      results: results
    };

    console.log('📊 Payload variation test completed');
    console.log(`Results: ${summary.successful}/${summary.total} successful`);

    return res.status(200).json({
      success: true,
      summary,
      results,
      conclusion: summary.successful > 0 ? 
        '✅ Found working payload format!' :
        summary.unauthorized > 0 ?
        '🔐 All variations require authentication' :
        '❌ All variations return Bad Request - likely needs session/auth',
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Payload variation test failed:', error.message);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
} 