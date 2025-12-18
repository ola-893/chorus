"""
API Router for historical event querying.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..event_sourcing import event_log_manager

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/history")
async def get_events_history(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type (message, decision, or all)"),
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format"),
    limit: int = Query(100, description="Max number of events to return", ge=1, le=1000)
):
    """
    Query historical events from the event log (Kafka).
    
    Returns events matching the specified filters, sorted by timestamp.
    """
    try:
        # Parse datetime strings if provided
        start_time = None
        end_time = None
        
        if start_date:
            try:
                start_time = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}")
        
        if end_date:
            try:
                end_time = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}")
        
        # If agent_id is provided, use the optimized get_agent_history
        if agent_id:
            events = event_log_manager.get_agent_history(
                agent_id, 
                start_time=start_time,
                end_time=end_time,
                event_type=event_type or "all"
            )
            # Limit results
            events = events[:limit]
        else:
            # For system-wide queries, we need to query both topics
            events = []
            
            # Define filter function
            def event_filter(payload):
                # Filter by event_type if specified
                if event_type and event_type != "all":
                    # This will be set by the topic we're querying
                    return True
                return True
            
            # Query message topic
            if not event_type or event_type in ["message", "all"]:
                msg_topic = event_log_manager.msg_topic
                for event in event_log_manager.replay_events(
                    msg_topic,
                    start_time=start_time,
                    end_time=end_time,
                    filter_func=event_filter,
                    limit=limit
                ):
                    event["type"] = "message"
                    events.append(event)
                    if len(events) >= limit:
                        break
            
            # Query decision topic if we haven't hit limit
            if (not event_type or event_type in ["decision", "all"]) and len(events) < limit:
                decision_topic = event_log_manager.decision_topic
                remaining_limit = limit - len(events)
                for event in event_log_manager.replay_events(
                    decision_topic,
                    start_time=start_time,
                    end_time=end_time,
                    filter_func=event_filter,
                    limit=remaining_limit
                ):
                    event["type"] = "decision"
                    events.append(event)
                    if len(events) >= limit:
                        break
            
            # Sort by timestamp
            events.sort(key=lambda x: x.get("timestamp", 0))
        
        # Format events for frontend consumption
        formatted_events = []
        for event in events:
            formatted_event = {
                "timestamp": event.get("timestamp"),
                "type": event.get("type", "unknown"),
                "source": event.get("value", {}).get("agent_id", "system"),
                "data": event.get("value", {}),
                "offset": event.get("offset"),
                "key": event.get("key")
            }
            formatted_events.append(formatted_event)
        
        return {
            "events": formatted_events,
            "count": len(formatted_events),
            "filters": {
                "agent_id": agent_id,
                "event_type": event_type,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query events: {str(e)}")
