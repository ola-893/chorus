# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used by the Chorus Agent Conflict Predictor system.

## Core Configuration

### Environment Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_ENVIRONMENT` | Yes | `development` | Deployment environment: `development`, `testing`, `staging`, `production` |
| `CHORUS_DEBUG` | No | `false` | Enable debug mode with verbose logging |

## Google Gemini API Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_GEMINI_API_KEY` | Yes | - | Google Gemini API key for conflict prediction |
| `CHORUS_GEMINI_MODEL` | No | `gemini-3-pro-preview` | Gemini model to use for analysis |
| `CHORUS_GEMINI_TIMEOUT` | No | `30.0` | API request timeout in seconds |
| `CHORUS_GEMINI_MAX_RETRIES` | No | `3` | Maximum retry attempts for failed requests |
| `CHORUS_GEMINI_RETRY_DELAY` | No | `1.0` | Delay between retry attempts in seconds |

## Redis Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_REDIS_HOST` | Yes | `localhost` | Redis server hostname or IP address |
| `CHORUS_REDIS_PORT` | No | `6379` | Redis server port number |
| `CHORUS_REDIS_PASSWORD` | No | - | Redis authentication password (recommended for production) |
| `CHORUS_REDIS_DB` | No | `0` | Redis database number (0-15) |
| `CHORUS_REDIS_POOL_SIZE` | No | `10` | Connection pool size |
| `CHORUS_REDIS_SOCKET_TIMEOUT` | No | `5.0` | Socket timeout in seconds |
| `CHORUS_REDIS_CONNECT_TIMEOUT` | No | `5.0` | Connection timeout in seconds |
| `CHORUS_REDIS_RETRY_ON_TIMEOUT` | No | `true` | Retry operations on timeout |

## API Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_API_HOST` | No | `0.0.0.0` | API server bind address |
| `CHORUS_API_PORT` | No | `8000` | API server port number |
| `CHORUS_API_WORKERS` | No | `1` | Number of API worker processes |

## Agent Simulation Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_MIN_AGENTS` | No | `5` | Minimum number of agents in simulation |
| `CHORUS_MAX_AGENTS` | No | `10` | Maximum number of agents in simulation |
| `CHORUS_AGENT_REQUEST_INTERVAL_MIN` | No | `1.0` | Minimum interval between agent requests (seconds) |
| `CHORUS_AGENT_REQUEST_INTERVAL_MAX` | No | `10.0` | Maximum interval between agent requests (seconds) |
| `CHORUS_AGENT_RESOURCE_TYPES` | No | `cpu,memory,network,storage` | Comma-separated list of resource types |

## Trust Scoring Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_INITIAL_TRUST_SCORE` | No | `100` | Initial trust score for new agents |
| `CHORUS_TRUST_SCORE_THRESHOLD` | No | `30` | Trust score threshold for quarantine |
| `CHORUS_TRUST_CONFLICT_PENALTY` | No | `10` | Trust score penalty for conflicts |
| `CHORUS_TRUST_COOPERATION_BONUS` | No | `1` | Trust score bonus for cooperation |
| `CHORUS_MAX_TRUST_SCORE` | No | `100` | Maximum possible trust score |
| `CHORUS_MIN_TRUST_SCORE` | No | `0` | Minimum possible trust score |

## Conflict Prediction Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_CONFLICT_RISK_THRESHOLD` | No | `0.7` | Risk threshold for intervention (0.0-1.0) |
| `CHORUS_PREDICTION_INTERVAL` | No | `5.0` | Prediction interval in seconds |
| `CHORUS_ANALYSIS_WINDOW` | No | `10` | Number of recent actions to analyze |

## Logging Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_LOG_LEVEL` | No | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `CHORUS_LOG_FORMAT` | No | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format |
| `CHORUS_LOG_STRUCTURED` | No | `true` | Use structured JSON logging |
| `CHORUS_LOG_FILE_PATH` | No | - | Log file path (if not set, logs to console) |
| `CHORUS_LOG_MAX_FILE_SIZE` | No | `10485760` | Maximum log file size in bytes (10MB) |
| `CHORUS_LOG_BACKUP_COUNT` | No | `5` | Number of log file backups to keep |

## Health Check Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_HEALTH_CHECK_ENABLED` | No | `true` | Enable health monitoring |
| `CHORUS_HEALTH_CHECK_INTERVAL` | No | `30.0` | Health check interval in seconds |
| `CHORUS_HEALTH_CHECK_TIMEOUT` | No | `10.0` | Health check timeout in seconds |
| `CHORUS_HEALTH_CHECK_MAX_FAILURES` | No | `3` | Maximum consecutive failures before marking as failed |

## CLI Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_CLI_REFRESH_RATE` | No | `1.0` | CLI dashboard refresh rate in seconds |
| `CHORUS_CLI_MAX_LINES` | No | `50` | Maximum lines to display in CLI |

