import { useState, useEffect } from 'react';
import Head from 'next/head';
import { format, addDays } from 'date-fns';

interface MonitoringStatus {
  isActive: boolean;
  email: string;
  fromDate: string;
  toDate: string;
  slotsFound: number;
  lastCheck: string;
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

  const startMonitoring = async () => {
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
      const response = await fetch('/api/start-monitoring', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          fromDate,
          toDate,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        showMessage('Monitoring started! You will receive emails when slots become available.', 'success');
        checkStatus();
      } else {
        showMessage(data.error || 'Failed to start monitoring', 'error');
      }
    } catch (error) {
      showMessage('Network error. Please try again.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const stopMonitoring = async () => {
    try {
      const response = await fetch('/api/stop-monitoring', {
        method: 'POST',
      });

      if (response.ok) {
        showMessage('Monitoring stopped.', 'info');
        setStatus(null);
      }
    } catch (error) {
      showMessage('Failed to stop monitoring', 'error');
    }
  };

  const checkStatus = async () => {
    try {
      const response = await fetch('/api/status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch status');
    }
  };

  const testEmail = async () => {
    if (!email) {
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
                🎯 Start Monitoring
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
                  {email && (
                    <p className="text-sm text-green-600 mt-1">
                      ✅ Email entered - test button enabled
                    </p>
                  )}
                </div>

                {/* Test Email Button */}
                <div>
                  <button
                    onClick={testEmail}
                    disabled={isLoading || !email}
                    className={`w-full font-medium py-2 px-4 rounded-md transition duration-200 flex items-center justify-center mb-2 ${
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
                  
                  {/* Debug information */}
                  <div className="text-xs text-gray-500 mb-2 text-center">
                    Debug: Email={email ? '✅' : '❌'} | Loading={isLoading ? '✅' : '❌'} | Disabled={isLoading || !email ? '✅' : '❌'}
                  </div>
                  
                  {!email && (
                    <p className="text-sm text-gray-500 mb-4 text-center">
                      ↑ Enter an email address above to enable testing
                    </p>
                  )}
                  {email && !isLoading && (
                    <p className="text-sm text-green-600 mb-4 text-center">
                      ✅ Button should be clickable now!
                    </p>
                  )}
                  {isLoading && (
                    <p className="text-sm text-orange-600 mb-4 text-center">
                      ⏳ Please wait - operation in progress...
                    </p>
                  )}
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
                    📧 <strong>Email:</strong> Powered by SendGrid ⚡
                  </p>
                </div>

                {/* Action Buttons */}
                {!status?.isActive ? (
                  <button
                    onClick={startMonitoring}
                    disabled={isLoading}
                    className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-md transition duration-200 flex items-center justify-center"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Starting...
                      </>
                    ) : (
                      '🚀 Start Monitoring'
                    )}
                  </button>
                ) : (
                  <button
                    onClick={stopMonitoring}
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-md transition duration-200"
                  >
                    🛑 Stop Monitoring
                  </button>
                )}
              </div>

              {/* Status Display */}
              {status?.isActive && (
                <div className="mt-6 bg-green-50 border border-green-200 rounded-md p-4">
                  <h3 className="font-semibold text-green-800 mb-2">✅ Monitoring Active</h3>
                  <div className="text-sm text-green-700 space-y-1">
                    <p>📧 Email: {status.email}</p>
                    <p>📅 Period: {status.fromDate} to {status.toDate}</p>
                    <p>🎯 Slots Found: {status.slotsFound}</p>
                    <p>🕐 Last Check: {status.lastCheck}</p>
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

            {/* Right Column - Sean Paul & Info */}
            <div className="space-y-6">
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
                  "Just gimme the light and pass the doh... and your körkort!"
                </blockquote>
                <p className="text-sm text-gray-500">
                  🎶 While you wait for your test slot, bump some Sean Paul! 🎶
                </p>
              </div>

              {/* How It Works */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-semibold mb-4 text-gray-800">
                  🔧 How It Works
                </h3>
                <div className="space-y-3 text-sm text-gray-600">
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">1️⃣</span>
                    <span>Enter your email and preferred date range</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">2️⃣</span>
                    <span>Our system monitors Trafikverket every 5 minutes</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">3️⃣</span>
                    <span>Get instant email alerts when slots open up</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-500 mr-2">4️⃣</span>
                    <span>Book quickly before someone else takes it!</span>
                  </div>
                </div>
              </div>

              {/* Tips */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-3 text-yellow-800">
                  💡 Pro Tips
                </h3>
                <ul className="text-sm text-yellow-700 space-y-2">
                  <li>• Set a wide date range for better chances</li>
                  <li>• Check your email frequently</li>
                  <li>• Have your Bank ID ready to book instantly</li>
                  <li>• Early morning slots often become available</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-12 text-gray-500 text-sm">
            <p>🚗 Good luck with your driving test! 🍀</p>
            <p className="mt-2">Made with ❤️ for future drivers</p>
          </div>
        </div>
      </div>
    </>
  );
} 