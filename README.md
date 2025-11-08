# 🚗 Master Agent Orchestration System

## Automotive Predictive Maintenance with LangGraph

A sophisticated multi-agent orchestration system for automotive predictive maintenance using LangGraph, featuring intelligent workflow management, UEBA compliance monitoring, and comprehensive error handling.

## 🏗️ Architecture Overview

The system implements a **Master Agent** that orchestrates **7 specialized worker agents** through a state-driven workflow using LangGraph for robust state management and conditional routing.

### Core Components

```
┌─────────────────┐    ┌──────────────────────────────────────┐
│   FastAPI       │    │           Master Agent               │
│   REST API      │───▶│        (LangGraph Workflow)          │
└─────────────────┘    └──────────────────────────────────────┘
                                        │
                       ┌────────────────┼────────────────┐
                       ▼                ▼                ▼
              ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
              │ Data Analysis   │ │ Diagnosis   │ │ Customer    │
              │ Agent           │ │ Agent       │ │ Engagement  │
              └─────────────────┘ └─────────────┘ └─────────────┘
                       ▼                ▼                ▼
              ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
              │ Scheduling      │ │ Feedback    │ │ Manufacturing│
              │ Agent           │ │ Agent       │ │ Insights     │
              └─────────────────┘ └─────────────┘ └─────────────┘
                                        │
                                ┌─────────────┐
                                │ UEBA        │
                                │ Monitoring  │
                                └─────────────┘
```

## 🤖 Worker Agents

### 1. **Data Analysis Agent** (`data_analysis_agent.py`)
- Processes vehicle telemetry data
- Performs anomaly detection and pattern analysis
- Generates initial health assessments

### 2. **Diagnosis Agent** (`diagnosis_agent.py`)
- Interprets analysis results
- Calculates failure probabilities
- Generates predictive maintenance recommendations
- Estimates repair costs and timelines

### 3. **Customer Engagement Agent** (`customer_engagement_agent.py`)
- Handles customer communications (voice/app notifications)
- Manages conversation context and sentiment analysis
- Determines appropriate contact methods based on priority

### 4. **Scheduling Agent** (`scheduling_agent.py`)
- Books service appointments
- Manages service center availability
- Optimizes scheduling based on priority and location

### 5. **Feedback Agent** (`feedback_agent.py`)
- Collects customer satisfaction data
- Gathers improvement suggestions
- Analyzes service quality metrics

### 6. **Manufacturing Insights Agent** (`manufacturing_insights_agent.py`)
- Analyzes fleet-wide patterns
- Identifies quality issues and trends
- Generates manufacturing improvement recommendations

### 7. **UEBA Monitoring Agent** (`ueba_monitoring_agent.py`)
- Tracks user and entity behavior analytics
- Monitors security compliance (SOX, GDPR, ISO27001, NIST)
- Detects anomalous activities and security risks

## 🔄 Workflow Logic

The Master Agent uses **conditional edges** to route between agents based on:

- **Prediction Severity**: P0/P1 → Voice contact, P2/P3 → App notification
- **Customer Response**: Positive → Scheduling, Negative → Feedback, Confused → Human escalation
- **System Health**: Circuit breaker states and error conditions
- **Security Risks**: UEBA compliance violations

## 🛡️ Error Handling & Resilience

### Circuit Breaker Pattern
- Individual circuit breakers for each agent
- Automatic fallback strategies when agents fail
- Exponential backoff retry logic

### Fallback Mechanisms
- **Data Analysis**: Rule-based analysis when ML models fail
- **Diagnosis**: Simple diagnostic rules as backup
- **Customer Engagement**: Basic notification system
- **Scheduling**: Manual scheduling fallback

### Health Monitoring
- Real-time system health checks
- Component status monitoring
- Performance metrics collection

## 📊 Monitoring & Observability

### Prometheus Metrics
- Agent execution times and success rates
- System resource utilization
- Security event tracking
- Customer satisfaction scores

### Structured Logging
- Comprehensive audit trails
- Error tracking and analysis
- Performance monitoring
- Compliance logging

### Real-time Dashboard
- System health overview
- Agent performance metrics
- Security analytics
- Recent activities feed

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd master-agent-orchestration
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the system**
   ```bash
   # Start the FastAPI server
   python api_server.py
   
   # Or run the demo
   python demo.py
   ```

### Environment Configuration

