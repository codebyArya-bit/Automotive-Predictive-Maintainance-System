# 🚀 Quick Start Guide

Get the Automotive AI platform running in 5 minutes!

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Python 3.8+** (for local development)
- **Node.js 16+** (for frontend development)

## Option 1: Quick Docker Setup (Recommended)

### 1. Clone and Configure

```bash
# Navigate to project directory
cd "Techathon Automotive AI - EY 6.0"

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional for quick start)
```

### 2. Deploy Everything

**On Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh development
```

**On Windows (PowerShell):**
```powershell
.\deploy.ps1 development
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Option 2: Manual Setup

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python api_server.py
```

The API will be available at http://localhost:8000

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:3000

## Option 3: Docker Compose Only

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 🧪 Testing the Application

### 1. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Process a vehicle (example)
curl -X POST http://localhost:8000/api/v1/process-vehicle \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "TEST001",
    "telemetry_data": {
      "engine_temperature": 95,
      "brake_pad_thickness": 3.2,
      "oil_pressure": 45,
      "mileage": 75000
    }
  }'
```

### 2. Test the Frontend

1. Open http://localhost:3000
2. Navigate to "Dashboard"
3. View real-time metrics
4. Check agent monitoring

### 3. Run the Demo

```bash
# Run comprehensive demo
python demo.py

# Or run specific test
python test_api.py
```

## 📊 Monitoring

### Prometheus Metrics

Visit http://localhost:9090 and try these queries:

```promql
# Request rate
rate(http_requests_total[5m])

# Average response time
avg(http_request_duration_seconds)
```

### Grafana Dashboards

1. Open http://localhost:3000
2. Login with admin/admin
3. View pre-configured dashboards

## 🛠️ Development Workflow

### Making Changes

```bash
# Backend changes
# 1. Edit Python files
# 2. The server will auto-reload (if DEBUG=true)

# Frontend changes
cd frontend
npm run dev
# Changes will hot-reload automatically
```

### Running Linters

```bash
# Backend
python -m flake8 *.py agents/*.py
python -m black *.py agents/*.py

# Frontend
cd frontend
npm run lint
```

### Running Tests

```bash
# Backend tests
pytest

# Specific agent test
python test_enhanced_data_analysis.py

# Frontend tests (if configured)
cd frontend
npm test
```

## 🔧 Configuration

### Backend Configuration

Edit `.env` file:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database
DATABASE_URL=sqlite:///automotive_ai.db

# Logging
LOG_LEVEL=INFO

# Feature Flags
ENABLE_ML_MODELS=true
ENABLE_WEBSOCKETS=true
ENABLE_CACHING=true
```

### Frontend Configuration

Edit `frontend/.env.development`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENVIRONMENT=development
VITE_ENABLE_DEBUG=true
VITE_ENABLE_WEBSOCKETS=true
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
# Linux/Mac:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Or change port in .env
API_PORT=8001
```

### Docker Issues

```bash
# Remove all containers and start fresh
docker-compose down -v
docker-compose up -d --build

# View logs
docker-compose logs -f master-agent-api

# Check service status
docker-compose ps
```

### Database Issues

```bash
# Reset database (SQLite)
rm automotive_ai.db
python -c "from database_manager import DatabaseManager; DatabaseManager().initialize_database()"

# Or with Docker
docker-compose down -v  # Removes volumes
docker-compose up -d
```

### Frontend Not Connecting

1. Check `VITE_API_BASE_URL` in `frontend/.env.development`
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check browser console for CORS errors
4. Verify CORS settings in `api_server.py`

## 📚 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Review Architecture**: Read `README.md` for detailed architecture overview
3. **Customize Agents**: Modify agents in the `agents/` directory
4. **Add Features**: See `IMPROVEMENTS_AND_DEPLOYMENT.md` for enhancement ideas
5. **Deploy to Production**: Follow deployment guide in `IMPROVEMENTS_AND_DEPLOYMENT.md`

## 🆘 Getting Help

- Check logs: `docker-compose logs -f`
- Review documentation: `README.md` and `IMPROVEMENTS_AND_DEPLOYMENT.md`
- Test individual components with the test files
- Check health endpoints: http://localhost:8000/health

## 🎉 Success Checklist

- [ ] Docker services running (`docker-compose ps`)
- [ ] API health check passes (`curl http://localhost:8000/health`)
- [ ] Frontend loads (http://localhost:3000)
- [ ] Can process a test vehicle
- [ ] Metrics visible in Prometheus (http://localhost:9090)
- [ ] Grafana dashboard accessible (http://localhost:3000)

---

**Ready to go!** 🚗💨 Your Automotive AI platform is now running!
