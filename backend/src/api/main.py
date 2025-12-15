"""
FastAPI application for the Chorus Agent Conflict Predictor.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import asyncio
import json
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
    from fastapi.security import Security
    from fastapi.security.api_key import APIKeyHeader
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    # FastAPI is optional dependency
    FastAPI = None
    HTTPException = None
    Depends = None
    Security = None
    APIKeyHeader = None
    JSONResponse = None
    BaseModel = None
    FASTAPI_AVAILABLE = False
    BaseModel = None
    WebSocket = None
    WebSocketDisconnect = None
    Security = None
    APIKeyHeader = None
    Request = None

from ..system_lifecycle import SystemLifecycleManager
from ..logging_config import get_agent_logger
from ..prediction_engine.redis_client import RedisClient
from ..prediction_engine.trust_manager import RedisTrustManager, RedisTrustScoreManager
from ..config import settings
from ..event_bus import event_bus

agent_logger = get_agent_logger(__name__)

# Security schemes
API_KEY_NAME = "X-Agent-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False) if FASTAPI_AVAILABLE else None

async def verify_api_key(api_key: str = Security(api_key_header) if FASTAPI_AVAILABLE and Security else None):
    """
    Verify API key.
    """
    # In development/test, we might allow no auth if configured
    if settings.environment.value in ["development", "testing"] and not settings.is_production():
        if not api_key:
            return None # Allow anonymous in dev/test for now, or check generic key
            
    if not api_key:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
        
    # In a real app, check against DB/Redis
    # For now, we check against a simple configured key if present, or generic
    # Assume valid if it matches an internal secret or is a valid agent ID hash
    return api_key

class RateLimiter:
    """
    Simple Redis-based rate limiter.
    """
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.redis = RedisClient()

    async def __call__(self, request: Request, api_key: str = Depends(verify_api_key)):
        """
        Check rate limit.
        """
        if not self.redis:
            return
            
        # Use IP or API key as identifier
        client_id = api_key if api_key else request.client.host
        key = f"rate_limit:{client_id}:{datetime.now(timezone.utc).minute}"
        
        try:
            current = self.redis.get(key)
            if current and int(current) >= self.requests_per_minute:
                raise HTTPException(status_code=429, detail="Too many requests")
            
            # Increment
            pipe = self.redis._client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60) # Expire after 1 minute
            pipe.execute()
        except HTTPException:
            raise
        except Exception as e:
            # Fail open if Redis error
            agent_logger.log_system_error(e, "api", "rate_limiter")

# Instantiate rate limiter
limiter = RateLimiter(requests_per_minute=100)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    uptime: float
    components: Dict[str, str]
    details: Optional[Dict[str, Any]] = None


class SystemStatusResponse(BaseModel):
    """System status response model."""
    state: str
    uptime: float
    start_time: Optional[str]
    is_healthy: bool
    dependency_checks: int
    health: Optional[Dict[str, Any]] = None

class TrustScoreResponse(BaseModel):
    """Trust score response model."""
    agent_id: str
    trust_score: int
    history_length: int
    last_updated: Optional[str] = None

class ConnectionManager:
    """WebSocket connection manager."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                agent_logger.log_system_error(e, "api", "broadcast")

manager = ConnectionManager()