Create a `.env` file with the following variables:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Agent Configuration
MAX_RETRIES=3
CIRCUIT_BREAKER_THRESHOLD=5
HEALTH_CHECK_INTERVAL=30

# Monitoring
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO

# External Services (if needed)
# OPENAI_API_KEY=your_openai_key
# DATABASE_URL=postgresql://user:pass@localhost/db
```

## 📡 API Endpoints

### Core Endpoints

#### `POST /api/v1/process-vehicle`
Process a vehicle through the complete workflow.

**Request:**
```json
{
  "vehicle_id": "VIN123456789",
  "telemetry_data": {
    "engine_temperature": 95.5,
    "brake_pad_thickness": 3.2,
    "oil_pressure": 45.0,
    "mileage": 75000
  },
  "customer_info": {
    "name": "John Doe",
    "phone": "+1234567890",
    "preferred_contact": "voice"
  },
  "priority_override": "P1"
}
```

**Response:**
```json
{
  "success": true,
  "vehicle_id": "VIN123456789",
  "processing_time": 2.34,
  "agents_executed": ["data_analysis", "diagnosis", "customer_engagement"],
  "escalated": false,
  "prediction": {
    "component": "brake_pads",
    "failure_probability": 0.85,
    "predicted_failure_date": "2024-02-15",
    "priority": "P1"
  }
}
```

#### `GET /api/v1/health`
Get comprehensive system health status.

#### `GET /api/v1/dashboard`
Get real-time dashboard data for monitoring.

#### `GET /api/v1/circuit-breakers`
Get circuit breaker status for all agents.

#### `POST /api/v1/demo`
Run demonstration scenarios.

## 🧪 Running Demos

The system includes comprehensive demo scenarios:

```bash
python demo.py
```

**Demo Scenarios:**
- **Critical Engine Failure**: High-priority emergency scenario
- **Brake Maintenance Warning**: Medium-priority maintenance alert
- **Routine Maintenance**: Low-priority scheduled service
- **Healthy Vehicle**: Normal operation validation

## 🔧 Configuration

### Agent Configuration (`config.py`)
```python
class Config:
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_THRESHOLD = 5
    CIRCUIT_BREAKER_TIMEOUT = 60
    
    # Priority thresholds
    CONTACT_PROBABILITY_THRESHOLD = 0.7
    HIGH_PRIORITY_LEVELS = ["P0", "P1"]
```

### State Management (`state.py`)
The system maintains comprehensive state across the workflow:

```python
class State(TypedDict):
    vehicle_id: str
    telemetry_snapshot: Dict[str, Any]
    prediction: Optional[Dict[str, Any]]
    customer_response: Optional[Dict[str, Any]]
    appointment: Optional[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]
    current_agent: str
    retry_count: int
    escalate_to_human: bool
    audit_trail: List[Dict[str, Any]]
```

## 🔒 Security & Compliance

### UEBA Monitoring
- **User Behavior Analytics**: Tracks access patterns and anomalies
- **Entity Behavior Analytics**: Monitors system and agent activities
- **Compliance Frameworks**: SOX, GDPR, ISO27001, NIST support

### Security Features
- Circuit breaker protection against cascading failures
- Comprehensive audit logging
- Risk scoring and alerting
- Anomaly detection and response

## 📈 Performance & Scalability

### Optimization Features
- **Async Processing**: Non-blocking agent execution
- **Circuit Breakers**: Prevent system overload
- **Caching**: Reduce redundant computations
- **Load Balancing**: Distribute processing load

### Monitoring Metrics
- Agent execution times
- Success/failure rates
- Resource utilization
- Customer satisfaction scores

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_agents.py
pytest tests/test_workflow.py
pytest tests/test_api.py
```

## 📚 Development

### Code Style
The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black .

# Lint code
flake8 .

# Type check
mypy .
```

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods (`process`, `get_capabilities`)
3. Add agent to `MasterAgent` workflow
4. Update state management if needed
5. Add monitoring and error handling

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api_server.py"]
```

### Production Considerations
- Use production WSGI server (Gunicorn)
- Configure proper logging levels
- Set up monitoring and alerting
- Implement proper security measures
- Use environment-specific configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the demo scenarios for examples

## 🔮 Future Enhancements

- **Machine Learning Integration**: Advanced predictive models
- **Real-time Streaming**: Live telemetry processing
- **Mobile App Integration**: Customer mobile interface
- **Advanced Analytics**: Deeper insights and reporting
- **Multi-tenant Support**: Enterprise deployment features