# PowerShell Deployment Script for Automotive AI Platform
# Usage: .\deploy.ps1 [development|staging|production]

param(
    [Parameter(Position=0)]
    [ValidateSet('development', 'staging', 'production')]
    [string]$Environment = 'development'
)

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "========================================" "Green"
Write-ColorOutput "   Automotive AI Deployment Script     " "Green"
Write-ColorOutput "   Environment: $Environment           " "Green"
Write-ColorOutput "========================================" "Green"

# Pre-flight checks
Write-ColorOutput "`n>>> Running pre-flight checks..." "Yellow"

# Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-ColorOutput "Error: Docker is not installed" "Red"
    exit 1
}

if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-ColorOutput "Error: Docker Compose is not installed" "Red"
    exit 1
}

Write-ColorOutput "✓ Docker and Docker Compose are installed" "Green"

# Check for environment file
if (!(Test-Path ".env.$Environment") -and !(Test-Path ".env")) {
    Write-ColorOutput "Error: No .env.$Environment or .env file found" "Red"
    Write-ColorOutput "Please create an environment file before deploying" "Red"
    exit 1
}

# Use environment-specific .env file if it exists
if (Test-Path ".env.$Environment") {
    Write-ColorOutput ">>> Using .env.$Environment configuration" "Yellow"
    Copy-Item ".env.$Environment" ".env" -Force
}

# Backend deployment
Write-ColorOutput "`n>>> Preparing backend..." "Yellow"

# Check if Python is available
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Installing Python dependencies..."
    python -m pip install -r requirements.txt --quiet
    Write-ColorOutput "✓ Python dependencies installed" "Green"
}

# Run linting
Write-ColorOutput "`n>>> Running code quality checks..." "Yellow"
python -m flake8 *.py agents/*.py --count --statistics
Write-ColorOutput "✓ Backend linting complete" "Green"

# Frontend deployment
Write-ColorOutput "`n>>> Preparing frontend..." "Yellow"

Push-Location frontend

# Create environment file for frontend
if (Test-Path "../.env.$Environment") {
    Get-Content "../.env.$Environment" | Where-Object { $_ -match "^VITE_" } | Out-File -FilePath ".env" -Encoding utf8
}

# Install dependencies
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "Installing Node dependencies..."
    npm install --silent
    Write-ColorOutput "✓ Node dependencies installed" "Green"

    # Run linting
    Write-Host "Running frontend linting..."
    npm run lint
    Write-ColorOutput "✓ Frontend linting complete" "Green"

    # Build frontend for production/staging
    if ($Environment -eq "production" -or $Environment -eq "staging") {
        Write-Host "Building frontend for $Environment..."
        npm run build
        Write-ColorOutput "✓ Frontend built successfully" "Green"
    }
}

Pop-Location

# Docker deployment
Write-ColorOutput "`n>>> Starting Docker services..." "Yellow"

switch ($Environment) {
    "development" {
        Write-Host "Starting development environment..."
        docker-compose up -d --build
    }
    "staging" {
        Write-Host "Starting staging environment..."
        docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build
    }
    "production" {
        Write-Host "Starting production environment..."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    }
}

# Wait for services
Write-ColorOutput "`n>>> Waiting for services to be ready..." "Yellow"
Start-Sleep -Seconds 10

# Health checks
Write-ColorOutput "`n>>> Running health checks..." "Yellow"

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-ColorOutput "✓ API is healthy" "Green"
    }
} catch {
    Write-ColorOutput "✗ API health check failed" "Red"
    Write-ColorOutput "Check logs with: docker-compose logs master-agent-api" "Yellow"
}

# Display service URLs
Write-ColorOutput "`n>>> Service URLs:" "Yellow"
Write-Host "  API:        http://localhost:8000"
Write-Host "  Frontend:   http://localhost:3000"
Write-Host "  Prometheus: http://localhost:9090"
Write-Host "  Grafana:    http://localhost:3000 (admin/admin)"
Write-Host "  API Docs:   http://localhost:8000/docs"

# Show useful commands
Write-ColorOutput "`n>>> Useful commands:" "Yellow"
Write-Host "  View logs:        docker-compose logs -f"
Write-Host "  Stop services:    docker-compose down"
Write-Host "  Restart services: docker-compose restart"
Write-Host "  View status:      docker-compose ps"

Write-ColorOutput "`n========================================" "Green"
Write-ColorOutput "   Deployment Complete! 🚀              " "Green"
Write-ColorOutput "========================================" "Green"
