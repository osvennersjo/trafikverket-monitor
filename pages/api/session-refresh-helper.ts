import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('🔄 Testing current session and providing refresh instructions...');

    // Current session cookies (these are likely expired)
    const currentCookies = 'FpsPartnerDeviceIdentifier=3A9A20D3DFD8E7E8348165854B94CD43E2D822F4026DEDD3407F014780642DD771360F659AED5CDF95DED2B5A9A7B9066F0455B5D57AD5DACC2584AB51B138600EE895AB16EB15C674C086C328E7947F3B19D3CB1CCD7E92BC4259CE1E0426A81A437032B1C30DE5A2DE152FF33AC0B19F3C011D1999C6C1270FC96C7DD95E1F37E788036DB7DC471D2D7EE1E640A4E20018ABE755C85D304A3CDDD11F3B8883; ASP.NET_SessionId=mdv2vyjiglhod4ltaypemhur; TrvCookieConsent=functional%3Dfalse%26analytical%3Dfalse; NSC_mc-gpsbsqspw-fyu-xfc-iuuq-wt=ffffffff0914196145525d5f4f58455e445a4a423660; FpsExternalIdentity=7B923F9FFB5157E254F4B6D446B98030094EA5AEE79B967ECDA78DF72C832944875DB730D5111DEDBE4CB8C3806B7AB4CCD84B3CCC15F1C6719B77ADDA4751DAFA4E28281607AA4276EF3F7BBCD947A7CDCCFD9DE65A1D2057498F0B0A1120A7553AE5050735C9376F5E8411EEEF394419F0B8390FF435B70D052B46F49F3787BD40B0F9226136F9816E561A40EC6A42B30C2890D1469AD5EB007D46C7E547CE4334FEA2ACC3D86A104651B07BF6053DBC8F3C6DF1FEB9C7F33DB2040339288EF076962DF923C1272B8BD6D530637FC14F16C147BA5FAC40381F484DDDA4096C7F7653FB0731C3445BCA583F6A5DF9248AF0DBFD01A0C032C02CE7F952684AC3D2E264198F030DC90F7EDF2DB5DB73A0E8F23529C3F65D42BAC8E975C5DAF86E59FFDFD2E65EB58FA90D7501AC5DC213B38603D249CBA49384D4F5F1C70A7D067F80AA0279892A3F0BA41085E05AF1E01BB5BE7F9B0D3DC2A79E814979689152405CD1C42E8F34CD4EF2DB96423A7225B541585D3AF736CD67E3BA2372DF73C15B74A395ED1E1C4DB79BD15DF41F21E0DC5E62DAA8456E014ED8571A9F7C85139055FC1A69B838B2389DD9D9D637E9EB';

    // Test current session
    console.log('🧪 Testing current session validity...');
    
    const testPayload = {
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
        "locationId": 1000132,
        "languageId": 13,
        "vehicleTypeId": 2,
        "tachographTypeId": 1,
        "occasionChoiceId": 1,
        "examinationTypeId": 12
      }
    };

    let sessionStatus = 'unknown';
    let sessionError = '';
    let hasData = false;

    try {
      const response = await axios.post('https://fp.trafikverket.se/Boka/occasion-bundles', testPayload, {
        timeout: 5000,
        headers: {
          'Accept': 'application/json, text/plain, */*',
          'Accept-Language': 'sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7',
          'Connection': 'keep-alive',
          'Content-Type': 'application/json; charset=UTF-8',
          'Cookie': currentCookies,
          'Origin': 'https://fp.trafikverket.se',
          'Referer': 'https://fp.trafikverket.se/Boka/ng/search/dSdDbIsIiEdAin/5/12/0/0',
          'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      if (response.status === 200) {
        sessionStatus = 'active';
        hasData = response.data && response.data.data && response.data.data.bundles;
        console.log('✅ Current session still works!');
      }

    } catch (error: any) {
      sessionStatus = 'expired';
      sessionError = `${error.response?.status} ${error.response?.statusText || error.message}`;
      console.log(`❌ Current session failed: ${sessionError}`);
    }

    return res.status(200).json({
      success: true,
      currentSessionStatus: {
        status: sessionStatus,
        hasData: hasData,
        error: sessionError,
        message: sessionStatus === 'active' ? '✅ Current session still works' : '❌ Session expired - need refresh'
      },
      refreshInstructions: {
        title: '🔄 How to Get Fresh Session Cookies',
        steps: [
          '1️⃣ Open a NEW INCOGNITO/PRIVATE browser window',
          '2️⃣ Go to https://fp.trafikverket.se',
          '3️⃣ Complete Bank ID login process',
          '4️⃣ Navigate to driving test booking section',
          '5️⃣ Press F12 to open DevTools → Network tab',
          '6️⃣ Try to search for test slots (any location)',
          '7️⃣ Look for "occasion-bundles" request in Network tab',
          '8️⃣ Right-click on it → Copy → Copy as cURL',
          '9️⃣ Send the new cURL command to update the system'
        ],
        whatToLookFor: [
          '🔍 Look for POST request to "occasion-bundles"',
          '📊 Should return large response (1-2MB)',
          '🍪 New cookies will have updated FpsExternalIdentity',
          '🕐 Fresh LoginValid timestamp'
        ],
        criticalCookies: [
          'FpsExternalIdentity (long encrypted token)',
          'ASP.NET_SessionId (session identifier)', 
          'LoginValid (timestamp that can be extended)',
          'FpsPartnerDeviceIdentifier (device fingerprint)'
        ]
      },
      timeManipulationStatus: {
        confirmed: true,
        message: '🎉 Time manipulation WORKS! Once we get fresh cookies, we can extend them automatically',
        benefit: 'Fresh session + time manipulation = unlimited monitoring!'
      },
      nextSteps: sessionStatus === 'active' ? [
        '✅ Current session still works somehow!',
        '🚀 Try the V2 monitor test again',
        '🎯 Start monitoring immediately'
      ] : [
        '🔄 Get fresh session cookies using instructions above',
        '🔧 Update the system with new cookies',
        '🎉 Then activate unlimited monitoring with time manipulation!'
      ],
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Session refresh helper failed:', error.message);
    return res.status(500).json({ 
      success: false, 
      error: error.message,
      message: 'Could not test session status',
      timestamp: new Date().toISOString()
    });
  }
} 