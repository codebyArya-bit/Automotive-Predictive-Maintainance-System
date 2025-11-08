# AutoMind Deployment Guide

This guide provides step-by-step instructions for deploying the AutoMind system across different environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [AWS EKS Deployment](#aws-eks-deployment)
6. [Monitoring Setup](#monitoring-setup)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **Docker**: Version 20.10 or later
- **Docker Compose**: Version 2.0 or later
- **kubectl**: Version 1.28 or later
- **Terraform**: Version 1.6 or later
- **AWS CLI**: Version 2.0 or later (for AWS deployments)
- **Helm**: Version 3.0 or later (optional)

### Required Accounts and Access

- AWS Account with appropriate permissions
- GitHub account for CI/CD
- Slack workspace for notifications (optional)
- Email service for alerts (optional)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/automind.git
cd automind
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
# Database
POSTGRES_DB=automind_dev
POSTGRES_USER=automind_user
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_redis_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Security
JWT_SECRET=your_jwt_secret_key
```

### 3. Start Local Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f automind-api
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## Docker Deployment

### 1. Build Images

```bash
# Build API image
docker build -t automind-api:latest .

# Tag for registry
docker tag automind-api:latest your-registry/automind-api:latest

# Push to registry
docker push your-registry/automind-api:latest
```

### 2. Production Docker Compose

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

## Kubernetes Deployment

### 1. Prepare Kubernetes Cluster

```bash
# Verify cluster access
kubectl cluster-info

# Create namespace
kubectl apply -f k8s/namespace.yaml
```

### 2. Configure Secrets

```bash
# Create database password secret
kubectl create secret generic postgres-secret \
  --from-literal=password=your_secure_password \
  --namespace=automind

# Create Redis password secret
kubectl create secret generic redis-secret \
  --from-literal=password=your_redis_password \
  --namespace=automind

# Create JWT secret
kubectl create secret generic jwt-secret \
  --from-literal=secret=your_jwt_secret \
  --namespace=automind
```

### 3. Deploy Services

```bash
# Apply all configurations
kubectl apply -k k8s/

# Check deployment status
kubectl get pods -n automind
kubectl get services -n automind
kubectl get ingress -n automind
```

### 4. Verify Deployment

```bash
# Check pod logs
kubectl logs -f deployment/automind-api -n automind

# Port forward for testing
kubectl port-forward service/automind-api 8000:8000 -n automind

# Test API
curl http://localhost:8000/health
```

## AWS EKS Deployment

### 1. Configure AWS CLI

```bash
# Configure AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

### 2. Deploy Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="environments/prod.tfvars"

# Apply infrastructure
terraform apply -var-file="environments/prod.tfvars"

# Get cluster credentials
aws eks update-kubeconfig --region us-west-2 --name automind-prod
```

### 3. Deploy Application

```bash
# Update image tags in kustomization.yaml
cd ../k8s
kubectl apply -k .

# Check deployment
kubectl get pods -n automind
kubectl get services -n automind
```

### 4. Configure DNS and SSL

```bash
# Get load balancer DNS
kubectl get ingress -n automind

# Update DNS records in Route53
# SSL certificates will be automatically provisioned by cert-manager
```

## Monitoring Setup

### 1. Deploy Monitoring Stack

```bash
# Apply monitoring configurations
kubectl apply -f k8s/monitoring-deployment.yaml

# Check monitoring pods
kubectl get pods -n automind | grep -E "(prometheus|grafana|alertmanager)"
```

### 2. Access Monitoring Dashboards

```bash
# Port forward Grafana
kubectl port-forward service/grafana 3000:3000 -n automind

# Port forward Prometheus
kubectl port-forward service/prometheus 9090:9090 -n automind

# Access dashboards
open http://localhost:3000  # Grafana (admin/admin123)
open http://localhost:9090  # Prometheus
```

### 3. Configure Alerts

```bash
# Verify alerting rules
kubectl get prometheusrules -n automind

# Check Alertmanager configuration
kubectl get configmap alertmanager-config -n automind -o yaml
```

## Environment-Specific Configurations

### Development Environment

```bash
# Use development variables
terraform apply -var-file="environments/dev.tfvars"

# Reduced resource limits
# Debug logging enabled
# Single replica deployments
```

### Staging Environment

```bash
# Use staging variables
terraform apply -var-file="environments/staging.tfvars"

# Production-like configuration
# Full monitoring enabled
# Load testing capabilities
```

### Production Environment

```bash
# Use production variables
terraform apply -var-file="environments/prod.tfvars"

# High availability setup
# Auto-scaling enabled
# Full security hardening
# Backup and disaster recovery
```

## Security Considerations

### 1. Network Security

- VPC with private subnets
- Security groups with minimal access
- WAF protection for public endpoints
- Network policies in Kubernetes

### 2. Data Security

- Encryption at rest and in transit
- Secrets management with AWS Secrets Manager
- Regular security scanning
- Access logging and monitoring

### 3. Access Control

- IAM roles and policies
- Kubernetes RBAC
- Multi-factor authentication
- Regular access reviews

## Backup and Disaster Recovery

### 1. Database Backups

```bash
# Automated RDS backups (configured in Terraform)
# Point-in-time recovery enabled
# Cross-region backup replication
```

### 2. Application State

```bash
# Persistent volume snapshots
# Configuration backups
# Container image versioning
```

### 3. Disaster Recovery Testing

```bash
# Regular DR drills
# Recovery time objectives (RTO): 4 hours
# Recovery point objectives (RPO): 1 hour
```

## Performance Optimization

### 1. Auto Scaling

```bash
# Horizontal Pod Autoscaler
kubectl get hpa -n automind

# Cluster Autoscaler
kubectl get nodes

# Vertical Pod Autoscaler (if enabled)
kubectl get vpa -n automind
```

### 2. Resource Optimization

```bash
# Monitor resource usage
kubectl top pods -n automind
kubectl top nodes

# Adjust resource requests and limits
# Optimize container images
# Use multi-stage builds
```

## Troubleshooting

### Common Issues

1. **Pod Startup Issues**
   ```bash
   kubectl describe pod <pod-name> -n automind
   kubectl logs <pod-name> -n automind
   ```

2. **Database Connection Issues**
   ```bash
   kubectl exec -it deployment/automind-api -n automind -- psql -h postgres -U automind_user -d automind_db
   ```

3. **Service Discovery Issues**
   ```bash
   kubectl get endpoints -n automind
   kubectl get services -n automind
   ```

4. **Ingress Issues**
   ```bash
   kubectl describe ingress automind-ingress -n automind
   kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
   ```

### Health Checks

```bash
# API health
curl https://api.automind.com/health

# Database health
kubectl exec -it deployment/postgres -n automind -- pg_isready

# Redis health
kubectl exec -it deployment/redis -n automind -- redis-cli ping
```

### Log Analysis

```bash
# Application logs
kubectl logs -f deployment/automind-api -n automind

# System logs
kubectl logs -f daemonset/fluentd -n kube-system

# Monitoring logs
kubectl logs -f deployment/prometheus -n automind
```

## Maintenance

### Regular Tasks

1. **Security Updates**
   - Update base images monthly
   - Apply security patches
   - Rotate secrets quarterly

2. **Performance Monitoring**
   - Review metrics weekly
   - Optimize resource allocation
   - Plan capacity upgrades

3. **Backup Verification**
   - Test backup restoration monthly
   - Verify backup integrity
   - Update disaster recovery procedures

### Upgrade Procedures

1. **Application Updates**
   ```bash
   # Update image tags
   kubectl set image deployment/automind-api automind-api=automind-api:v2.0.0 -n automind
   
   # Monitor rollout
   kubectl rollout status deployment/automind-api -n automind
   
   # Rollback if needed
   kubectl rollout undo deployment/automind-api -n automind
   ```

2. **Kubernetes Upgrades**
   ```bash
   # Plan upgrade
   terraform plan -var kubernetes_version="1.29"
   
   # Apply upgrade
   terraform apply -var kubernetes_version="1.29"
   ```

## Support and Documentation

- **API Documentation**: https://api.automind.com/docs
- **Monitoring Dashboards**: https://grafana.automind.com
- **Issue Tracking**: GitHub Issues
- **Team Communication**: Slack #automind-ops

For additional support, contact the platform team or create an issue in the GitHub repository.