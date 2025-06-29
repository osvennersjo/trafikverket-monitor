# 🚗 Quick Deployment Guide - Share Your Körkort Monitor!

## 🎯 What You've Got

A complete web app that:
- 📧 Lets friends enter their email and date preferences
- 🤖 Monitors Trafikverket for driving test slots automatically
- 📱 Works on all devices (mobile, tablet, desktop)
- 🎵 Features Sean Paul motivation (as requested!)
- ⚡ Sends instant email alerts when slots become available

## 🚀 Deploy in 5 Minutes

### Option 1: Vercel (Easiest)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "🚗 Initial Trafikverket Monitor"
   git remote add origin https://github.com/YOURUSERNAME/trafikverket-monitor.git
   git push -u origin main
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repo
   - Add environment variables:
     ```
     SMTP_HOST=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USER=your.email@gmail.com
     SMTP_PASSWORD=your-app-password
     FROM_EMAIL=your.email@gmail.com
     ```
   - Click Deploy!

3. **Get your URL**: `https://your-app-name.vercel.app`

### Option 2: Run Setup Script

```bash
./deploy-setup.sh
npm run dev
```

## 📧 Email Setup (Gmail)

1. **Enable 2FA** on your Google account
2. **Create App Password**:
   - Google Account → Security → App passwords
   - Generate password for "Mail"
   - Use this in `SMTP_PASSWORD`

## 🎯 Share with Friends

Send them your Vercel URL! They can:
1. Enter their email address
2. Select date range for monitoring
3. Click "Start Monitoring"
4. Get instant notifications when slots appear!

## 🎵 Sean Paul Feature

Your friends will enjoy:
- Sean Paul's photo for motivation
- Inspirational quotes in the UI
- Sean Paul references in email notifications
- Because everyone needs some dancehall vibes while waiting for their driving test! 😄

## 📱 Mobile Optimized

The app works perfectly on phones, so your friends can use it anywhere!

## 🔒 Privacy & Security

- No data is stored permanently
- Email addresses are only used for notifications
- All communication with Trafikverket is read-only
- Respects rate limits and terms of service

---

**Your friends will love this! 🎉**

Just send them the link and they're ready to monitor for driving test slots with style! 🚗🎵 