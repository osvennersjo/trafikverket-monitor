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
    'Cache-Control': 'no-cache'
  };

  // All XHR endpoints from the user's Network tab
  const xhrEndpoints = [
    {
      name: "is-system-updating",
      url: "https://fp.trafikverket.se/boka/ng/api/is-system-updating",
      method: "GET",
      expectedSize: "2.0 kB"
    },
    {
      name: "start", 
      url: "https://fp.trafikverket.se/boka/ng/api/start",
      method: "GET",
      expectedSize: "2.3 kB"
    },
    {
      name: "getLanguageSupport",
      url: "https://fp.trafikverket.se/boka/ng/api/getLanguageSupport", 
      method: "GET",
      expectedSize: "102 kB"
    },
    {
      name: "is-authorized",
      url: "https://fp.trafikverket.se/boka/ng/api/is-authorized",
      method: "GET", 
      expectedSize: "2.0 kB"
    },
    {
      name: "get-navigation-model",
      url: "https://fp.trafikverket.se/boka/ng/api/get-navigation-model",
      method: "GET",
      expectedSize: "202 kB"
    },
    {
      name: "get-suggested-reservations-by-licence-and-ssn",
      url: "https://fp.trafikverket.se/boka/ng/api/get-suggested-reservations-by-licence-and-ssn",
      method: "GET",
      expectedSize: "2.3 kB"
    },
    {
      name: "information",
      url: "https://fp.trafikverket.se/boka/ng/api/information", 
      method: "GET",
      expectedSize: "3.5 kB"
    },
    {
      name: "search-information", 
      url: "https://fp.trafikverket.se/boka/ng/api/search-information",
      method: "GET",
      expectedSize: "46.7 kB",
      priority: "HIGH"
    },
    {
      name: "getCookie",
      url: "https://fp.trafikverket.se/boka/ng/api/getCookie",
      method: "GET", 
      expectedSize: "2.0 kB"
    },
    {
      name: "get-active-reservations",
      url: "https://fp.trafikverket.se/boka/ng/api/get-active-reservations",
      method: "GET",
      expectedSize: "2.1 kB",
      priority: "HIGH"
    }
  ];

  for (const endpoint of xhrEndpoints) {
    const result: any = {
      name: endpoint.name,
      url: endpoint.url,
      method: endpoint.method,
      expectedSize: endpoint.expectedSize,
      priority: endpoint.priority || "NORMAL",
      success: false,
      status: null,
      error: null,
      responseSize: 0,
      responseSizeKB: "0 kB",
      containsSlotData: false,
      containsLocationData: false,
      responsePreview: null,
      dataAnalysis: {}
    };

    try {
      console.log(`Testing ${endpoint.name} (expected: ${endpoint.expectedSize})...`);
      
      let response;
      
      if (endpoint.method === 'GET') {
        response = await axios.get(endpoint.url, {
          headers,
          timeout: 15000
        });
      } else {
        response = await axios.post(endpoint.url, {}, {
          headers: { ...headers, 'Content-Type': 'application/json' },
          timeout: 15000
        });
      }

      result.success = true;
      result.status = response.status;
      result.responseSize = JSON.stringify(response.data).length;
      result.responseSizeKB = (result.responseSize / 1024).toFixed(1) + " kB";

      if (response.data) {
        const dataStr = JSON.stringify(response.data).toLowerCase();
        
        // Check for slot-related keywords
        const slotKeywords = ['farsta', 'södertälje', 'sodertalje', 'occasion', 'slot', 'date', 'time', 'available', 'book', 'test', 'exam', 'körkort', 'körprov', 'september', 'oktober', '2025', 'bundle'];
        const foundSlotKeywords = slotKeywords.filter(keyword => dataStr.includes(keyword));
        
        // Check for location keywords  
        const locationKeywords = ['location', 'plats', 'ort', 'stad', 'city'];
        const foundLocationKeywords = locationKeywords.filter(keyword => dataStr.includes(keyword));

        result.containsSlotData = foundSlotKeywords.length > 0;
        result.containsLocationData = foundLocationKeywords.length > 0;
        
        result.dataAnalysis = {
          isArray: Array.isArray(response.data),
          isObject: typeof response.data === 'object',
          hasSlotKeywords: foundSlotKeywords,
          hasLocationKeywords: foundLocationKeywords,
          keywordCount: foundSlotKeywords.length + foundLocationKeywords.length,
          topLevelKeys: typeof response.data === 'object' && response.data !== null ? Object.keys(response.data).slice(0, 10) : []
        };

        // Store preview (first 800 chars)
        result.responsePreview = JSON.stringify(response.data, null, 2).substring(0, 800) + (result.responseSize > 800 ? '...' : '');

        // Mark as promising based on multiple criteria
        const isPromising = result.containsSlotData || 
                           result.containsLocationData || 
                           result.responseSize > 5000 ||
                           endpoint.priority === "HIGH" ||
                           foundSlotKeywords.length > 2;

        if (isPromising) {
          testResults.promising.push(result);
        }

        console.log(`✅ ${endpoint.name}: ${result.responseSizeKB}, Keywords: ${foundSlotKeywords.length}, Promising: ${isPromising}`);
      }

    } catch (error: any) {
      result.success = false;
      result.status = error.response?.status || 'NETWORK_ERROR';
      result.error = error.message;
      
      if (error.response?.data) {
        result.errorResponse = JSON.stringify(error.response.data).substring(0, 300) + '...';
      }

      console.log(`❌ ${endpoint.name}: ${error.message} (${result.status})`);
    }

    testResults.results.push(result);
    
    // Small delay between requests
    await new Promise(resolve => setTimeout(resolve, 300));
  }

  // Generate summary
  const successful = testResults.results.filter((r: any) => r.success);
  const withSlotData = testResults.results.filter((r: any) => r.containsSlotData);
  const withLocationData = testResults.results.filter((r: any) => r.containsLocationData);
  const highPriority = testResults.results.filter((r: any) => r.priority === "HIGH");

  testResults.summary = {
    total: testResults.results.length,
    successful: successful.length,
    failed: testResults.results.length - successful.length,
    withSlotData: withSlotData.length,
    withLocationData: withLocationData.length,
    promising: testResults.promising.length,
    highPriorityTested: highPriority.length,
    bestEndpoint: testResults.promising.length > 0 ? testResults.promising[0].name : 'None found'
  };

  res.status(200).json(testResults);
}
