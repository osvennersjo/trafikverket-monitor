# 🚗 Trafikverket Driving Test Monitor - Web App

A beautiful web application to monitor Swedish driving test availability with Sean Paul vibes! 🎵

![Trafikverket Monitor](https://img.shields.io/badge/Status-Ready%20to%20Deploy-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![Tailwind](https://img.shields.io/badge/Tailwind-3-cyan)

## ✨ Features

- 🎯 **Smart Monitoring**: Automatically discovers working Trafikverket API endpoints
- 📍 **Location-Specific**: Monitors Södertälje and Farsta driving test centers
- 📧 **Email Notifications**: Instant alerts when slots become available
- 🎵 **Sean Paul Motivation**: Because why not! 
- 🎨 **Beautiful UI**: Modern, responsive design with Tailwind CSS
- ⚡ **Real-time Updates**: Live status updates every 30 seconds
- 🔒 **Secure**: Environment variables for sensitive configuration

## 🚀 Quick Start

### Deploy to Vercel (Recommended)

1. **Fork this repository** or click "Deploy to Vercel" button:

   [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/trafikverket-monitor)

2. **Set up environment variables** in Netlify dashboard:
   - Go to your site dashboard → Site Settings → Environment Variables
   - Add the following variables:

   ```
   SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
   FROM_EMAIL=your-verified-email@example.com
   ```

3. **Deploy!** Netlify will automatically build and deploy your app from GitHub.

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/osvennersjo/trafikverket-monitor.git
   cd trafikverket-monitor
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   # Create .env.local with your SendGrid settings
   echo "SENDGRID_API_KEY=SG.your_api_key_here" > .env.local
   echo "FROM_EMAIL=your-email@example.com" >> .env.local
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```

5. **Open your browser**: Visit [http://localhost:3000](http://localhost:3000)

## 📧 Email Configuration

### SendGrid Setup (Recommended)

1. **Create SendGrid Account**: Sign up at [sendgrid.com](https://sendgrid.com)
2. **Generate API Key**:
   - Go to Settings → API Keys
   - Create API Key with "Mail Send" permissions
   - Copy the API key (starts with `SG.`)
3. **Verify Sender Email**:
   - Go to Settings → Sender Authentication
   - Verify your FROM_EMAIL address
   - Complete the verification process

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SENDGRID_API_KEY` | SendGrid API key | SG.abc123... |
| `FROM_EMAIL` | Verified sender email | your-email@example.com |

## 🎯 How It Works

1. **API Discovery**: Automatically finds working Trafikverket endpoints
2. **Smart Monitoring**: Checks for new slots every 5 minutes
3. **Location Targeting**: Focuses on Södertälje and Farsta test centers
4. **Change Detection**: Only notifies about genuinely new slots
5. **Email Alerts**: Beautiful HTML emails with Sean Paul motivation!

## 🛠 API Endpoints

The app provides these API endpoints:

- `POST /api/start-monitoring` - Start monitoring with email and date range
- `POST /api/stop-monitoring` - Stop active monitoring
- `GET /api/status` - Get current monitoring status

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SENDGRID_API_KEY` | SendGrid API key for sending emails | SG.abc123def456... |
| `FROM_EMAIL` | Verified sender email address | your-email@example.com |

### Monitoring Settings

- **Check Interval**: 5 minutes (300,000ms)
- **Target Locations**: Södertälje, Farsta
- **Test Type**: Manual B License (ID: 5)
- **Timeout**: 15 seconds per API request

## 🎨 Customization

### Adding New Locations

Edit `lib/trafikverket-monitor.ts` and add to `targetCities`:

```typescript
const targetCities = ['södertälje', 'farsta', 'stockholm', 'göteborg'];
```

### Changing Check Interval

In `pages/api/start-monitoring.ts`:

```typescript
checkInterval: 3 * 60 * 1000, // 3 minutes instead of 5
```

### Sean Paul Quotes

Edit the Sean Paul section in `pages/index.tsx` to add more quotes!

## 🚀 Deployment Options

### Netlify (Recommended)
- ✅ Easy GitHub integration
- ✅ Automatic deployments
- ✅ Environment variables
- ✅ Next.js support with plugin
- ✅ Built-in location filtering protection

### Vercel
- ✅ Easy deployment
- ✅ Automatic HTTPS
- ✅ Environment variables
- ✅ Serverless functions

### Railway
- ✅ Great for Node.js apps
- ✅ Built-in environment variables

### Heroku
- ✅ Traditional deployment
- ⚠️ May sleep on free tier

## 🐛 Troubleshooting

### Common Issues

1. **Email not sending**:
   - Verify SendGrid API key is correct
   - Ensure FROM_EMAIL is verified in SendGrid
   - Check SendGrid dashboard for delivery logs

2. **No API endpoints found**:
   - Trafikverket may have updated their API
   - Check browser network tab for new endpoints
   - Update endpoint list in monitoring code

3. **Monitoring stops**:
   - Check Netlify function logs
   - Verify function timeout settings (default: 10s, may need 26s)
   - Restart monitoring from the UI

### Debug Mode

Add console logging by setting environment variable:
```
DEBUG=true
```

## 📱 Mobile Friendly

The app is fully responsive and works great on:
- 📱 Mobile phones
- 📱 Tablets
- 💻 Desktop computers

## 🔒 Security & Privacy

- ✅ No driving test data is stored
- ✅ Email addresses are not logged
- ✅ All API calls are read-only
- ✅ Environment variables protect sensitive data
- ✅ Respects Trafikverket's rate limits

## 📈 Monitoring Stats

The app tracks:
- Number of slots found
- Last check timestamp
- Monitoring status
- API endpoint health

## 🎵 Sean Paul Easter Eggs

Look out for Sean Paul references throughout the app:
- 🎵 Motivational quotes
- 🎶 Email notifications
- 🎤 UI messages
- 🎧 Loading states

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect Trafikverket's terms of service and use responsibly.

## 🙏 Acknowledgments

- Trafikverket for their driving test platform
- Sean Paul for the motivation 🎵
- The Next.js team for the amazing framework
- Vercel for easy deployment

---

**Made with ❤️ and Sean Paul vibes for future Swedish drivers!** 🚗🎵

*"Just gimme the light and pass the doh... and your körkort!"* - Sean Paul (probably) 