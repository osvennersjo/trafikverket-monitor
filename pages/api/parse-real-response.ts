import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🎯 Testing response parsing and time manipulation...');

    // Base cookies from successful test
    const baseCookies = 'FpsPartnerDeviceIdentifier=3A9A20D3DFD8E7E8348165854B94CD43E2D822F4026DEDD3407F014780642DD771360F659AED5CDF95DED2B5A9A7B9066F0455B5D57AD5DACC2584AB51B138600EE895AB16EB15C674C086C328E7947F3B19D3CB1CCD7E92BC4259CE1E0426A81A437032B1C30DE5A2DE152FF33AC0B19F3C011D1999C6C1270FC96C7DD95E1F37E788036DB7DC471D2D7EE1E640A4E20018ABE755C85D304A3CDDD11F3B8883; ASP.NET_SessionId=mdv2vyjiglhod4ltaypemhur; TrvCookieConsent=functional%3Dfalse%26analytical%3Dfalse; NSC_mc-gpsbsqspw-fyu-xfc-iuuq-wt=ffffffff0914196145525d5f4f58455e445a4a423660; FpsExternalIdentity=7B923F9FFB5157E254F4B6D446B98030094EA5AEE79B967ECDA78DF72C832944875DB730D5111DEDBE4CB8C3806B7AB4CCD84B3CCC15F1C6719B77ADDA4751DAFA4E28281607AA4276EF3F7BBCD947A7CDCCFD9DE65A1D2057498F0B0A1120A7553AE5050735C9376F5E8411EEEF394419F0B8390FF435B70D052B46F49F3787BD40B0F9226136F9816E561A40EC6A42B30C2890D1469AD5EB007D46C7E547CE4334FEA2ACC3D86A104651B07BF6053DBC8F3C6DF1FEB9C7F33DB2040339288EF076962DF923C1272B8BD6D530637FC14F16C147BA5FAC40381F484DDDA4096C7F7653FB0731C3445BCA583F6A5DF9248AF0DBFD01A0C032C02CE7F952684AC3D2E264198F030DC90F7EDF2DB5DB73A0E8F23529C3F65D42BAC8E975C5DAF86E59FFDFD2E65EB58FA90D7501AC5DC213B38603D249CBA49384D4F5F1C70A7D067F80AA0279892A3F0BA41085E05AF1E01BB5BE7F9B0D3DC2A79E814979689152405CD1C42E8F34CD4EF2DB96423A7225B541585D3AF736CD67E3BA2372DF73C15B74A395ED1E1C4DB79BD15DF41F21E0DC5E62DAA8456E014ED8571A9F7C85139055FC1A69B838B2389DD9D9D637E9EB';

    // Test different LoginValid times
    const now = new Date();
    const timeVariations = [
      {
        name: 'Original time (2025-06-30 00:21)',
        loginValid: '2025-06-30 00:21'
      },
      {
        name: 'Extended +1 hour',
        loginValid: new Date(now.getTime() + 60 * 60 * 1000).toISOString().slice(0, 16).replace('T', ' ')
      },
      {
        name: 'Extended +1 day', 
        loginValid: new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString().slice(0, 16).replace('T', ' ')
      },
      {
        name: 'Extended +1 week',
        loginValid: new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16).replace('T', ' ')
      }
    ];

    const workingPayload = {
      "bookingSession": {
        "socialSecurityNumber": "20061211-0718",
        "licenceId": 5,
        "bookingModeId": 0,
        "ignoreDebt": false,
        "ignoreBookingHindrance": false,
        "examinationTypeId": 12,
        "excludeExaminationCategories": [],
        "rescheduleTypeId": 0,
        "paymentIsActive": false,
        "paymentReference": "",
        "paymentUrl": "",
        "searchedMonths": 0
      },
      "occasionBundleQuery": {
        "startDate": "2024-12-20T00:00:00.000Z",
        "searchedMonths": 0,
        "locationId": 1000132, // Södertälje - our target location
        "nearbyLocationIds": [1000019], // Keep the nearby one that gave us data
        "languageId": 13,
        "vehicleTypeId": 2,
        "tachographTypeId": 1,
        "occasionChoiceId": 1,
        "examinationTypeId": 12
      }
    };

    const results = [];

    for (const timeVar of timeVariations) {
      try {
        const cookiesWithTime = `${baseCookies}; LoginValid=${encodeURIComponent(timeVar.loginValid)}`;
        
        console.log(`🕐 Testing: ${timeVar.name}`);
        
        const httpClient = axios.create({
          baseURL: 'https://fp.trafikverket.se',
          timeout: 10000,
          headers: {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': cookiesWithTime,
            'Origin': 'https://fp.trafikverket.se',
            'Referer': 'https://fp.trafikverket.se/Boka/ng/search/dSdDbIsIiEdAin/5/12/0/0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
          }
        });

        const response = await httpClient.post('/Boka/occasion-bundles', workingPayload);
        
        // Parse the response data
        const responseData = response.data;
        let occasionInfo = {
          totalOccasions: 0,
          locations: new Set(),
          dates: new Set(),
          sodertaljeeSlots: 0,
          farstaSlots: 0,
          otherSlots: 0
        };

        // Parse occasions from the response
        if (responseData && responseData.data && responseData.data.bundles) {
          for (const bundle of responseData.data.bundles) {
            if (bundle.occasions) {
              occasionInfo.totalOccasions += bundle.occasions.length;
              
              for (const occasion of bundle.occasions) {
                // Track locations
                if (occasion.locationId) {
                  occasionInfo.locations.add(occasion.locationId);
                  
                  // Count by location
                  if (occasion.locationId === 1000132) {
                    occasionInfo.sodertaljeeSlots++;
                  } else if (occasion.locationId === 1000019) { // Check if this is Farsta
                    occasionInfo.farstaSlots++;
                  } else {
                    occasionInfo.otherSlots++;
                  }
                }
                
                // Track dates
                if (occasion.duration && occasion.duration.start) {
                  const date = occasion.duration.start.split('T')[0];
                  occasionInfo.dates.add(date);
                }
              }
            }
          }
        }

        results.push({
          name: timeVar.name,
          loginValid: timeVar.loginValid,
          success: true,
          status: response.status,
          responseSize: JSON.stringify(response.data).length,
          occasionInfo: {
            ...occasionInfo,
            locations: Array.from(occasionInfo.locations),
            dates: Array.from(occasionInfo.dates).sort()
          },
          message: `✅ Success! ${occasionInfo.totalOccasions} occasions, ${occasionInfo.sodertaljeeSlots} Södertälje slots`,
          timeWorked: true
        });
        
        console.log(`✅ ${timeVar.name}: ${occasionInfo.totalOccasions} occasions found`);

      } catch (error: any) {
        const status = error.response?.status;
        const responseData = error.response?.data;
        
        results.push({
          name: timeVar.name,
          loginValid: timeVar.loginValid,
          success: false,
          status: status,
          responseData: typeof responseData === 'string' ? responseData.substring(0, 200) : responseData,
          message: status === 401 ? '🔐 Session expired/invalid' : 
                  status === 400 ? '❌ Bad Request' :
                  `❌ Error ${status}`,
          timeWorked: false
        });
        
        console.log(`❌ ${timeVar.name}: Failed with ${status}`);
      }
      
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    const summary = {
      total: results.length,
      successful: results.filter(r => r.success).length,
      timeManipulationWorks: results.filter(r => r.success && r.name !== 'Original time (2025-06-30 00:21)').length > 0,
      totalOccasionsFound: results.filter(r => r.success).reduce((sum, r) => sum + (r.occasionInfo?.totalOccasions || 0), 0),
      sodertaljeSlotsFound: results.filter(r => r.success).reduce((sum, r) => sum + (r.occasionInfo?.sodertaljeeSlots || 0), 0)
    };

    const conclusion = summary.successful === 0 ? 
      '❌ All time variations failed - session might be tied to external factors' :
      summary.timeManipulationWorks ?
      '🎉 TIME MANIPULATION WORKS! We can extend session lifetime!' :
      '⚠️ Only original time works - time manipulation detected/blocked';

    console.log('🎯 Response parsing and time test completed');
    console.log(`Results: ${summary.successful}/${summary.total} successful`);
    console.log(`Time manipulation: ${summary.timeManipulationWorks ? 'WORKS' : 'BLOCKED'}`);

    return res.status(200).json({
      success: true,
      summary,
      results,
      conclusion,
      recommendations: summary.timeManipulationWorks ? [
        '🎉 Update monitoring system to extend LoginValid time automatically',
        '⏰ Set up time extension logic before each API call',
        '🚀 Start continuous monitoring with time manipulation'
      ] : [
        '🔄 Need to refresh session cookies periodically',
        '💡 Implement session refresh mechanism',
        '🎯 Focus on using current working session while it lasts'
      ],
      locationAnalysis: {
        locationIds: results.filter(r => r.success).map(r => r.occasionInfo?.locations).flat(),
        message: 'Location 1000019 gave us data - need to identify if this is Farsta or nearby Södertälje'
      },
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Response parsing test failed:', error.message);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
} 