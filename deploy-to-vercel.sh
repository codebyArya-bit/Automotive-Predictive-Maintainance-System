#!/bin/bash
# Deploy frontend to Vercel

echo "🚀 Deploying Frontend to Vercel..."
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if logged in
echo "Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "Please login to Vercel:"
    vercel login
fi

echo "✅ Authenticated"
echo ""

# Check if .env.production is configured
if [ -f "frontend/.env.production" ]; then
    echo "📋 Current production environment variables:"
    cat frontend/.env.production
    echo ""
    read -p "Are these values correct? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please update frontend/.env.production with your backend URL"
        exit 1
    fi
else
    echo "⚠️  frontend/.env.production not found!"
    echo "Please create it with your backend URL:"
    echo ""
    echo "VITE_API_BASE_URL=https://your-render-app.onrender.com/api/v1"
    echo "VITE_WS_URL=wss://your-render-app.onrender.com/ws"
    echo "VITE_APP_NAME=AutoMind"
    echo "VITE_ENVIRONMENT=production"
    exit 1
fi

# Deploy to preview first
echo "Deploying to preview environment..."
vercel

echo ""
read -p "Deploy to production? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploying to production..."
    vercel --prod

    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "⚠️  IMPORTANT: Update CORS in Render"
    echo "1. Go to your Render dashboard"
    echo "2. Select automind-api service"
    echo "3. Go to Environment tab"
    echo "4. Update CORS_ORIGINS with your Vercel URL"
    echo "   (Check the deployment output above for your URL)"
fi
