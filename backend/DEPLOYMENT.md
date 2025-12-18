# Chorus Agent Conflict Predictor - Deployment Guide

This guide covers deployment options for the Chorus Agent Conflict Predictor system with observability and trust layer enhancements.

## Prerequisites

- Python 3.9 or higher
- Redis server (for persistent trust storage)
- Node.js 18+ and npm (for React dashboard)
- Valid Gemini API key
- (Optional) Datadog API keys for observability
- (Optional) Docker and Docker Compose for containerized deployment
- (Optional) Kubernetes cluster for production deployment

## Configuration

1. Copy the appropriate configuration template:
   ```bash
   # For development
   cp .env.example .env
   
   # For production
   cp .env.production .env
   
   # For staging
   cp .env.staging .env  # if available
   ```

2. Edit `.env` with your configuration. **Required settings:**
   ```bash
   # Environment Configuration
   CHORUS_ENVIRONMENT=production  # or development/staging
   CHORUS_DEBUG=false
   
   # Google Gemini API (REQUIRED)
   CHORUS_GEMINI_API_KEY=your_actual_gemini_api_key_here
   CHORUS_GEMINI_MODEL=gemini-3-pro-preview
   
   # Redis Configuration (REQUIRED for persistence)
   CHORUS_REDIS_HOST=your_redis_host
   CHORUS_REDIS_PORT=6379
   CHORUS_REDIS_PASSWORD=your_secure_redis_password
   CHORUS_REDIS_DB=0
   ```

3. **Optional but recommended for production:**
   ```bash
   # Datadog Observability
   CHORUS_DATADOG_ENABLED=true
   CHORUS_DATADOG_API_KEY=your_datadog_api_key
   CHORUS_DATADOG_APP_KEY=your_datadog_app_key
   CHORUS_DATADOG_SITE=datadoghq.com
   
   # ElevenLabs Voice Alerts
   CHORUS_ELEVENLABS_ENABLED=true
   CHORUS_ELEVENLABS_API_KEY=your_elevenlabs_key
   
   # Confluent Kafka Event Streaming
   KAFKA_ENABLED=true
   KAFKA_BOOTSTRAP_SERVERS=your-kafka-cluster:9092
   KAFKA_SASL_USERNAME=your_kafka_username
   KAFKA_SASL_PASSWORD=your_kafka_password
   ```

4. **Validate configuration:**
   ```bash
   # Comprehensive configuration validation
   python start_system.py validate-config
   
   # Alternative validation method
   python -m src.config_validator
   
   # Validate with specific environment file
   python -m src.config_validator --env-file .env.production
   ```

5. **Test system health:**
   ```bash
   # Run health checks
   python start_system.py health-check
   
   # Test individual components
   python -c "from src.system_lifecycle import lifecycle_manager; print(lifecycle_manager._run_dependency_checks())"
   ```

## Deployment Options

### 1. Local Development

For development and testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (if not running)
redis-server

# Run simulation mode
python start_system.py simulation

# Or run API mode
python start_system.py api
```

### 2. Docker Deployment

#### Development Environment

For development with hot reloading:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Production Environment

For production deployment with optimized builds:

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

#### Quick Docker Deployment

Use the deployment script for easier management:

```bash
# Deploy development environment
./deploy-docker.sh dev

# Deploy production environment
./deploy-docker.sh prod

# Show service status
./deploy-docker.sh status

# View logs
./deploy-docker.sh logs

# Run health check
./deploy-docker.sh health

# Stop all services
./deploy-docker.sh stop

# Clean up everything
./deploy-docker.sh cleanup
```

Services included:
- `backend`: Main API and simulation service (port 8000)
- `dashboard`: React web dashboard (port 3000 dev, port 80 prod)
- `redis`: Redis database with persistence (port 6379)
- `nginx`: Reverse proxy for production (port 443)

### 3. Production Deployment (Linux)

For production deployment on Linux with systemd:

```bash
# Run deployment script as root
sudo ./deploy.sh deploy

# Edit configuration
sudo nano /opt/chorus-agent-predictor/backend/.env

# Start service
sudo systemctl start chorus-agent-predictor

# Enable auto-start
sudo systemctl enable chorus-agent-predictor

# Check status
sudo systemctl status chorus-agent-predictor

# View logs
sudo journalctl -u chorus-agent-predictor -f
```

The deployment script now includes:
- Redis server installation and configuration
- Nginx setup for dashboard hosting
- Node.js and npm installation for dashboard build
- Automatic dashboard build and deployment
- Enhanced service configuration

### 4. Kubernetes Deployment

For production Kubernetes deployment:

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s-deployment.yml

# Check deployment status
kubectl get pods -n chorus-agent-predictor

# View logs
kubectl logs -f deployment/backend-deployment -n chorus-agent-predictor

# Access dashboard (after setting up ingress)
# https://chorus.yourdomain.com
```

Features included:
- Horizontal Pod Autoscaling (HPA)
- Persistent storage for Redis
- TLS termination with cert-manager
- Resource limits and health checks
- Multi-replica deployment for high availability

## System Management

### Health Checks

Check system health:
```bash
# Comprehensive health check
python start_system.py health-check

# Deployment validation script
./validate-deployment.sh

# API health check (if API mode is running)
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/system/health

# Dashboard health check
curl http://localhost:3000  # Development
curl http://localhost       # Production

# Redis connectivity check
redis-cli -h $CHORUS_REDIS_HOST -p $CHORUS_REDIS_PORT ping

# Docker health check
./deploy-docker.sh health
```

