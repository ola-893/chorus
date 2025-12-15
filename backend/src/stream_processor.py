"""
Stream processing pipeline for agent messages.
"""
import json
import threading
import time
from typing import Optional, Dict, Any

from .config import settings
from .logging_config import get_agent_logger
from .integrations.kafka_client import kafka_bus, KafkaOperationError
from .prediction_engine.intervention_engine import intervention_engine
from .prediction_engine.models.core import AgentIntention, ConflictAnalysis

agent_logger = get_agent_logger(__name__)

class StreamProcessor:
    """
    Processes stream of agent messages to predict and prevent conflicts.
    """
    
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.input_topic = settings.kafka.agent_messages_topic
        self.output_topic = settings.kafka.agent_decisions_topic
        self.dlq_topic = "agent-messages-dlq" # Convention
        
    def start(self):
        """Start processing loop in a background thread."""
        if self.running:
            return
            
        self.running = True
        kafka_bus.subscribe([self.input_topic])
        
        self.thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.thread.start()
        
        agent_logger.log_agent_action(
            "INFO", 
            "Stream processor started", 
            action_type="stream_processor_start",
            context={"input_topic": self.input_topic}
        )

    def stop(self):
        """Stop processing loop."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            
        agent_logger.log_agent_action(
            "INFO", 
            "Stream processor stopped", 
            action_type="stream_processor_stop"
        )

    def _processing_loop(self):
        """Main processing loop."""
        while self.running:
            try:
                # Poll for messages
                msg = kafka_bus.poll(timeout=1.0)
                
                if msg is None:
                    continue
                    
                self._process_message(msg)
                
                # Manual commit effectively happening via auto-commit=False logic if we implemented it, 
                # but KafkaMessageBus.commit() exists.
                kafka_bus.commit()
                
            except Exception as e:
                agent_logger.log_system_error(e, "stream_processor", "loop")
                time.sleep(1.0) # Backoff on loop crash

    def _process_message(self, msg: Dict[str, Any]):
        """
        Process a single message.
        """
        try:
            payload = msg.get("value")
            if not payload:
                return

            # Assume payload is an AgentIntention or similar dict
            # We need to convert it to AgentIntention object if possible
            # For now, let's assume it's a dict compatible with our logic
            
            # Enrich / Analyze
            # In a real scenario, we might batch these or look up context
            # Here we call the intervention engine directly
            
            # We simulate "Analysis" 
            # (InterventionEngine might be complex, for now let's pass-through or mock logic)
            
            decision = self._analyze_intention(payload)
            
            # Produce decision
            kafka_bus.produce(
                self.output_topic,
                decision,
                key=msg.get("key")
            )
            
        except Exception as e:
            agent_logger.log_system_error(
                e, 
                "stream_processor", 
                "process_message", 
                context={"msg_offset": msg.get("offset")}
            )
            # Send to DLQ
            try:
                kafka_bus.produce(
                    self.dlq_topic,
                    {
                        "original_message": msg,
                        "error": str(e),
                        "timestamp": time.time()
                    },
                    key=msg.get("key")
                )
            except Exception as dlq_error:
                agent_logger.log_system_error(dlq_error, "stream_processor", "dlq_produce")

    def _analyze_intention(self, intention_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze intention and generate decision.
        """
        # This is where we would call Gemini/InterventionEngine
        # For prototype, we generate a mock decision
        
        agent_id = intention_data.get("agent_id", "unknown")
        
        # Determine if conflict (mock logic or integration)
        # In full implementation, we'd convert intention_data to AgentIntention
        # analysis = intervention_engine.evaluate(...)
        
        return {
            "decision_id": f"dec_{int(time.time())}",
            "agent_id": agent_id,
            "status": "APPROVED", # or REJECTED
            "risk_score": 0.1,
            "processed_at": time.time(),
            "original_request": intention_data
        }

# Global instance
stream_processor = StreamProcessor()
