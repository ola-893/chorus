# Deployment Checklist - Chorus Agent Conflict Predictor

Use this checklist to ensure a successful deployment of the observability and trust layer.

## Pre-Deployment Checklist

### 📋 Prerequisites
- [ ] **Python 3.9+** installed
- [ ] **Node.js 18+** and npm installed (for dashboard)
- [ ] **Redis server** available (local or remote)
- [ ] **Docker & Docker Compose** installed (for containerized deployment)
- [ ] **Valid Gemini API key** obtained from Google AI Studio
- [ ] **Datadog account** and API keys (optional, for observability)
- [ ] **Sufficient system resources** (2GB RAM minimum, 4GB recommended)

### 🔑 API Keys and Credentials
- [ ] **Gemini API Key** - Required for conflict prediction
  - Format: Starts with "AI..." (~40 characters)
  - Test: `curl -H "Authorization: Bearer YOUR_KEY" https://generativelanguage.googleapis.com/v1/models`
- [ ] **Datadog API Key** - Optional for observability
- [ ] **Datadog App Key** - Optional for observability  
- [ ] **Redis Password** - Recommended for production
- [ ] **ElevenLabs API Key** - Optional for voice alerts

### 🌐 Network and Infrastructure
- [ ] **Ports available**: 8000 (API), 3000 (dev dashboard), 80/443 (prod dashboard), 6379 (Redis)
- [ ] **Firewall rules** configured for required ports
- [ ] **DNS configuration** (for production domain)
- [ ] **SSL certificates** (for HTTPS in production)
- [ ] **Load balancer** configured (for multi-instance deployment)

## Configuration Checklist

### 📝 Environment Configuration
- [ ] **Copy configuration template**
  ```bash
  cp .env.example .env  # Development
  cp .env.production .env  # Production
  cp .env.staging .env  # Staging
  ```

- [ ] **Required environment variables set**:
  - [ ] `CHORUS_GEMINI_API_KEY`
  - [ ] `CHORUS_REDIS_HOST`
  - [ ] `CHORUS_REDIS_PORT`
  - [ ] `CHORUS_ENVIRONMENT` (development/staging/production)

- [ ] **Optional but recommended variables**:
  - [ ] `CHORUS_DATADOG_ENABLED=true`
  - [ ] `CHORUS_DATADOG_API_KEY`
  - [ ] `CHORUS_DATADOG_APP_KEY`
  - [ ] `CHORUS_REDIS_PASSWORD`

- [ ] **Configuration validation passed**
  ```bash
  python start_system.py validate-config
  ```

### 🔧 Service Configuration
- [ ] **Redis configuration** optimized for workload
- [ ] **Log levels** appropriate for environment
- [ ] **Resource limits** configured (memory, CPU)
- [ ] **Health check intervals** configured
- [ ] **Backup and retention policies** defined

## Deployment Execution

### 🐳 Docker Deployment (Recommended)
- [ ] **Development deployment**
  ```bash
  ./deploy-docker.sh dev
  ```
- [ ] **Production deployment**
  ```bash
  ./deploy-docker.sh prod
  ```
- [ ] **Services started successfully**
  ```bash
  ./deploy-docker.sh status
  ```

### 🖥️ Native Linux Deployment
- [ ] **System dependencies installed**
- [ ] **Application deployed**
  ```bash
  sudo ./deploy.sh deploy
  ```
- [ ] **Service enabled and started**
  ```bash
  sudo systemctl enable chorus-agent-predictor
  sudo systemctl start chorus-agent-predictor
  ```

### ☸️ Kubernetes Deployment
- [ ] **Namespace created**
- [ ] **Secrets configured** (API keys)
- [ ] **ConfigMaps applied**
- [ ] **Deployments applied**
  ```bash
  kubectl apply -f k8s-deployment.yml
  ```
- [ ] **Ingress configured** (for external access)

## Post-Deployment Validation

### 🏥 Health Checks
- [ ] **Run deployment validation**
  ```bash
  ./validate-deployment.sh
  ```
- [ ] **Backend API responding**
  ```bash
  curl http://localhost:8000/health
  ```
- [ ] **Dashboard accessible**
  - Development: http://localhost:3000
  - Production: http://localhost or https://your-domain.com
