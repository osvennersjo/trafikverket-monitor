import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('⚡ Quick time manipulation test...');

    // Base cookies from successful test
    const baseCookies = 'FpsPartnerDeviceIdentifier=3A9A20D3DFD8E7E8348165854B94CD43E2D822F4026DEDD3407F014780642DD771360F659AED5CDF95DED2B5A9A7B9066F0455B5D57AD5DACC2584AB51B138600EE895AB16EB15C674C086C328E7947F3B19D3CB1CCD7E92BC4259CE1E0426A81A437032B1C30DE5A2DE152FF33AC0B19F3C011D1999C6C1270FC96C7DD95E1F37E788036DB7DC471D2D7EE1E640A4E20018ABE755C85D304A3CDDD11F3B8883; ASP.NET_SessionId=mdv2vyjiglhod4ltaypemhur; TrvCookieConsent=functional%3Dfalse%26analytical%3Dfalse; NSC_mc-gpsbsqspw-fyu-xfc-iuuq-wt=ffffffff0914196145525d5f4f58455e445a4a423660; FpsExternalIdentity=7B923F9FFB5157E254F4B6D446B98030094EA5AEE79B967ECDA78DF72C832944875DB730D5111DEDBE4CB8C3806B7AB4CCD84B3CCC15F1C6719B77ADDA4751DAFA4E28281607AA4276EF3F7BBCD947A7CDCCFD9DE65A1D2057498F0B0A1120A7553AE5050735C9376F5E8411EEEF394419F0B8390FF435B70D052B46F49F3787BD40B0F9226136F9816E561A40EC6A42B30C2890D1469AD5EB007D46C7E547CE4334FEA2ACC3D86A104651B07BF6053DBC8F3C6DF1FEB9C7F33DB2040339288EF076962DF923C1272B8BD6D530637FC14F16C147BA5FAC40381F484DDDA4096C7F7653FB0731C3445BCA583F6A5DF9248AF0DBFD01A0C032C02CE7F952684AC3D2E264198F030DC90F7EDF2DB5DB73A0E8F23529C3F65D42BAC8E975C5DAF86E59FFDFD2E65EB58FA90D7501AC5DC213B38603D249CBA49384D4F5F1C70A7D067F80AA0279892A3F0BA41085E05AF1E01BB5BE7F9B0D3DC2A79E814979689152405CD1C42E8F34CD4EF2DB96423A7225B541585D3AF736CD67E3BA2372DF73C15B74A395ED1E1C4DB79BD15DF41F21E0DC5E62DAA8456E014ED8571A9F7C85139055FC1A69B838B2389DD9D9D637E9EB';

    // Test just 2 variations to stay under timeout
    const now = new Date();
    const timeTests = [
      {
        name: 'Original (2025-06-30 00:21)',
        loginValid: '2025-06-30 00:21'
      },
      {
        name: 'Extended +3 hours',
        loginValid: new Date(now.getTime() + 3 * 60 * 60 * 1000).toISOString().slice(0, 16).replace('T', ' ')
      }
    ];

    // Lightweight payload - just test authentication, not full data
    const quickPayload = {
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
        "locationId": 1000132, // Just Södertälje for speed
        "languageId": 13,
        "vehicleTypeId": 2,
        "tachographTypeId": 1,
        "occasionChoiceId": 1,
        "examinationTypeId": 12
      }
    };

    const results = [];
    const startTime = Date.now();

    for (const test of timeTests) {
      const testStart = Date.now();
      
      try {
        const cookiesWithTime = `${baseCookies}; LoginValid=${encodeURIComponent(test.loginValid)}`;
        
        console.log(`⚡ Testing: ${test.name}`);
        
        const response = await axios.post('https://fp.trafikverket.se/Boka/occasion-bundles', quickPayload, {
          timeout: 4000, // 4 second timeout per request
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
        
        // Quick response analysis
        const responseSize = JSON.stringify(response.data).length;
        const hasData = response.data && response.data.data && response.data.data.bundles;
        const occasionCount = hasData ? 
          response.data.data.bundles.reduce((sum: number, bundle: any) => 
            sum + (bundle.occasions ? bundle.occasions.length : 0), 0) : 0;

        const testDuration = Date.now() - testStart;
        
        results.push({
          name: test.name,
          loginValid: test.loginValid,
          success: true,
          status: response.status,
          responseSize,
          occasionCount,
          duration: testDuration,
          message: `✅ SUCCESS! ${occasionCount} occasions found`,
          timeWorked: true
        });
        
        console.log(`✅ ${test.name}: ${occasionCount} occasions in ${testDuration}ms`);

      } catch (error: any) {
        const testDuration = Date.now() - testStart;
        const status = error.response?.status;
        
        results.push({
          name: test.name,
          loginValid: test.loginValid,
          success: false,
          status: status,
          duration: testDuration,
          message: status === 401 ? '🔐 Session expired/invalid' : 
                  status === 400 ? '❌ Bad Request' :
                  `❌ Error ${status}`,
          timeWorked: false
        });
        
        console.log(`❌ ${test.name}: Failed with ${status} in ${testDuration}ms`);
      }
    }

    const totalDuration = Date.now() - startTime;

    const summary = {
      total: results.length,
      successful: results.filter(r => r.success).length,
      timeManipulationWorks: results.filter(r => r.success && r.name.includes('Extended')).length > 0,
      totalDuration,
      averageDuration: Math.round(totalDuration / results.length)
    };

    const conclusion = summary.timeManipulationWorks ? 
      '🎉 TIME MANIPULATION WORKS! Session can be extended!' :
      summary.successful > 0 ?
      '⚠️ Only original time works - manipulation blocked' :
      '❌ All tests failed - session issues';

    console.log(`⚡ Quick time test completed in ${totalDuration}ms`);
    console.log(`Results: ${summary.successful}/${summary.total} successful`);

    return res.status(200).json({
      success: true,
      summary,
      results,
      conclusion,
      recommendations: summary.timeManipulationWorks ? [
        '🎉 Implement automatic time extension in monitor',
        '⏰ Extend LoginValid before each API call',
        '🚀 Start continuous monitoring with auto-session-refresh'
      ] : [
        '🔄 Need periodic session refresh from browser',
        '💡 Implement session refresh mechanism',
        '🎯 Monitor with current session while it lasts'
      ],
      performance: {
        totalTime: `${totalDuration}ms`,
        avgPerTest: `${summary.averageDuration}ms`,
        stayedUnderTimeout: totalDuration < 8000
      },
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Quick time test failed:', error.message);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
} 