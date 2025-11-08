# AutoMind Operations Runbook

This runbook provides operational procedures for managing the AutoMind system in production.

## Table of Contents

1. [Emergency Contacts](#emergency-contacts)
2. [System Overview](#system-overview)
3. [Incident Response](#incident-response)
4. [Common Issues and Solutions](#common-issues-and-solutions)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Maintenance Procedures](#maintenance-procedures)
7. [Escalation Procedures](#escalation-procedures)

## Emergency Contacts

### On-Call Rotation

| Role | Primary | Secondary | Escalation |
|------|---------|-----------|------------|
| Platform Engineer | @john.doe | @jane.smith | @tech.lead |
| Database Administrator | @db.admin | @senior.dba | @data.lead |
| Security Engineer | @sec.engineer | @security.lead | @ciso |
| Product Owner | @product.owner | @product.manager | @vp.product |

### Communication Channels

- **Critical Incidents**: #incident-response
- **General Operations**: #automind-ops
- **Database Issues**: #database-alerts
- **Security Issues**: #security-alerts

### External Contacts

- **AWS Support**: Enterprise Support Case
- **Monitoring Vendor**: support@monitoring-vendor.com
- **CDN Provider**: support@cdn-provider.com

## System Overview

### Architecture Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   API Gateway   │────│   AutoMind API  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐             │
                       │  Celery Workers │─────────────┤
                       └─────────────────┘             │
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │────│      Redis      │────│   File Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Metrics

- **SLA Target**: 99.9% uptime
- **Response Time**: < 200ms (95th percentile)
- **Error Rate**: < 0.1%
- **Data Processing**: 10,000 vehicles/minute

### Dependencies

- **AWS Services**: EKS, RDS, ElastiCache, S3, Route53
- **External APIs**: Vehicle manufacturer APIs
- **Third-party Services**: Monitoring, logging, alerting

## Incident Response

### Severity Levels

#### Severity 1 (Critical)
- **Definition**: Complete service outage or data loss
- **Response Time**: 15 minutes
- **Examples**: API completely down, database corruption, security breach

#### Severity 2 (High)
- **Definition**: Significant service degradation
- **Response Time**: 30 minutes
- **Examples**: High error rates, slow response times, partial outage

#### Severity 3 (Medium)
- **Definition**: Minor service impact
- **Response Time**: 2 hours
- **Examples**: Non-critical feature issues, monitoring alerts

#### Severity 4 (Low)
- **Definition**: No immediate service impact
- **Response Time**: Next business day
- **Examples**: Documentation updates, minor bugs

### Incident Response Process

#### 1. Detection and Alerting

```bash
# Check alert source
# - Monitoring dashboard
# - User reports
# - Automated alerts

# Verify incident
curl -I https://api.automind.com/health
kubectl get pods -n automind
```

#### 2. Initial Response (First 5 minutes)

```bash
# Acknowledge alert
# Post in #incident-response channel
# Assign incident commander
# Create incident ticket

# Quick assessment
kubectl get pods -n automind --sort-by=.status.startTime
kubectl get events -n automind --sort-by=.firstTimestamp
```

#### 3. Investigation and Diagnosis

```bash
# Check system status
kubectl top pods -n automind
kubectl get hpa -n automind

# Review logs
kubectl logs -f deployment/automind-api -n automind --tail=100
kubectl logs -f deployment/celery-worker -n automind --tail=100

# Check database
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT version();"

# Check Redis
kubectl exec -it deployment/redis -n automind -- redis-cli info
```

#### 4. Mitigation and Resolution

```bash
# Common mitigation steps
kubectl scale deployment/automind-api --replicas=5 -n automind
kubectl rollout restart deployment/automind-api -n automind
kubectl rollout undo deployment/automind-api -n automind
```

#### 5. Post-Incident Activities

- Update incident ticket with resolution
- Conduct post-mortem meeting
- Document lessons learned
- Implement preventive measures

## Common Issues and Solutions

### API Service Issues

#### Issue: High Response Times

**Symptoms:**
- Response time > 500ms
- High CPU usage on API pods
- Queue backlog in Celery

**Investigation:**
```bash
# Check API pod resources
kubectl top pods -n automind | grep automind-api

# Check database connections
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

**Resolution:**
```bash
# Scale API pods
kubectl scale deployment/automind-api --replicas=10 -n automind

# Restart API service
kubectl rollout restart deployment/automind-api -n automind

# Clear Redis cache if needed
kubectl exec -it deployment/redis -n automind -- redis-cli flushdb
```

#### Issue: API Pods Crashing

**Symptoms:**
- CrashLoopBackOff status
- High restart count
- Memory or CPU limits exceeded

**Investigation:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n automind

# Check resource limits
kubectl get pod <pod-name> -n automind -o yaml | grep -A 10 resources

# Check logs
kubectl logs <pod-name> -n automind --previous
```

**Resolution:**
```bash
# Increase resource limits
kubectl patch deployment automind-api -n automind -p '{"spec":{"template":{"spec":{"containers":[{"name":"automind-api","resources":{"limits":{"memory":"2Gi","cpu":"1000m"}}}]}}}}'

# Rollback to previous version
kubectl rollout undo deployment/automind-api -n automind
```

### Database Issues

#### Issue: High Database Connections

**Symptoms:**
- Connection pool exhausted
- "too many connections" errors
- Slow query performance

**Investigation:**
```bash
# Check active connections
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Check connection sources
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT client_addr, count(*) FROM pg_stat_activity GROUP BY client_addr;"
```

**Resolution:**
```bash
# Kill idle connections
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '5 minutes';"

# Restart API pods to reset connection pools
kubectl rollout restart deployment/automind-api -n automind
```

#### Issue: Database Performance Issues

**Symptoms:**
- Slow query execution
- High I/O wait
- Lock contention

**Investigation:**
```bash
# Check running queries
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"

# Check locks
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT * FROM pg_locks WHERE NOT granted;"
```

**Resolution:**
```bash
# Kill long-running queries
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT pg_terminate_backend(<pid>);"

# Analyze and optimize queries
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "ANALYZE;"
```

### Redis Issues

#### Issue: High Memory Usage

**Symptoms:**
- Memory usage > 80%
- Eviction of keys
- Slow Redis operations

**Investigation:**
```bash
# Check memory usage
kubectl exec -it deployment/redis -n automind -- redis-cli info memory

# Check key distribution
kubectl exec -it deployment/redis -n automind -- redis-cli --bigkeys
```

**Resolution:**
```bash
# Clear expired keys
kubectl exec -it deployment/redis -n automind -- redis-cli eval "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "*expired*"

# Increase memory limit or scale Redis
kubectl patch deployment redis -n automind -p '{"spec":{"template":{"spec":{"containers":[{"name":"redis","resources":{"limits":{"memory":"4Gi"}}}]}}}}'
```

### Kubernetes Issues

#### Issue: Node Resource Exhaustion

**Symptoms:**
- Pods in Pending state
- Node NotReady status
- High resource utilization

**Investigation:**
```bash
# Check node status
kubectl get nodes
kubectl describe node <node-name>

# Check resource usage
kubectl top nodes
kubectl top pods -n automind
```

**Resolution:**
```bash
# Drain and cordon node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Scale cluster (if using cluster autoscaler)
kubectl scale deployment cluster-autoscaler --replicas=1 -n kube-system

# Manual node addition (if needed)
# Add nodes through AWS console or Terraform
```

## Monitoring and Alerting

### Key Dashboards

1. **System Overview**: https://grafana.automind.com/d/system-overview
2. **API Performance**: https://grafana.automind.com/d/api-performance
3. **Database Metrics**: https://grafana.automind.com/d/database-metrics
4. **Infrastructure**: https://grafana.automind.com/d/infrastructure

### Critical Alerts

#### API Down Alert

**Alert**: `AutoMindAPIDown`
**Threshold**: API unavailable for > 1 minute
**Action**:
```bash
# Check API pods
kubectl get pods -n automind | grep automind-api

# Check service and ingress
kubectl get service automind-api -n automind
kubectl get ingress automind-ingress -n automind

# Check load balancer
aws elbv2 describe-load-balancers --names automind-prod-alb
```

#### High Error Rate Alert

**Alert**: `HighErrorRate`
**Threshold**: Error rate > 5% for 5 minutes
**Action**:
```bash
# Check recent deployments
kubectl rollout history deployment/automind-api -n automind

# Check logs for errors
kubectl logs -f deployment/automind-api -n automind | grep ERROR

# Consider rollback
kubectl rollout undo deployment/automind-api -n automind
```

#### Database Connection Alert

**Alert**: `DatabaseHighConnections`
**Threshold**: Connections > 80% of max for 5 minutes
**Action**:
```bash
# Check connection count
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
kubectl exec -it deployment/postgres -n automind -- psql -U automind_user -d automind_db -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '10 minutes';"
```

### Alert Escalation Matrix

| Alert Severity | Initial Response | Escalation (30 min) | Escalation (60 min) |
|----------------|------------------|---------------------|---------------------|
| Critical | On-call engineer | Team lead | Engineering manager |
| High | On-call engineer | Team lead | - |
| Medium | On-call engineer | - | - |
| Low | Next business day | - | - |

## Maintenance Procedures

### Scheduled Maintenance

#### Weekly Maintenance Window
- **Time**: Sunday 2:00 AM - 4:00 AM UTC
- **Duration**: 2 hours maximum
- **Activities**: Security updates, minor deployments

#### Monthly Maintenance Window
- **Time**: First Sunday of month 2:00 AM - 6:00 AM UTC
- **Duration**: 4 hours maximum
- **Activities**: Major updates, infrastructure changes

### Pre-Maintenance Checklist

```bash
# 1. Notify stakeholders
# Post in #automind-ops channel
# Update status page

# 2. Backup critical data
kubectl exec -it deployment/postgres -n automind -- pg_dump -U automind_user automind_db > backup_$(date +%Y%m%d).sql

# 3. Scale down non-essential services
kubectl scale deployment/celery-worker --replicas=1 -n automind

# 4. Verify monitoring
curl https://grafana.automind.com/api/health
```

### Post-Maintenance Checklist

```bash
# 1. Verify all services
kubectl get pods -n automind
curl https://api.automind.com/health

# 2. Check monitoring dashboards
# Verify metrics are being collected
# Check for any new alerts

# 3. Scale services back up
kubectl scale deployment/celery-worker --replicas=3 -n automind

# 4. Update documentation
# Record any changes made
# Update runbook if needed

# 5. Notify completion
# Post in #automind-ops channel
# Update status page
```

### Emergency Maintenance

#### Immediate Security Patch

```bash
# 1. Assess impact
# Determine affected components
# Estimate downtime

# 2. Prepare patch
# Build new container images
# Test in staging environment

# 3. Deploy patch
kubectl set image deployment/automind-api automind-api=automind-api:security-patch -n automind

# 4. Verify deployment
kubectl rollout status deployment/automind-api -n automind
curl https://api.automind.com/health
```

## Escalation Procedures

### When to Escalate

1. **Severity 1 incidents** not resolved within 30 minutes
2. **Multiple component failures** indicating systemic issues
3. **Security incidents** requiring specialized expertise
4. **Data integrity issues** requiring DBA intervention

### Escalation Contacts

#### Technical Escalation
1. **Level 1**: On-call engineer
2. **Level 2**: Team lead or senior engineer
3. **Level 3**: Engineering manager
4. **Level 4**: CTO or VP Engineering

#### Business Escalation
1. **Level 1**: Product owner
2. **Level 2**: Product manager
3. **Level 3**: VP Product
4. **Level 4**: CEO

### External Escalation

#### AWS Support
```bash
# Create support case
aws support create-case \
  --subject "AutoMind Production Issue" \
  --service-code "amazon-eks" \
  --severity-code "high" \
  --category-code "performance" \
  --communication-body "Description of issue"
```

#### Vendor Support
- **Monitoring**: Create ticket via vendor portal
- **Security**: Contact security vendor hotline
- **CDN**: Use vendor emergency contact

## Documentation and Knowledge Base

### Internal Documentation
- **Architecture Diagrams**: Confluence/Wiki
- **API Documentation**: https://api.automind.com/docs
- **Database Schema**: Database documentation tool

### External Resources
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Terraform Documentation**: https://www.terraform.io/docs/

### Training Resources
- **New Team Member Onboarding**: Internal training program
- **Incident Response Training**: Quarterly training sessions
- **Technology Updates**: Monthly tech talks

## Continuous Improvement

### Post-Incident Reviews
- **Timeline**: Within 48 hours of incident resolution
- **Participants**: Incident responders, stakeholders
- **Deliverables**: Action items, process improvements

### Metrics and KPIs
- **MTTR** (Mean Time To Recovery): Target < 30 minutes
- **MTBF** (Mean Time Between Failures): Target > 720 hours
- **Alert Accuracy**: Target > 95% (no false positives)

### Regular Reviews
- **Weekly**: Operations metrics review
- **Monthly**: Runbook updates and improvements
- **Quarterly**: Disaster recovery testing

---

**Last Updated**: $(date)
**Version**: 1.0
**Next Review**: $(date -d "+3 months")