- [ ] **Redis connectivity verified**
  ```bash
  redis-cli ping
  ```

### 📊 Functional Testing
- [ ] **Agent simulation running**
- [ ] **Trust scores updating**
- [ ] **Dashboard showing real-time data**
- [ ] **API endpoints responding correctly**
- [ ] **WebSocket connections working**
- [ ] **Datadog metrics flowing** (if enabled)

### 🔍 Monitoring Setup
- [ ] **Log aggregation working**
- [ ] **Metrics collection active**
- [ ] **Alerting configured** (Datadog)
- [ ] **Dashboard monitoring setup**
- [ ] **Health check monitoring**
- [ ] **Performance baselines established**

## Security Validation

### 🔒 Security Checklist
- [ ] **API keys secured** (not in logs/version control)
- [ ] **Redis password set** (production)
- [ ] **HTTPS enabled** (production)
- [ ] **Firewall rules applied**
- [ ] **User permissions restricted**
- [ ] **Log access controlled**
- [ ] **Backup encryption enabled**

### 🛡️ Access Control
- [ ] **API authentication configured**
- [ ] **Dashboard access restricted** (if needed)
- [ ] **Admin access limited**
- [ ] **Service accounts configured**
- [ ] **Network segmentation applied**

## Performance Validation

### ⚡ Performance Testing
- [ ] **Load testing completed**
- [ ] **Memory usage within limits**
- [ ] **CPU usage acceptable**
- [ ] **Response times acceptable**
  - API endpoints: < 200ms
  - Dashboard loading: < 3s
  - WebSocket latency: < 100ms
- [ ] **Concurrent user testing**
- [ ] **Stress testing passed**

### 📈 Scaling Verification
- [ ] **Horizontal scaling tested** (if applicable)
- [ ] **Auto-scaling configured** (Kubernetes HPA)
- [ ] **Load balancer tested**
- [ ] **Database connection pooling**
- [ ] **Resource monitoring active**

## Backup and Recovery

### 💾 Backup Procedures
- [ ] **Configuration backup automated**
- [ ] **Redis data backup scheduled**
- [ ] **Log rotation configured**
- [ ] **Backup testing completed**
- [ ] **Recovery procedures documented**
- [ ] **Disaster recovery plan ready**

### 🔄 Recovery Testing
- [ ] **Service restart tested**
- [ ] **Configuration recovery tested**
- [ ] **Data recovery tested**
- [ ] **Failover procedures tested**
- [ ] **Rollback procedures verified**

## Documentation and Handover

### 📚 Documentation Complete
- [ ] **Deployment guide updated**
- [ ] **Configuration documented**
- [ ] **Troubleshooting guide available**
- [ ] **Monitoring runbooks created**
- [ ] **Emergency procedures documented**
- [ ] **Contact information updated**

### 👥 Team Handover
- [ ] **Operations team trained**
- [ ] **Access credentials shared securely**
- [ ] **Monitoring alerts configured**
- [ ] **Escalation procedures defined**
- [ ] **Maintenance windows scheduled**
- [ ] **Support contacts established**

## Final Sign-off

### ✅ Deployment Approval
- [ ] **All critical tests passed**
- [ ] **Performance requirements met**
- [ ] **Security requirements satisfied**
- [ ] **Monitoring and alerting active**
- [ ] **Documentation complete**
- [ ] **Team ready for operations**

### 📝 Deployment Record
- **Deployment Date**: _______________
- **Environment**: _______________
- **Version**: _______________
- **Deployed by**: _______________
- **Approved by**: _______________
- **Notes**: _______________

---

## Quick Commands Reference

```bash
# Validation
./validate-deployment.sh

# Docker Management
./deploy-docker.sh {dev|prod|stop|logs|health|status}

# Native Service Management
sudo systemctl {start|stop|restart|status} chorus-agent-predictor
sudo journalctl -u chorus-agent-predictor -f

# Configuration Testing
python start_system.py validate-config
python start_system.py health-check

# Health Checks
curl http://localhost:8000/health
redis-cli ping
```

## Emergency Contacts

- **Primary Contact**: _______________
- **Secondary Contact**: _______________
- **Escalation**: _______________
- **Vendor Support**: _______________