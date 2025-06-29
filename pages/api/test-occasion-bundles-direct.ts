import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🎯 Direct test of /Boka/occasion-bundles endpoint...');

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

    const payload = {
      bookingSession: {
        socialSecurityNumber: '', // Empty - no auth
        licenceId: 5, // B license
        bookingModeId: 0
      },
      occasionBundleQuery: {
        startDate: '2024-12-20',
        endDate: '2025-01-15',
        locationId: null, // Search all locations
        examinationTypeId: 5, // B license
        tachographTypeId: 1,
        occasionChoiceId: 1,
        searchedMonths: 0
      }
    };

    console.log('📤 Sending payload:', JSON.stringify(payload, null, 2));

    let response;
    let error = null;
    let responseAnalysis: any = {};

    try {
      response = await httpClient.post('/Boka/occasion-bundles', payload);
      
      console.log('✅ Request successful!');
      console.log('📊 Status:', response.status);
      console.log('📊 Headers:', JSON.stringify(response.headers, null, 2));
      
      // Analyze response
      const responseText = JSON.stringify(response.data);
      const isHtml = responseText.includes('<!doctype html>') || responseText.includes('<html');
      const isJson = typeof response.data === 'object' && response.data !== null;
      const responseSize = responseText.length;
      
      responseAnalysis = {
        isHtml,
        isJson,
        responseSize,
        responseType: typeof response.data,
        hasOccasions: isJson && (response.data.occasions || response.data.occasionBundles || response.data.results),
        topLevelKeys: isJson ? Object.keys(response.data) : [],
        responsePreview: responseText.substring(0, 500) + (responseText.length > 500 ? '...' : '')
      };
      
      console.log('📊 Response Analysis:', responseAnalysis);
      
    } catch (err: any) {
      error = err;
      console.log('❌ Request failed');
      console.log('📊 Error status:', err.response?.status);
      console.log('📊 Error message:', err.message);
      console.log('📊 Error data:', err.response?.data);
      
      // Analyze error response for 400 Bad Request
      if (err.response?.status === 400) {
        console.log('='.repeat(50));
        console.log('🔍 400 BAD REQUEST - SERVER ERROR RESPONSE:');
        console.log('='.repeat(50));
        console.log('📊 Response data type:', typeof err.response.data);
        
        if (err.response.data) {
          console.log('🚨 SERVER ERROR RESPONSE (this tells us what to fix):');
          console.log(JSON.stringify(err.response.data, null, 2));
          
          const errorData = err.response.data;
          if (typeof errorData === 'string') {
            console.log('📊 Server error string:', errorData);
          } else if (typeof errorData === 'object') {
            console.log('📊 Server error object keys:', Object.keys(errorData));
            if (errorData.message) console.log('🎯 Server message:', errorData.message);
            if (errorData.error) console.log('🎯 Server error:', errorData.error);
            if (errorData.errors) console.log('🎯 Server validation errors:', errorData.errors);
            if (errorData.details) console.log('🎯 Server error details:', errorData.details);
            if (errorData.title) console.log('🎯 Server error title:', errorData.title);
            if (errorData.type) console.log('🎯 Server error type:', errorData.type);
          }
        } else {
          console.log('⚠️ No error response data from server');
        }
        console.log('='.repeat(50));
      }
      
      // Check if it's an authentication error (expected)
      if (err.response?.status === 401 || err.response?.status === 403) {
        console.log('ℹ️ Authentication required (this is expected without proper session)');
      }
    }

    const result = {
      success: !error,
      endpoint: '/Boka/occasion-bundles',
      status: response?.status || error?.response?.status,
      error: error ? {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        hasResponseData: !!error.response?.data,
        responseData: error.response?.data,
        is400BadRequest: error.response?.status === 400
      } : null,
      responseAnalysis,
      payload,
      timestamp: new Date().toISOString(),
      conclusion: error ? 
        (error.response?.status === 401 || error.response?.status === 403 ? 
          '🔐 Endpoint exists but requires authentication (Bank ID)' :
          error.response?.status === 400 ?
          '🔧 Endpoint exists but payload format is wrong (400 Bad Request)' :
          '❌ Endpoint not accessible') :
        (responseAnalysis.isHtml ? 
          '❌ Endpoint returns HTML (redirect)' :
          '✅ Endpoint returns JSON data')
    };

    console.log('🎯 Final result:', result.conclusion);
    return res.status(200).json(result);

  } catch (error: any) {
    console.error('❌ Test failed:', error.message);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
} 