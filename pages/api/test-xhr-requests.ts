import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const testResults: any = {
    timestamp: new Date().toISOString(),
    results: [],
    promising: [],
    summary: {}
  };

  const headers = {
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
  };

  // Test different payload strategies to bypass SSN requirement
  const testStrategies = [
    {
      name: "No SSN - Minimum Required",
      payload: {
        bookingSession: {
          licenceId: 5,
          bookingModeId: 0,
          ignoreDebt: false
        },
        occasionBundleQuery: {
          startDate: new Date().toISOString(),
          searchedMonths: 6,
          locationId: 1000132
        }
      }
    },
    {
      name: "Empty SSN",
      payload: {
        bookingSession: {
          socialSecurityNumber: "",
          licenceId: 5,
          bookingModeId: 0,
          ignoreDebt: false
        },
        occasionBundleQuery: {
          startDate: new Date().toISOString(),
          searchedMonths: 6,
          locationId: 1000132
        }
      }
    },
    {
      name: "Test SSN Pattern",
      payload: {
        bookingSession: {
          socialSecurityNumber: "19900101-0000",
          licenceId: 5,
          bookingModeId: 0,
          ignoreDebt: false
        },
        occasionBundleQuery: {
          startDate: new Date().toISOString(),
          searchedMonths: 6,
          locationId: 1000132
        }
      }
    },
    {
      name: "Södertälje Location",
      payload: {
        bookingSession: {
          licenceId: 5,
          bookingModeId: 0,
          ignoreDebt: false
        },
        occasionBundleQuery: {
          startDate: new Date().toISOString(),
          searchedMonths: 6,
          locationId: 1000133
        }
      }
    },
    {
      name: "Multiple Locations Array",
      payload: {
        bookingSession: {
          licenceId: 5,
          bookingModeId: 0,
          ignoreDebt: false
        },
        occasionBundleQuery: {
          startDate: new Date().toISOString(),
          searchedMonths: 6,
          locationIds: [1000132, 1000133]
        }
      }
    }
  ];

  const url = 'https://fp.trafikverket.se/Boka/occasion-bundles';

  for (const strategy of testStrategies) {
    const result: any = {
      strategy: strategy.name,
      url: url,
      success: false,
      status: null,
      error: null,
      responseSize: 0,
      containsSlotData: false,
      containsLocationData: false,
      slotsFound: 0,
      responsePreview: null
    };

    try {
      console.log(`Testing strategy: ${strategy.name}`);
      
      const response = await axios.post(url, strategy.payload, {
        headers,
        timeout: 15000
      });

      result.success = true;
      result.status = response.status;
      result.responseSize = JSON.stringify(response.data).length;

      if (response.data) {
        const dataStr = JSON.stringify(response.data).toLowerCase();
        
        // Check for slot-related data
        const slotKeywords = ['farsta', 'södertälje', 'sodertalje', 'occasion', 'date', 'time', 'available', 'september', 'oktober', '2025'];
        const foundSlotKeywords = slotKeywords.filter(keyword => dataStr.includes(keyword));
        
        result.containsSlotData = foundSlotKeywords.length > 0;
        result.containsLocationData = dataStr.includes('location') || dataStr.includes('plats');
        
        // Try to count potential slots
        if (Array.isArray(response.data)) {
          result.slotsFound = response.data.length;
        } else if (response.data.occasions && Array.isArray(response.data.occasions)) {
          result.slotsFound = response.data.occasions.length;
        } else if (response.data.bundles && Array.isArray(response.data.bundles)) {
          result.slotsFound = response.data.bundles.length;
        }

        result.dataAnalysis = {
          isArray: Array.isArray(response.data),
          hasSlotKeywords: foundSlotKeywords,
          topLevelKeys: typeof response.data === 'object' && response.data !== null ? Object.keys(response.data).slice(0, 10) : [],
          potentialSlotCount: result.slotsFound
        };

        // Store preview (first 1000 chars)
        result.responsePreview = JSON.stringify(response.data, null, 2).substring(0, 1000) + '...';

        if (result.containsSlotData || result.slotsFound > 0 || result.responseSize > 1000) {
          testResults.promising.push(result);
        }

        console.log(`✅ Strategy "${strategy.name}" worked! Size: ${result.responseSize}, Slots: ${result.slotsFound}`);
      }

    } catch (error: any) {
      result.success = false;
      result.status = error.response?.status || 'NETWORK_ERROR';
      result.error = error.message;
      
      if (error.response?.data) {
        result.errorResponse = JSON.stringify(error.response.data).substring(0, 500) + '...';
      }

      console.log(`❌ Strategy "${strategy.name}" failed: ${error.message}`);
    }

    testResults.results.push(result);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // Generate summary
  const successful = testResults.results.filter((r: any) => r.success);
  const withSlotData = testResults.results.filter((r: any) => r.containsSlotData);

  testResults.summary = {
    total: testResults.results.length,
    successful: successful.length,
    failed: testResults.results.length - successful.length,
    withSlotData: withSlotData.length,
    promising: testResults.promising.length,
    bestStrategy: testResults.promising.length > 0 ? testResults.promising[0].strategy : 'None worked'
  };

  res.status(200).json(testResults);
}
