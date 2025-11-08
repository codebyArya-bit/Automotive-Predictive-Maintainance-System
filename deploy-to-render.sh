#!/bin/bash
# Deploy to Render using render.yaml blueprint

echo "🚀 Deploying to Render..."
echo ""

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "⚠️  Render CLI not found. Install it first:"
    echo "   npm install -g render-cli"
    echo ""
    echo "Or deploy via Render Dashboard:"
    echo "   1. Go to https://dashboard.render.com"
    echo "   2. Click 'New +' → 'Blueprint'"
    echo "   3. Connect your GitHub repository"
    echo "   4. Select this repository and click 'Apply'"
    exit 1
fi

# Check if logged in
echo "Checking Render authentication..."
if ! render whoami &> /dev/null; then
    echo "Please login to Render first:"
    echo "   render login"
    exit 1
fi

echo "✅ Authenticated"
echo ""

# Deploy
echo "Deploying services from render.yaml..."
render deploy

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "Next steps:"
echo "1. Go to https://dashboard.render.com to monitor deployment"
echo "2. Note your backend URL (e.g., https://automind-api.onrender.com)"
echo "3. Update frontend/.env.production with your backend URL"
echo "4. Run ./deploy-to-vercel.sh to deploy frontend"
echo ""
