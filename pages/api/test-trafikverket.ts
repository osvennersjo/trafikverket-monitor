import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const testResults: any = {
    timestamp: new Date().toISOString(),
    tests: []
  };

  // Create HTTP client like the monitor does
  const httpClient = axios.create({
    baseURL: 'https://fp.trafikverket.se',
    timeout: 15000,
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
      'Cache-Control': 'no-cache'
    }
  });

  // Test endpoints one by one
  const endpointsToTest = [
    { path: '/boka/api/2.0/examinationTypes', method: 'GET' },
    { path: '/boka/api/2.0/locations', method: 'GET' },
    { path: '/boka/api/2.0/occasions', method: 'POST' },
    { path: '/boka/api/examinationTypes', method: 'GET' },
    { path: '/boka/api/locations', method: 'GET' },
    { path: '/boka/api/occasions', method: 'POST' },
  ];

  for (const endpoint of endpointsToTest) {
    const testResult: any = {
      endpoint: endpoint.path,
      method: endpoint.method,
      success: false,
      status: null,
      error: null,
      responseSize: 0,
      hasData: false
    };

    try {
      let response;
      
      if (endpoint.method === 'GET') {
        response = await httpClient.get(endpoint.path);
      } else {
        // For POST, try with minimal valid data
        response = await httpClient.post(endpoint.path, {
          licenceCategoryId: "5",
          examTypeId: "5",
          fromDate: new Date().toISOString().split('T')[0],
          toDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        });
      }

      testResult.success = true;
      testResult.status = response.status;
      testResult.responseSize = JSON.stringify(response.data).length;
      testResult.hasData = !!response.data;
      
      // Sample of response (first 200 chars for debugging)
      if (response.data) {
        testResult.dataSample = JSON.stringify(response.data).substring(0, 200) + '...';
      }

    } catch (error: any) {
      testResult.success = false;
      testResult.status = error.response?.status || 'NETWORK_ERROR';
      testResult.error = error.message;
      
      if (error.response?.data) {
        testResult.errorResponse = JSON.stringify(error.response.data).substring(0, 200) + '...';
      }
    }

    testResults.tests.push(testResult);
  }

  // Summary
  const successfulTests = testResults.tests.filter((t: any) => t.success);
  testResults.summary = {
    total: testResults.tests.length,
    successful: successfulTests.length,
    failed: testResults.tests.length - successfulTests.length
  };

  res.status(200).json(testResults);
} 