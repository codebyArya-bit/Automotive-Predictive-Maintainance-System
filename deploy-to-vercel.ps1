# Deploy frontend to Vercel

Write-Host "🚀 Deploying Frontend to Vercel..." -ForegroundColor Green
Write-Host ""

# Check if vercel CLI is installed
$vercelExists = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelExists) {
    Write-Host "⚠️  Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

# Check if logged in
Write-Host "Checking Vercel authentication..."
$whoami = vercel whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Vercel:" -ForegroundColor Yellow
    vercel login
}

Write-Host "✅ Authenticated" -ForegroundColor Green
Write-Host ""

# Check if .env.production is configured
$envFile = "frontend\.env.production"
if (Test-Path $envFile) {
    Write-Host "📋 Current production environment variables:" -ForegroundColor Cyan
    Get-Content $envFile
    Write-Host ""
    $response = Read-Host "Are these values correct? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Please update frontend\.env.production with your backend URL" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "⚠️  frontend\.env.production not found!" -ForegroundColor Yellow
    Write-Host "Please create it with your backend URL:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "VITE_API_BASE_URL=https://your-render-app.onrender.com/api/v1"
    Write-Host "VITE_WS_URL=wss://your-render-app.onrender.com/ws"
    Write-Host "VITE_APP_NAME=AutoMind"
    Write-Host "VITE_ENVIRONMENT=production"
    exit 1
}

# Deploy to preview first
Write-Host "Deploying to preview environment..." -ForegroundColor Cyan
vercel

Write-Host ""
$response = Read-Host "Deploy to production? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "Deploying to production..." -ForegroundColor Cyan
    vercel --prod

    Write-Host ""
    Write-Host "✅ Deployment complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Update CORS in Render" -ForegroundColor Yellow
    Write-Host "1. Go to your Render dashboard"
    Write-Host "2. Select automind-api service"
    Write-Host "3. Go to Environment tab"
    Write-Host "4. Update CORS_ORIGINS with your Vercel URL"
    Write-Host "   (Check the deployment output above for your URL)"
}