### Configuration Validation

Validate configuration before deployment:
```bash
# Primary validation method
python start_system.py validate-config

# Alternative validation with detailed output
python -m src.config_validator

# Validate specific environment file
python -m src.config_validator --env-file .env.production

# Test configuration loading
python -c "from src.config import load_settings; settings = load_settings(); print(settings.get_config_summary())"
```

### System Status

Get detailed system status:
```bash
# System lifecycle status
python -c "from src.system_lifecycle import get_system_status; print(get_system_status())"

# API status (if API mode is running)
curl http://localhost:8000/api/v1/system/status

# Health monitoring status
python -c "from src.system_health import health_monitor; print(health_monitor.get_health_status())"

# Docker service status
./deploy-docker.sh status
```

## Service Management

### Systemd Service (Linux)

```bash
# Start service
sudo systemctl start chorus-agent-predictor

# Stop service
sudo systemctl stop chorus-agent-predictor

# Restart service
sudo systemctl restart chorus-agent-predictor

# Check status
sudo systemctl status chorus-agent-predictor

# View logs
sudo journalctl -u chorus-agent-predictor -f

# Enable auto-start on boot
sudo systemctl enable chorus-agent-predictor

# Disable auto-start
sudo systemctl disable chorus-agent-predictor
```

### Docker Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d chorus-agent-predictor

# Stop all services
docker-compose down

# View logs
docker-compose logs -f chorus-agent-predictor

# Restart service
docker-compose restart chorus-agent-predictor

# Scale API service
docker-compose up -d --scale chorus-api=3
```

## Monitoring and Logging

### Log Files

- **Development**: Logs to console
- **Production**: Logs to systemd journal and optionally to file
- **Docker**: Logs to Docker logging driver

### Log Levels

Configure log level in `.env`:
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Structured Logging

Enable structured JSON logging:
```bash
LOG_STRUCTURED=true
```

### Health Monitoring

The system includes built-in health monitoring:

- **Redis connection**: Checks Redis connectivity
- **Gemini API**: Validates API access
- **System resources**: Monitors CPU and memory usage

Health checks run automatically every 30 seconds and can be triggered manually:
```bash
# Send SIGUSR1 to trigger health check
sudo kill -USR1 $(pgrep -f chorus-agent-predictor)
```

## Troubleshooting

### Common Issues

1. **Configuration validation fails**
   - Check `.env` file exists and has correct values
   - Ensure Gemini API key is valid
   - Verify Redis is running and accessible

2. **Redis connection fails**
   - Check Redis server is running: `redis-cli ping`
   - Verify Redis host/port in configuration
   - Check network connectivity

3. **Gemini API errors**
   - Verify API key is correct and active
   - Check internet connectivity
   - Review API quotas and limits

4. **Permission errors (Linux)**
   - Ensure `chorus` user has correct permissions
   - Check file ownership: `chown -R chorus:chorus /opt/chorus-agent-predictor`

### Debug Mode

Enable debug mode for detailed logging:
```bash
# Command line
python start_system.py --debug simulation

# Environment variable
DEBUG=true python start_system.py simulation
```

### Log Analysis

View recent logs:
```bash
# Systemd
sudo journalctl -u chorus-agent-predictor --since "1 hour ago"

# Docker
docker-compose logs --since 1h chorus-agent-predictor
```

Filter logs by level:
```bash
# Error logs only
sudo journalctl -u chorus-agent-predictor -p err

# Docker with grep
docker-compose logs chorus-agent-predictor | grep ERROR
```

## Security Considerations

### File Permissions

- Configuration files should be readable only by the application user
- Log files should have appropriate permissions
- API keys should never be logged or exposed

### Network Security

- API service should be behind a reverse proxy in production
- Use TLS/SSL for external communications
- Restrict Redis access to localhost or private network

### Environment Variables

Sensitive configuration should use environment variables:
```bash
# Good
GEMINI_API_KEY=actual_key_here

# Bad (don't commit to version control)
GEMINI_API_KEY=your_gemini_api_key_here
```

## Performance Tuning

### Resource Limits

Configure resource limits in systemd service:
```ini
[Service]
MemoryMax=1G
CPUQuota=200%
```

### Redis Optimization

For high-throughput scenarios:
```bash
# Redis configuration
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Agent Simulation

Adjust agent count based on system resources:
```bash
MIN_AGENTS=5
MAX_AGENTS=10  # Increase for more load testing
```

## Backup and Recovery

### Configuration Backup

Backup configuration files:
```bash
sudo cp /opt/chorus-agent-predictor/backend/.env /backup/chorus-config-$(date +%Y%m%d).env
```

### Redis Data Backup

Backup Redis data:
```bash
# Create backup
redis-cli BGSAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb
```

### Service Recovery

Automatic restart is configured in systemd service:
```ini
[Service]
Restart=always
RestartSec=10
```

## Uninstallation

### Remove Docker Deployment

```bash
docker-compose down -v
docker rmi $(docker images -q chorus*)
```

### Remove Production Deployment

```bash
sudo ./deploy.sh uninstall
```

This will:
- Stop and disable the systemd service
- Remove application files
- Remove the application user
- Clean up systemd configuration

## Support

For issues and support:
1. Check logs for error messages
2. Validate configuration
3. Run health checks
4. Review this deployment guide
5. Check system resources and dependencies