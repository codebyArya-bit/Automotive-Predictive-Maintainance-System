# Deploy to Render using render.yaml blueprint

Write-Host "🚀 Deploying to Render..." -ForegroundColor Green
Write-Host ""

# Check if render CLI is installed
$renderExists = Get-Command render -ErrorAction SilentlyContinue
if (-not $renderExists) {
    Write-Host "⚠️  Render CLI not found. Install it first:" -ForegroundColor Yellow
    Write-Host "   npm install -g render-cli"
    Write-Host ""
    Write-Host "Or deploy via Render Dashboard:" -ForegroundColor Cyan
    Write-Host "   1. Go to https://dashboard.render.com"
    Write-Host "   2. Click 'New +' → 'Blueprint'"
    Write-Host "   3. Connect your GitHub repository"
    Write-Host "   4. Select this repository and click 'Apply'"
    exit 1
}

# Check if logged in
Write-Host "Checking Render authentication..."
$whoami = render whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Render first:" -ForegroundColor Yellow
    Write-Host "   render login"
    exit 1
}

Write-Host "✅ Authenticated" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "Deploying services from render.yaml..." -ForegroundColor Cyan
render deploy

Write-Host ""
Write-Host "✅ Deployment initiated!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://dashboard.render.com to monitor deployment"
Write-Host "2. Note your backend URL (e.g., https://automind-api.onrender.com)"
Write-Host "3. Update frontend\.env.production with your backend URL"
Write-Host "4. Run .\deploy-to-vercel.ps1 to deploy frontend"
Write-Host ""
