#!/bin/bash
# Deployment Script for Automotive AI Platform
# Usage: ./deploy.sh [development|staging|production]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
PROJECT_NAME="automotive-ai"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Automotive AI Deployment Script     ${NC}"
echo -e "${GREEN}   Environment: $ENVIRONMENT           ${NC}"
echo -e "${GREEN}========================================${NC}"

# Function to print section headers
print_section() {
    echo -e "\n${YELLOW}>>> $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Pre-flight checks
print_section "Running pre-flight checks..."

if ! command_exists docker; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Check for environment file
if [ ! -f ".env.$ENVIRONMENT" ] && [ ! -f ".env" ]; then
    echo -e "${RED}Error: No .env.$ENVIRONMENT or .env file found${NC}"
    echo "Please create an environment file before deploying"
    exit 1
fi

# Use environment-specific .env file if it exists
if [ -f ".env.$ENVIRONMENT" ]; then
    print_section "Using .env.$ENVIRONMENT configuration"
    cp ".env.$ENVIRONMENT" .env
fi

# Backend deployment
print_section "Preparing backend..."

# Install Python dependencies
if command_exists python3; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
fi

# Run linting
print_section "Running code quality checks..."
python -m flake8 *.py agents/*.py --count --statistics || true
echo -e "${GREEN}✓ Backend linting complete${NC}"

# Frontend deployment
print_section "Preparing frontend..."

cd frontend

# Create environment file for frontend
if [ -f "../.env.$ENVIRONMENT" ]; then
    grep "VITE_" "../.env.$ENVIRONMENT" > .env 2>/dev/null || echo "No VITE_ variables found"
fi

# Install dependencies
if command_exists npm; then
    echo "Installing Node dependencies..."
    npm install --silent
    echo -e "${GREEN}✓ Node dependencies installed${NC}"

    # Run linting
    echo "Running frontend linting..."
    npm run lint || true
    echo -e "${GREEN}✓ Frontend linting complete${NC}"

    # Build frontend
    if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "staging" ]; then
        echo "Building frontend for $ENVIRONMENT..."
        npm run build
        echo -e "${GREEN}✓ Frontend built successfully${NC}"
    fi
fi

cd ..

# Docker deployment
print_section "Starting Docker services..."

case $ENVIRONMENT in
    development)
        echo "Starting development environment..."
        docker-compose up -d --build
        ;;
    staging)
        echo "Starting staging environment..."
        docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build
        ;;
    production)
        echo "Starting production environment..."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
        ;;
    *)
        echo -e "${RED}Unknown environment: $ENVIRONMENT${NC}"
        echo "Valid options: development, staging, production"
        exit 1
        ;;
esac

# Wait for services to be ready
print_section "Waiting for services to be ready..."
sleep 10

# Health checks
print_section "Running health checks..."

# Check API health
API_URL="http://localhost:8000/health"
if curl -f -s "$API_URL" > /dev/null; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API health check failed${NC}"
    echo "Check logs with: docker-compose logs master-agent-api"
fi

# Check database
if docker-compose ps postgres | grep -q "Up"; then
    echo -e "${GREEN}✓ Database is running${NC}"
else
    echo -e "${YELLOW}⚠ Database may not be running${NC}"
fi

# Check Redis
if docker-compose ps redis | grep -q "Up"; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠ Redis may not be running${NC}"
fi

# Display service URLs
print_section "Service URLs:"
echo "  API:        http://localhost:8000"
echo "  Frontend:   http://localhost:3000"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana:    http://localhost:3000 (admin/admin)"
echo "  API Docs:   http://localhost:8000/docs"

# Show logs command
print_section "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  View status:      docker-compose ps"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}   Deployment Complete! 🚀              ${NC}"
echo -e "${GREEN}========================================${NC}"
