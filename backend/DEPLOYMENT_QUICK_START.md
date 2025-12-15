# Chorus Agent Conflict Predictor - Quick Start Deployment Guide

This guide provides quick deployment instructions for different environments.

## 🚀 Quick Start Options

### Option 1: Docker Development (Recommended for Testing)

```bash
# 1. Clone and navigate to backend directory
cd backend

# 2. Copy environment configuration
cp .env.example .env

# 3. Edit configuration (add your Gemini API key)
nano .env

# 4. Deploy with Docker
./deploy-docker.sh dev

# 5. Validate deployment
./validate-deployment.sh

# Access:
# - Dashboard: http://localhost:3000
# - API: http://localhost:8000
# - Redis: localhost:6379
```

### Option 2: Docker Production

```bash
# 1. Setup production configuration
cp .env.production .env
nano .env  # Add your production API keys

# 2. Deploy production environment
./deploy-docker.sh prod

# 3. Validate deployment
./validate-deployment.sh --backend-url http://localhost:8000

# Access:
# - Application: http://localhost
# - API: http://localhost:8000
```

### Option 3: Native Linux Deployment

```bash
# 1. Run as root
sudo ./deploy.sh deploy

# 2. Configure environment
sudo nano /opt/chorus-agent-predictor/backend/.env

# 3. Start service
sudo systemctl start chorus-agent-predictor

# 4. Validate
./validate-deployment.sh
```

### Option 4: Kubernetes Production

```bash
# 1. Update k8s-deployment.yml with your configuration
nano k8s-deployment.yml

# 2. Deploy to Kubernetes
kubectl apply -f k8s-deployment.yml

# 3. Check status
kubectl get pods -n chorus-agent-predictor

# 4. Access via ingress (configure your domain)
# https://chorus.yourdomain.com
```

## 📋 Prerequisites Checklist

- [ ] **Gemini API Key** (Required)
  - Get from: https://makersuite.google.com/app/apikey
  - Set in: `CHORUS_GEMINI_API_KEY`

- [ ] **Redis Server** (Required for persistence)
  - Included in Docker deployments
  - For native: `sudo apt install redis-server`

- [ ] **Datadog Keys** (Optional, recommended for production)
  - API Key: `CHORUS_DATADOG_API_KEY`
  - App Key: `CHORUS_DATADOG_APP_KEY`

- [ ] **Node.js 18+** (Required for dashboard)
  - Included in Docker deployments
  - For native: `curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -`

## 🔧 Configuration Templates

### Minimal Configuration (.env)
```bash
CHORUS_ENVIRONMENT=development
CHORUS_GEMINI_API_KEY=your_gemini_api_key_here
CHORUS_REDIS_HOST=localhost
CHORUS_REDIS_PORT=6379
```

### Production Configuration (.env)
```bash
CHORUS_ENVIRONMENT=production
CHORUS_DEBUG=false
CHORUS_GEMINI_API_KEY=your_production_gemini_key
CHORUS_REDIS_HOST=your_redis_host
CHORUS_REDIS_PASSWORD=your_secure_redis_password
CHORUS_DATADOG_ENABLED=true
CHORUS_DATADOG_API_KEY=your_datadog_api_key
CHORUS_DATADOG_APP_KEY=your_datadog_app_key
CHORUS_LOG_LEVEL=INFO
CHORUS_API_WORKERS=4
```

## 🏥 Health Checks

### Quick Health Check
```bash
# Run validation script
./validate-deployment.sh

# Manual checks
curl http://localhost:8000/health
curl http://localhost:3000  # Development dashboard
redis-cli ping
```

### Service Status
```bash
# Docker
./deploy-docker.sh status

# Native Linux
sudo systemctl status chorus-agent-predictor

# Kubernetes
kubectl get pods -n chorus-agent-predictor
```

## 📊 Monitoring Access

### Dashboard URLs
- **Development**: http://localhost:3000
- **Production**: http://localhost or https://your-domain.com
- **API Documentation**: http://localhost:8000/docs

### Log Access
```bash
# Docker
./deploy-docker.sh logs

# Native Linux
sudo journalctl -u chorus-agent-predictor -f

# Kubernetes
kubectl logs -f deployment/backend-deployment -n chorus-agent-predictor
```

## 🔍 Troubleshooting

### Common Issues

1. **"Gemini API key invalid"**
   ```bash
   # Check API key format
   echo $CHORUS_GEMINI_API_KEY
   # Should start with "AI..." and be ~40 characters
   ```

2. **"Redis connection failed"**
   ```bash
   # Check Redis status
   redis-cli ping
   # Should return "PONG"
   ```

3. **"Dashboard not loading"**
   ```bash
   # Check if Node.js build completed
   ./deploy-docker.sh logs dashboard
   ```

4. **"Port already in use"**
   ```bash
   # Stop existing services
   ./deploy-docker.sh stop
   # Or change ports in docker-compose.yml
   ```

### Debug Mode
```bash
# Enable debug logging
export CHORUS_DEBUG=true
export CHORUS_LOG_LEVEL=DEBUG

# Run with debug output
./deploy-docker.sh dev
```

## 🛠 Management Commands

### Docker Management
```bash
./deploy-docker.sh dev      # Start development
./deploy-docker.sh prod     # Start production
./deploy-docker.sh stop     # Stop all services
./deploy-docker.sh logs     # View logs
./deploy-docker.sh health   # Health check
./deploy-docker.sh cleanup  # Remove everything
```

### Native Linux Management
```bash
sudo systemctl start chorus-agent-predictor    # Start
sudo systemctl stop chorus-agent-predictor     # Stop
sudo systemctl restart chorus-agent-predictor  # Restart
sudo systemctl status chorus-agent-predictor   # Status
sudo journalctl -u chorus-agent-predictor -f   # Logs
```

## 📈 Scaling

### Docker Scaling
```bash
# Scale backend replicas
docker-compose up -d --scale backend=3

# Production with load balancer
docker-compose -f docker-compose.prod.yml up -d --scale backend=4
```

### Kubernetes Scaling
```bash
# Manual scaling
kubectl scale deployment backend-deployment --replicas=5 -n chorus-agent-predictor

# Auto-scaling is configured via HPA in k8s-deployment.yml
```

## 🔒 Security Checklist

- [ ] Change default Redis password
- [ ] Use HTTPS in production (configure nginx/ingress)
- [ ] Restrict API access with authentication
- [ ] Set up firewall rules
- [ ] Use secrets management for API keys
- [ ] Enable audit logging
- [ ] Regular security updates

## 📞 Support

If you encounter issues:

1. **Run validation**: `./validate-deployment.sh`
2. **Check logs**: `./deploy-docker.sh logs` or `journalctl -u chorus-agent-predictor`
3. **Verify configuration**: Ensure all required environment variables are set
4. **Check resources**: Ensure sufficient CPU, memory, and disk space
5. **Network connectivity**: Verify Redis, Datadog, and Gemini API access

For additional help, check the full [DEPLOYMENT.md](DEPLOYMENT.md) guide.