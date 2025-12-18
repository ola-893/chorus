# Deployment Troubleshooting Guide

This guide helps diagnose and resolve common deployment issues with the Chorus Agent Conflict Predictor system.

## Quick Diagnostic Commands

Run these commands first to get an overview of system status:

```bash
# Comprehensive deployment validation
./validate-deployment.sh

# System health check
python start_system.py health-check

# Configuration validation
python start_system.py validate-config

# System status
python -c "from src.system_lifecycle import get_system_status; print(get_system_status())"
```

## Common Issues and Solutions

### 1. Configuration Issues

#### Problem: "Gemini API key is required"
```
ConfigurationError: Gemini API key is required
```

**Solution:**
```bash
# Check if API key is set
echo $CHORUS_GEMINI_API_KEY

# Set API key in .env file
echo "CHORUS_GEMINI_API_KEY=your_actual_api_key_here" >> .env

# Validate API key format (should start with "AI..." and be ~40 characters)
python -c "
from src.config import settings
print(f'API Key: {settings.gemini.api_key[:10]}...')
print(f'Length: {len(settings.gemini.api_key)}')
"
```

#### Problem: "Redis connection failed"
```
ConnectionError: Redis connection failed
```

**Solution:**
```bash
# Check Redis server status
redis-cli ping

# Check Redis configuration
redis-cli info server

# Test connection with specific host/port
redis-cli -h $CHORUS_REDIS_HOST -p $CHORUS_REDIS_PORT ping

# Check Redis logs
sudo journalctl -u redis-server -f

# Restart Redis if needed
sudo systemctl restart redis-server
```

#### Problem: "Configuration validation failed"
```
ValidationError: Configuration validation failed
```

**Solution:**
```bash
# Run detailed validation
python -m src.config_validator

# Check specific environment file
python -m src.config_validator --env-file .env.production

# Validate individual settings
python -c "
from src.config import load_settings, validate_configuration
settings = load_settings()
issues = validate_configuration(settings)
for issue in issues:
    print(f'Issue: {issue}')
"
```

### 2. Dependency Issues

#### Problem: "Required dependencies failed"
```
DependencyError: Required dependencies failed: ['redis_connection', 'gemini_api']
```

**Solution:**
```bash
# Check individual dependencies
python -c "
from src.system_lifecycle import lifecycle_manager
for name, check in lifecycle_manager.dependency_checks.items():
    try:
        result = check.check_function()
        print(f'{name}: {'PASS' if result else 'FAIL'}')
    except Exception as e:
        print(f'{name}: ERROR - {e}')
"

# Test Redis dependency
python -c "
from src.prediction_engine.redis_client import RedisClient
client = RedisClient()
print('Redis ping:', client.ping())
"

# Test Gemini API dependency
python -c "
from src.prediction_engine.gemini_client import GeminiClient
client = GeminiClient()
print('Gemini test:', client.test_connection())
"
```

### 3. Docker Issues

#### Problem: "Docker services not starting"
```bash
# Check Docker daemon status
sudo systemctl status docker

# Check Docker Compose logs
./deploy-docker.sh logs

# Check individual service logs
docker-compose logs backend
docker-compose logs redis
docker-compose logs dashboard

# Restart Docker services
./deploy-docker.sh stop
./deploy-docker.sh dev  # or prod
```

#### Problem: "Port already in use"
```
Error: Port 8000 is already in use
```

**Solution:**
```bash
# Find process using the port
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process if safe to do so
sudo kill -9 <PID>

# Or change port in configuration
echo "CHORUS_API_PORT=8001" >> .env
```

### 4. API Issues

#### Problem: "API not responding"
```bash
# Check if API process is running
ps aux | grep uvicorn

# Check API logs
tail -f logs/chorus.log

# Test API endpoints
curl -v http://localhost:8000/health
curl -v http://localhost:8000/api/v1/system/health

# Check API configuration
python -c "
from src.config import settings
print(f'API Host: {settings.api_host}')
print(f'API Port: {settings.api_port}')
print(f'API Workers: {settings.api_workers}')
"
```

#### Problem: "API returns 500 errors"
```bash
# Check detailed API logs
tail -f logs/chorus.log | grep ERROR

# Run API in debug mode
CHORUS_DEBUG=true python start_system.py api

# Test API dependencies
python -c "
from src.api.main import create_app
from src.system_lifecycle import lifecycle_manager
app = create_app(lifecycle_manager)
print('API app created successfully')
"
```

### 5. Database Issues

#### Problem: "Redis memory issues"
```
Redis OOM: Out of memory
```

**Solution:**
```bash
# Check Redis memory usage
redis-cli info memory

# Check Redis configuration
redis-cli config get maxmemory
redis-cli config get maxmemory-policy

# Set memory limit and policy
redis-cli config set maxmemory 256mb
redis-cli config set maxmemory-policy allkeys-lru

# Clear Redis data if safe
redis-cli flushdb
```

#### Problem: "Trust scores not persisting"
```bash
# Check Redis connection
redis-cli ping

# Check trust score keys
redis-cli keys "trust_score:*"

# Test trust score operations
python -c "
from src.prediction_engine.trust_manager import TrustScoreManager
manager = TrustScoreManager()
manager.update_trust_score('test_agent', 90, 'test')
score = manager.get_trust_score('test_agent')
print(f'Test score: {score}')
"
```