## Datadog Integration (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_DATADOG_ENABLED` | No | `false` | Enable Datadog integration |
| `CHORUS_DATADOG_API_KEY` | No* | - | Datadog API key (*required if enabled) |
| `CHORUS_DATADOG_APP_KEY` | No* | - | Datadog application key (*required if enabled) |
| `CHORUS_DATADOG_SITE` | No | `datadoghq.com` | Datadog site (e.g., `datadoghq.eu` for EU) |

## ElevenLabs Integration (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHORUS_ELEVENLABS_ENABLED` | No | `false` | Enable ElevenLabs voice alerts |
| `CHORUS_ELEVENLABS_API_KEY` | No* | - | ElevenLabs API key (*required if enabled) |
| `CHORUS_ELEVENLABS_VOICE_ID` | No | `21m00Tcm4TlvDq8ikWAM` | Default voice ID for alerts |

## Confluent Kafka Integration (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KAFKA_ENABLED` | No | `false` | Enable Kafka event streaming |
| `KAFKA_BOOTSTRAP_SERVERS` | No* | `localhost:9092` | Kafka bootstrap servers (*required if enabled) |
| `KAFKA_SECURITY_PROTOCOL` | No | `PLAINTEXT` | Security protocol: `PLAINTEXT`, `SASL_SSL` |
| `KAFKA_SASL_MECHANISM` | No | - | SASL mechanism: `PLAIN`, `SCRAM-SHA-256` |
| `KAFKA_SASL_USERNAME` | No* | - | SASL username (*required for SASL) |
| `KAFKA_SASL_PASSWORD` | No* | - | SASL password (*required for SASL) |
| `KAFKA_AGENT_MESSAGES_TOPIC` | No | `agent-messages-raw` | Topic for raw agent messages |
| `KAFKA_AGENT_DECISIONS_TOPIC` | No | `agent-decisions-processed` | Topic for processed decisions |
| `KAFKA_SYSTEM_ALERTS_TOPIC` | No | `system-alerts` | Topic for system alerts |

## Environment-Specific Recommendations

### Development Environment
```bash
CHORUS_ENVIRONMENT=development
CHORUS_DEBUG=true
CHORUS_LOG_LEVEL=DEBUG
CHORUS_MIN_AGENTS=3
CHORUS_MAX_AGENTS=5
CHORUS_REDIS_HOST=localhost
CHORUS_DATADOG_ENABLED=false
```

### Staging Environment
```bash
CHORUS_ENVIRONMENT=staging
CHORUS_DEBUG=false
CHORUS_LOG_LEVEL=INFO
CHORUS_MIN_AGENTS=5
CHORUS_MAX_AGENTS=10
CHORUS_REDIS_PASSWORD=staging_password
CHORUS_DATADOG_ENABLED=true
```

### Production Environment
```bash
CHORUS_ENVIRONMENT=production
CHORUS_DEBUG=false
CHORUS_LOG_LEVEL=INFO
CHORUS_LOG_STRUCTURED=true
CHORUS_LOG_FILE_PATH=/var/log/chorus/chorus.log
CHORUS_MIN_AGENTS=10
CHORUS_MAX_AGENTS=50
CHORUS_API_WORKERS=4
CHORUS_REDIS_POOL_SIZE=20
CHORUS_REDIS_PASSWORD=secure_production_password
CHORUS_DATADOG_ENABLED=true
CHORUS_HEALTH_CHECK_ENABLED=true
```

## Validation

Use the following commands to validate your environment configuration:

```bash
# Validate all configuration
python start_system.py validate-config

# Validate with specific environment file
python -m src.config_validator --env-file .env.production

# Test configuration loading
python -c "from src.config import load_settings; settings = load_settings(); print(settings.get_config_summary())"
```

## Security Considerations

1. **Never commit API keys to version control**
2. **Use strong passwords for Redis in production**
3. **Restrict Redis access to localhost or private networks**
4. **Use environment-specific configuration files**
5. **Regularly rotate API keys and passwords**
6. **Monitor access logs for suspicious activity**

## Troubleshooting

### Common Configuration Issues

1. **Invalid Gemini API Key**
   - Ensure key starts with "AI..." and is approximately 40 characters
   - Verify key is active in Google AI Studio

2. **Redis Connection Failed**
   - Check Redis server is running: `redis-cli ping`
   - Verify host, port, and password settings
   - Ensure network connectivity

3. **Configuration Validation Errors**
   - Run `python start_system.py validate-config` for detailed errors
   - Check for typos in variable names
   - Ensure required variables are set

4. **Performance Issues**
   - Adjust agent count based on system resources
   - Increase Redis pool size for high load
   - Monitor system resources and scale accordingly