def create_app(lifecycle_manager: SystemLifecycleManager) -> FastAPI:
    """
    Create FastAPI application with lifecycle management.
    
    Args:
        lifecycle_manager: System lifecycle manager instance
        
    Returns:
        FastAPI application instance
    """
    if FastAPI is None:
        raise ImportError("FastAPI is required for API mode. Install with: pip install fastapi")
    
    app = FastAPI(
        title="Chorus Agent Conflict Predictor API",
        description="Real-time conflict prediction and intervention for decentralized agent networks",
        version="0.1.0"
    )
    
    # Initialize Redis components for API use
    # Note: In a real app, this might be dependency injected or managed by lifecycle
    try:
        redis_client = RedisClient()
        score_manager = RedisTrustScoreManager(redis_client_instance=redis_client)
        trust_manager = RedisTrustManager(score_manager=score_manager)
    except Exception as e:
        agent_logger.log_system_error(e, "api", "init_redis_components")
        trust_manager = None
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """
        Health check endpoint.
        
        Returns:
            Health status information
        """
        try:
            # Get system status
            system_status = lifecycle_manager.get_status()
            
            # Determine overall health
            is_healthy = lifecycle_manager.is_healthy()
            status = "healthy" if is_healthy else "unhealthy"
            
            # Get component statuses
            components = {}
            if "health" in system_status and system_status["health"]["component_statuses"]:
                components = system_status["health"]["component_statuses"]
            
            response = HealthResponse(
                status=status,
                timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                uptime=system_status["uptime"],
                components=components,
                details={
                    "state": system_status["state"],
                    "dependency_checks": system_status["dependency_checks"]
                }
            )
            
            # Log health check
            agent_logger.log_agent_action(
                "INFO",
                f"Health check requested: {status}",
                action_type="api_health_check",
                context={"status": status, "uptime": system_status["uptime"]}
            )
            
            # Return appropriate HTTP status
            if is_healthy:
                return response
            else:
                return JSONResponse(
                    status_code=503,
                    content=response.dict()
                )
                
        except Exception as e:
            agent_logger.log_system_error(
                e,
                component="api",
                operation="health_check"
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    "error": str(e)
                }
            )
    
    @app.get("/status", response_model=SystemStatusResponse, dependencies=[Depends(verify_api_key), Depends(limiter)])
    async def system_status():
        """
        System status endpoint.
        
        Returns:
            Detailed system status information
        """
        try:
            status = lifecycle_manager.get_status()
            
            response = SystemStatusResponse(
                state=status["state"],
                uptime=status["uptime"],
                start_time=status["start_time"],
                is_healthy=status["is_healthy"],
                dependency_checks=status["dependency_checks"],
                health=status.get("health")
            )
            
            agent_logger.log_agent_action(
                "INFO",
                "System status requested",
                action_type="api_system_status",
                context={"state": status["state"]}
            )
            
            return response
            
        except Exception as e:
            agent_logger.log_system_error(
                e,
                component="api",
                operation="system_status"
            )
            
            raise HTTPException(status_code=500, detail=str(e))
            
    @app.get("/agents/{agent_id}/trust-score", response_model=TrustScoreResponse, dependencies=[Depends(verify_api_key), Depends(limiter)])
    async def get_agent_trust_score(agent_id: str):
        """
        Get trust score for a specific agent.
        """
        if not trust_manager:
            raise HTTPException(status_code=503, detail="Trust manager not available")
            
        try:
            score = trust_manager.get_trust_score(agent_id)
            history = trust_manager.get_agent_history(agent_id)
            
            return TrustScoreResponse(
                agent_id=agent_id,
                trust_score=score,
                history_length=len(history),
                last_updated=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z') 
            )
        except Exception as e:
            agent_logger.log_system_error(e, "api", "get_trust_score", context={"agent_id": agent_id})
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agents/{agent_id}/history", dependencies=[Depends(verify_api_key), Depends(limiter)])
    async def get_agent_history(agent_id: str, start: Optional[str] = None, end: Optional[str] = None):
        """
        Get historical trust score data for a specific agent.
        """
        if not trust_manager:
            raise HTTPException(status_code=503, detail="Trust manager not available")
            
        try:
            history = trust_manager.get_agent_history(agent_id)
            
            # Filter by time range if provided
            if start or end:
                filtered_history = []
                for entry in history:
                    entry_time = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                    
                    if start:
                        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        if entry_time < start_time:
                            continue
                    
                    if end:
                        end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
                        if entry_time > end_time:
                            continue
                    
                    filtered_history.append(entry)
                
                history = filtered_history
            
            return {
                "agent_id": agent_id,
                "history": history,
                "total_entries": len(history),
                "time_range": {
                    "start": start,
                    "end": end
                }
            }
        except Exception as e:
            agent_logger.log_system_error(e, "api", "get_agent_history", context={"agent_id": agent_id})
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agents", dependencies=[Depends(verify_api_key), Depends(limiter)])
    async def get_all_agents():
        """
        Get list of all agents with their current trust scores.
        """
        if not trust_manager:
            raise HTTPException(status_code=503, detail="Trust manager not available")
            
        try:
            # Get all agent IDs from trust manager
            all_agents = []
            
            # This is a simplified implementation - in a real system, 
            # you'd have a proper agent registry
            agent_ids = trust_manager.get_all_agent_ids() if hasattr(trust_manager, 'get_all_agent_ids') else []
            
            for agent_id in agent_ids:
                score = trust_manager.get_trust_score(agent_id)
                history = trust_manager.get_agent_history(agent_id)
                last_entry = history[-1] if history else None
                
                all_agents.append({
                    "id": agent_id,
                    "trust_score": score,
                    "status": "quarantined" if score < 30 else "active",
                    "last_updated": last_entry.get('timestamp') if last_entry else datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    "history_length": len(history)
                })
            
            return {
                "agents": all_agents,
                "total_count": len(all_agents),
                "active_count": len([a for a in all_agents if a["status"] == "active"]),
                "quarantined_count": len([a for a in all_agents if a["status"] == "quarantined"]),
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        except Exception as e:
            agent_logger.log_system_error(e, "api", "get_all_agents")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/dashboard/metrics", dependencies=[Depends(verify_api_key), Depends(limiter)])
    async def get_dashboard_metrics():
        """
        Get aggregated metrics for the dashboard.
        """
        # In a real scenario, this would aggregate data from Datadog or Redis
        # For now, we return system status and trust summary
        status = lifecycle_manager.get_status()
        
        return {
            "system_health": status.get("is_healthy", False),
            "uptime": status.get("uptime", 0),
            "active_agents": 0, # TODO: Connect to simulation manager
            "conflicts_detected": 0, # TODO: Connect to prediction engine stats
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

    @app.get("/system/circuit-breakers", dependencies=[Depends(verify_api_key), Depends(limiter)])
    async def get_circuit_breaker_status():
        """
        Get current circuit breaker states for all services.
        """
        try:
            from ..error_handling import gemini_circuit_breaker, redis_circuit_breaker
            
            circuit_breakers = [
                {
                    "service_name": "gemini_api",
                    "state": gemini_circuit_breaker.state,
                    "failure_count": gemini_circuit_breaker.failure_count,
                    "last_failure_time": gemini_circuit_breaker.last_failure_time.isoformat() + "Z" if gemini_circuit_breaker.last_failure_time else None,
                    "next_attempt_time": gemini_circuit_breaker.next_attempt_time.isoformat() + "Z" if gemini_circuit_breaker.next_attempt_time else None
                },
                {
                    "service_name": "redis",
                    "state": redis_circuit_breaker.state,
                    "failure_count": redis_circuit_breaker.failure_count,
                    "last_failure_time": redis_circuit_breaker.last_failure_time.isoformat() + "Z" if redis_circuit_breaker.last_failure_time else None,
                    "next_attempt_time": redis_circuit_breaker.next_attempt_time.isoformat() + "Z" if redis_circuit_breaker.next_attempt_time else None
                }
            ]
            
            return {
                "circuit_breakers": circuit_breakers,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
        except Exception as e:
            agent_logger.log_system_error(e, "api", "get_circuit_breaker_status")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/system/dependencies", dependencies=[Depends(verify_api_key), Depends(limiter)])
    async def get_dependency_status():
        """
        Get status of external dependencies.
        """
        try:
            from ..system_health import health_monitor
            
            # Force health checks to get current status
            health_results = health_monitor.force_health_check()
            
            dependencies = []
            for check_name, is_healthy in health_results.items():
                status = "connected" if is_healthy else "disconnected"
                
                # Mock response times for demonstration
                response_times = {
                    "redis_connection": 2.3,
                    "gemini_api": 120.5,
                    "system_resources": 1.0
                }
                
                dependencies.append({
                    "name": check_name.replace("_", " ").title(),
                    "status": status,
                    "last_check": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "response_time": response_times.get(check_name, 0.0),
                    "error_message": None if is_healthy else f"{check_name} check failed"
                })
            
            return {
                "dependencies": dependencies,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
        except Exception as e:
            agent_logger.log_system_error(e, "api", "get_dependency_status")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/system/metrics", dependencies=[Depends(verify_api_key), Depends(limiter)])
    async def get_system_metrics():
        """
        Get current system performance metrics.
        """
        try:
            import psutil
            
            # Get system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Mock some additional metrics
            metrics = {
                "memory_usage": memory.percent,
                "cpu_usage": cpu_percent,
                "active_connections": len(manager.active_connections),
                "requests_per_minute": 145,  # Mock value
                "error_rate": 0.2  # Mock value
            }
            
            return {
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
        except ImportError:
            # psutil not available, return mock data
            return {
                "metrics": {
                    "memory_usage": 68.5,
                    "cpu_usage": 23.1,
                    "active_connections": len(manager.active_connections),
                    "requests_per_minute": 145,
                    "error_rate": 0.2
                },
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
        except Exception as e:
            agent_logger.log_system_error(e, "api", "get_system_metrics")
            raise HTTPException(status_code=500, detail=str(e))

    @app.websocket("/ws/dashboard")
    async def websocket_endpoint(websocket: WebSocket):
        """
        WebSocket endpoint for real-time dashboard updates.
        """
        await manager.connect(websocket)
        try:
            # Send initial state
            status = lifecycle_manager.get_status()
            await websocket.send_json({
                "type": "system_status",
                "data": status,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            })
            
            # Send initial circuit breaker status
            try:
                from ..error_handling import gemini_circuit_breaker, redis_circuit_breaker
                circuit_breakers = [
                    {
                        "service_name": "gemini_api",
                        "state": gemini_circuit_breaker.state,
                        "failure_count": gemini_circuit_breaker.failure_count,
                        "last_failure_time": gemini_circuit_breaker.last_failure_time.isoformat() + "Z" if gemini_circuit_breaker.last_failure_time else None,
                        "next_attempt_time": gemini_circuit_breaker.next_attempt_time.isoformat() + "Z" if gemini_circuit_breaker.next_attempt_time else None
                    },
                    {
                        "service_name": "redis",
                        "state": redis_circuit_breaker.state,
                        "failure_count": redis_circuit_breaker.failure_count,
                        "last_failure_time": redis_circuit_breaker.last_failure_time.isoformat() + "Z" if redis_circuit_breaker.last_failure_time else None,
                        "next_attempt_time": redis_circuit_breaker.next_attempt_time.isoformat() + "Z" if redis_circuit_breaker.next_attempt_time else None
                    }
                ]
                
                for cb in circuit_breakers:
                    await websocket.send_json({
                        "type": "circuit_breaker_update",
                        "data": cb,
                        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                    })
            except Exception as e:
                agent_logger.log_system_error(e, "api", "websocket_circuit_breaker_init")
            
            while True:
                # Keep connection alive, actual updates come via event_bus
                await asyncio.sleep(60) 
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    @app.get("/")
    async def root():
        """
        Root endpoint.
        
        Returns:
            Basic API information
        """
        return {
            "name": "Chorus Agent Conflict Predictor API",
            "version": "0.1.0",
            "status": "running" if lifecycle_manager.is_running() else "stopped",
            "endpoints": {
                "health": "/health",
                "status": "/status",
                "docs": "/docs",
                "trust_score": "/agents/{agent_id}/trust-score",
                "metrics": "/dashboard/metrics",
                "circuit_breakers": "/system/circuit-breakers",
                "dependencies": "/system/dependencies",
                "system_metrics": "/system/metrics",
                "websocket": "/ws/dashboard"
            }
        }
    
    # Add startup and shutdown event handlers
    @app.on_event("startup")
    async def startup_event():
        """Handle application startup."""
        agent_logger.log_agent_action(
            "INFO",
            "FastAPI application started",
            action_type="api_startup"
        )
        
        # Subscribe to event bus
        async def broadcast_event(data):
            try:
                # data should be a dict with 'type' and 'payload'
                message = json.dumps(data, default=str)
                await manager.broadcast(message)
            except Exception as e:
                agent_logger.log_system_error(e, "api", "broadcast_event")

        event_bus.subscribe("trust_score_update", broadcast_event)
        event_bus.subscribe("conflict_prediction", broadcast_event)
        event_bus.subscribe("system_health", broadcast_event)
        event_bus.subscribe("intervention_executed", broadcast_event)
        event_bus.subscribe("circuit_breaker_state_change", broadcast_event)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Handle application shutdown."""
        agent_logger.log_agent_action(
            "INFO",
            "FastAPI application shutting down",
            action_type="api_shutdown"
        )
        
        # Ensure lifecycle manager is shut down
        if lifecycle_manager.is_running():
            lifecycle_manager.shutdown()
    
    return app


# Create the app instance for uvicorn
from src.config import settings
lifecycle_manager = SystemLifecycleManager(settings)
app = create_app(lifecycle_manager)