### 6. Performance Issues

#### Problem: "High CPU usage"
```bash
# Check system resources
htop
iostat 1

# Check agent count
python -c "
from src.config import settings
print(f'Min agents: {settings.agent_simulation.min_agents}')
print(f'Max agents: {settings.agent_simulation.max_agents}')
"

# Reduce agent count temporarily
echo "CHORUS_MAX_AGENTS=5" >> .env
```

#### Problem: "High memory usage"
```bash
# Check memory usage by component
ps aux --sort=-%mem | head -10

# Check Redis memory
redis-cli info memory

# Check log file sizes
du -sh logs/

# Clean up old logs
find logs/ -name "*.log.*" -mtime +7 -delete
```

### 7. Network Issues

#### Problem: "Cannot connect to external services"
```bash
# Test internet connectivity
ping google.com

# Test Gemini API connectivity
curl -v https://generativelanguage.googleapis.com/v1/models

# Test Datadog connectivity (if enabled)
curl -v https://api.datadoghq.com/api/v1/validate

# Check firewall rules
sudo ufw status
sudo iptables -L
```

#### Problem: "Dashboard not accessible"
```bash
# Check if dashboard is running
curl http://localhost:3000  # Development
curl http://localhost:80    # Production

# Check dashboard logs
./deploy-docker.sh logs dashboard

# Check nginx configuration (production)
sudo nginx -t
sudo systemctl status nginx
```

### 8. Service Management Issues

#### Problem: "Systemd service not starting"
```bash
# Check service status
sudo systemctl status chorus-agent-predictor

# Check service logs
sudo journalctl -u chorus-agent-predictor -f

# Check service configuration
sudo systemctl cat chorus-agent-predictor

# Reload systemd configuration
sudo systemctl daemon-reload
sudo systemctl restart chorus-agent-predictor
```

#### Problem: "Service crashes on startup"
```bash
# Check startup logs
sudo journalctl -u chorus-agent-predictor --since "5 minutes ago"

# Run service manually for debugging
sudo -u chorus /opt/chorus-agent-predictor/backend/venv/bin/python \
  /opt/chorus-agent-predictor/backend/start_system.py simulation

# Check file permissions
ls -la /opt/chorus-agent-predictor/backend/
sudo chown -R chorus:chorus /opt/chorus-agent-predictor/
```

## Diagnostic Scripts

### System Health Check Script
```bash
#!/bin/bash
# save as health_check.sh

echo "=== Chorus System Health Check ==="

# Configuration
echo "1. Configuration Check:"
python start_system.py validate-config

# Dependencies
echo "2. Dependency Check:"
python start_system.py health-check

# Services
echo "3. Service Check:"
curl -f http://localhost:8000/health && echo "API: OK" || echo "API: FAIL"
redis-cli ping && echo "Redis: OK" || echo "Redis: FAIL"

# Resources
echo "4. Resource Check:"
free -h
df -h .
```

### Log Analysis Script
```bash
#!/bin/bash
# save as analyze_logs.sh

echo "=== Recent Errors ==="
tail -100 logs/chorus.log | grep ERROR

echo "=== Recent Warnings ==="
tail -100 logs/chorus.log | grep WARNING

echo "=== System Events ==="
tail -50 logs/chorus.log | grep "system_"

echo "=== Agent Events ==="
tail -50 logs/chorus.log | grep "agent_"
```

## Getting Help

### Log Collection for Support
```bash
# Collect system information
./validate-deployment.sh > system_info.txt 2>&1

# Collect configuration (sanitized)
python -c "
from src.config import settings
summary = settings.get_config_summary()
import json
print(json.dumps(summary, indent=2))
" > config_summary.json

# Collect recent logs
tail -500 logs/chorus.log > recent_logs.txt

# Create support bundle
tar -czf chorus_support_$(date +%Y%m%d_%H%M%S).tar.gz \
  system_info.txt config_summary.json recent_logs.txt .env.example
```

### Debug Mode
```bash
# Enable debug mode
export CHORUS_DEBUG=true
export CHORUS_LOG_LEVEL=DEBUG

# Run with debug output
python start_system.py simulation

# Or for API mode
python start_system.py api
```

### Contact Information
- Check the main README.md for project documentation
- Review the DEPLOYMENT.md for detailed deployment instructions
- Use the validate-deployment.sh script for automated diagnostics
- Check system logs in /var/log/chorus/ (production) or logs/ (development)

## Prevention

### Regular Maintenance
```bash
# Weekly health check
./validate-deployment.sh

# Monthly log cleanup
find logs/ -name "*.log.*" -mtime +30 -delete

# Quarterly configuration review
python -m src.config_validator

# Monitor system resources
df -h
free -h
redis-cli info memory
```

### Monitoring Setup
```bash
# Set up log monitoring
tail -f logs/chorus.log | grep -E "(ERROR|CRITICAL)"

# Set up health monitoring
watch -n 30 'python start_system.py health-check'

# Set up resource monitoring
watch -n 60 'free -h && df -h'
```