import { useState, useEffect } from 'react';
import Head from 'next/head';
import { format, addDays } from 'date-fns';

interface MonitoringStatus {
  isActive: boolean;
  email: string;
  fromDate: string;
  toDate: string;
  sessionWorking?: boolean;
  occasionsFound?: number;
  checkInterval?: string;
  emailProvider?: string;
  locations?: string[];
  lastCheck?: string;
  slotsFound?: number;
}

export default function Home() {
  const [email, setEmail] = useState('');
  const [fromDate, setFromDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [toDate, setToDate] = useState(format(addDays(new Date(), 7), 'yyyy-MM-dd'));
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<MonitoringStatus | null>(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');

  const showMessage = (text: string, type: 'success' | 'error' | 'info') => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => setMessage(''), 5000);
  };

  const startLiveMonitoring = async () => {
    if (!email || !fromDate || !toDate) {
      showMessage('Please fill in all fields!', 'error');
      return;
    }

    if (new Date(fromDate) >= new Date(toDate)) {
      showMessage('From date must be before to date!', 'error');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/start-live-monitoring', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'start',
          email,
          fromDate,
          toDate,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showMessage('🚀 Live monitoring started! You will receive emails when slots become available.', 'success');
        setStatus(data.status);
      } else {
        if (data.error?.includes('Session test failed')) {
          showMessage('⚠️ Session expired - please get fresh cookies from browser and try again', 'info');
        } else {
          showMessage(data.error || 'Failed to start live monitoring', 'error');
        }
      }
    } catch (error) {
      showMessage('Network error. Please try again.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const stopMonitoring = async () => {
    try {
      const response = await fetch('/api/start-live-monitoring', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'stop'
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showMessage('🛑 Live monitoring stopped.', 'info');
        setStatus(null);
      } else {
        showMessage(data.error || 'Failed to stop monitoring', 'error');
      }
    } catch (error) {
      showMessage('Failed to stop monitoring', 'error');
    }
  };

  const checkStatus = async () => {
    try {
      const response = await fetch('/api/start-live-monitoring', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'status'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.status.isActive) {
          setStatus(data.status);
        } else {
          setStatus(null);
        }
      }
    } catch (error) {
      console.error('Failed to fetch status');
    }
  };

  const testEmail = async () => {
    if (!email || email.trim().length === 0) {
      showMessage('Please enter an email address first', 'error');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/test-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        showMessage(`✅ Test email sent to ${email}! Check your inbox.`, 'success');
      } else {
        showMessage(`❌ Test failed: ${data.details || data.error}`, 'error');
      }
    } catch (error) {
      showMessage('❌ Failed to send test email', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Head>
        <title>🚗 Trafikverket Monitor - Get that körkort!</title>
        <meta name="description" content="Monitor driving test availability in Södertälje and Farsta" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              🚗 Trafikverket Monitor
            </h1>
            <p className="text-gray-600 text-lg">
              Get notified when driving test slots open up in Södertälje or Farsta!
            </p>
          </div>

          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
            {/* Left Column - Form */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-6 text-gray-800">
                🎯 Live Monitoring System
              </h2>

              <div className="space-y-4">
                {/* Email Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    📧 Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Test Email Button */}
                <div>
                  <button
                    onClick={testEmail}
                    disabled={isLoading || !email}
                    className={`w-full font-medium py-2 px-4 rounded-md transition duration-200 flex items-center justify-center mb-4 ${
                      isLoading || !email 
                        ? 'bg-gray-400 cursor-not-allowed text-white' 
                        : 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                    }`}
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Testing...
                      </>
                    ) : (
                      '🧪 Test Email Configuration'
                    )}
                  </button>
                </div>

                {/* Date Range */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      📅 From Date
                    </label>
                    <input
                      type="date"
                      value={fromDate}
                      onChange={(e) => setFromDate(e.target.value)}
                      min={format(new Date(), 'yyyy-MM-dd')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      📅 To Date
                    </label>
                    <input
                      type="date"
                      value={toDate}
                      onChange={(e) => setToDate(e.target.value)}
                      min={fromDate}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Info Box */}
                <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                  <p className="text-sm text-blue-800">
                    📍 <strong>Monitoring:</strong> Södertälje & Farsta<br />
                    🚗 <strong>Test Type:</strong> Manual B License<br />
                    🔄 <strong>Check Interval:</strong> Every 5 minutes<br />
                    📧 <strong>Email:</strong> Powered by SendGrid ⚡<br />
                    ⏰ <strong>Features:</strong> 24/7 monitoring with automatic session extension
                  </p>
                </div>

                {/* Live Monitoring Buttons */}
                {!status?.isActive ? (
                  <button
                    onClick={startLiveMonitoring}
                    disabled={isLoading || !email}
                    className={`w-full font-semibold py-4 px-4 rounded-md transition duration-200 flex items-center justify-center text-lg ${
                      isLoading || !email
                        ? 'bg-gray-400 cursor-not-allowed text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white cursor-pointer'
                    }`}
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Starting Live Monitoring...
                      </>
                    ) : (
                      '🚀 START LIVE MONITORING'
                    )}
                  </button>
                ) : (
                  <button
                    onClick={stopMonitoring}
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-4 px-4 rounded-md transition duration-200 text-lg"
                  >
                    🛑 STOP MONITORING
                  </button>
                )}
              </div>

              {/* Live Status Display */}
              {status?.isActive && (
                <div className="mt-6 bg-green-50 border border-green-200 rounded-md p-4">
                  <h3 className="font-semibold text-green-800 mb-3 flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                    🚀 Live Monitoring Active
                  </h3>
                  <div className="text-sm text-green-700 space-y-2">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p><strong>📧 Email:</strong> {status.email}</p>
                        <p><strong>📅 Period:</strong> {status.fromDate} to {status.toDate}</p>
                        <p><strong>🎯 Slots Found:</strong> {status.slotsFound || 0}</p>
                      </div>
                      <div>
                        <p><strong>⏰ Interval:</strong> {status.checkInterval || '5 minutes'}</p>
                        <p><strong>📧 Provider:</strong> {status.emailProvider || 'SendGrid'}</p>
                        <p><strong>📍 Locations:</strong> {status.locations?.join(', ') || 'Södertälje, Farsta'}</p>
                      </div>
                    </div>
                    
                    {status.sessionWorking && (
                      <div className="mt-3 p-2 bg-green-100 rounded text-green-800">
                        ✅ Session Active • {status.occasionsFound || 0} occasions monitored • Auto-extending time
                      </div>
                    )}
                    
                    {status.lastCheck && (
                      <p className="text-xs text-green-600 mt-2">
                        🕐 Last Check: {status.lastCheck}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Message Display */}
              {message && (
                <div className={`mt-4 p-4 rounded-md ${
                  messageType === 'success' ? 'bg-green-50 border border-green-200 text-green-800' :
                  messageType === 'error' ? 'bg-red-50 border border-red-200 text-red-800' :
                  'bg-blue-50 border border-blue-200 text-blue-800'
                }`}>
                  {message}
                </div>
              )}
            </div>

            {/* Right Column - Motivation & Info */}
            <div className="space-y-6">
              {/* Judo Champion Section */}
              <div className="bg-white rounded-xl shadow-lg p-6 text-center">
                <h3 className="text-xl font-semibold mb-4 text-gray-800">
                  🥇 Carl Dyckner - BJJ Champion Motivation
                </h3>
                <div className="mb-4">
                  <img
                    src="https://scontent-arn2-1.xx.fbcdn.net/v/t39.30808-6/476832982_4732982466980341_7968754554300336412_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=3a1ebe&_nc_ohc=hzxGbzJbLXQQ7kNvwG6thrZ&_nc_oc=AdnI1BkMnZ30oHepgh7ok7LrRUo1fxYhAIfbirk-22FnLHu0egY8C5TtYMzsFwr1BeB0q75PQtm8jVZN9OdYN8Cs&_nc_zt=23&_nc_ht=scontent-arn2-1.xx&_nc_gid=L9M080oI4fwRkt8gnRY2Gg&oh=00_AfOEPnG0Vop-iai_PzYgesTKJe5X9RY-NCI1bbwbUAzowg&oe=686777D3"
                    alt="Carl Dyckner - BJJ Champion"
                    className="w-64 h-80 mx-auto object-cover shadow-lg rounded-lg"
                  />
                </div>
                <p className="text-gray-700 font-medium text-lg">
                  "2 sm guld, 0 körkort, 100 bilar från vänster, 5 ratsingen"
                </p>
                <p className="text-gray-500 text-sm mt-2">
                  🏆 From podium to pedals - time to conquer the road!
                </p>
              </div>

              {/* Sean Paul Section */}
              <div className="bg-white rounded-xl shadow-lg p-6 text-center">
                <h3 className="text-xl font-semibold mb-4 text-gray-800">
                  🎵 Motivation from Sean Paul
                </h3>
                <div className="mb-4">
                  <img
                    src="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300&h=300&fit=crop&crop=face"
                    alt="Sean Paul vibes"
                    className="w-48 h-48 rounded-full mx-auto object-cover shadow-lg"
                  />
                </div>
                <blockquote className="text-gray-600 italic mb-4">
                  "five million and footi nooti shawties! baby girl"
                </blockquote>
                <p className="text-sm text-gray-500">
                  🎶 While you wait for your test slot, bump some Sean Paul! 🎶
                </p>
              </div>

              {/* How It Works */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-semibold mb-4 text-gray-800">
                  🔧 How Live Monitoring Works
                </h3>
                <div className="space-y-3 text-sm text-gray-600">
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">1️⃣</span>
                    <span>Enter your email and preferred date range</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">2️⃣</span>
                    <span>Our V2 system monitors Trafikverket 24/7 every 5 minutes</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">3️⃣</span>
                    <span>Automatic session extension keeps monitoring alive</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">4️⃣</span>
                    <span>Get instant SendGrid email alerts when slots open up</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">5️⃣</span>
                    <span>Book quickly before someone else takes it!</span>
                  </div>
                </div>
              </div>

              {/* Pro Tips */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-3 text-yellow-800">
                  💡 Pro Tips
                </h3>
                <ul className="text-sm text-yellow-700 space-y-2">
                  <li>• Set a wide date range for better chances</li>
                  <li>• Check your email frequently</li>
                  <li>• Have your Bank ID ready to book instantly</li>
                  <li>• Early morning slots often become available</li>
                  <li>• The system automatically extends session time</li>
                  <li>• Only NEW slots trigger emails (no duplicates)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-12 text-gray-500 text-sm">
            <p>🚗 Good luck with your driving test! 🍀</p>
            <p className="mt-2">Made with ❤️ for future drivers • Powered by SendGrid & Next.js</p>
          </div>
        </div>
      </div>
    </>
  );
} 
