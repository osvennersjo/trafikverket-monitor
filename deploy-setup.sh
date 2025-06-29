#!/bin/bash

echo "🚗 Trafikverket Monitor - Web App Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js version 18+ is required. Current version: $(node -v)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node -v) is installed${NC}"

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}📝 Creating .env.local file...${NC}"
    cp env.example .env.local
    echo -e "${YELLOW}⚠️  Please edit .env.local with your email settings!${NC}"
    echo -e "${BLUE}   You need to configure:${NC}"
    echo -e "   - SMTP_HOST (e.g., smtp.gmail.com)"
    echo -e "   - SMTP_PORT (e.g., 587)"
    echo -e "   - SMTP_USER (your email)"
    echo -e "   - SMTP_PASSWORD (app password)"
    echo -e "   - FROM_EMAIL (your email)"
fi

# Build the project
echo -e "${BLUE}🔨 Building the project...${NC}"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Project built successfully${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Edit .env.local with your email settings"
echo -e "2. Run 'npm run dev' to start development server"
echo -e "3. Visit http://localhost:3000 to see your app"
echo ""
echo -e "${BLUE}For deployment:${NC}"
echo -e "1. Push to GitHub"
echo -e "2. Connect to Vercel"
echo -e "3. Add environment variables in Vercel dashboard"
echo -e "4. Deploy!"
echo ""
echo -e "${YELLOW}🎵 Don't forget to add some Sean Paul to your playlist!${NC}"

# Initialize git repo
git init && git add . && git commit -m "🚗 Trafikverket Monitor"

# Push to GitHub and deploy to Vercel
# Add email environment variables in Vercel dashboard 