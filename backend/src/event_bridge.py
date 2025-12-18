"""
Bridge between Kafka topics and local EventBus.
Enables API streaming updates from distributed components.
"""
import threading
import json
import logging
import time
from typing import Optional

from .integrations.kafka_client import kafka_bus
from .event_bus import event_bus
from .config import settings
from .logging_config import get_agent_logger

logger = logging.getLogger(__name__)
agent_logger = get_agent_logger(__name__)

class KafkaEventBridge:
    """
    Consumes Kafka messages and republishes them to the local EventBus.
    """
    
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.topics = [
            settings.kafka.agent_decisions_topic,
            settings.kafka.system_alerts_topic,
            settings.kafka.causal_graph_updates_topic,
            settings.kafka.analytics_metrics_topic
        ]
        
    def start(self):
        """Start the bridge in a background thread."""
        if self.running or not kafka_bus.enabled:
            return
            
        self.running = True
        kafka_bus.subscribe(self.topics)
        
        self.thread = threading.Thread(target=self._consumption_loop, daemon=True)
        self.thread.start()
        logger.info(f"Kafka Event Bridge started, listening to {self.topics}")
        
    def stop(self):
        """Stop the bridge."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            
    def _consumption_loop(self):
        """Main loop."""
        while self.running:
            try:
                # Use polling from kafka_bus (which uses shared consumer, might be tricky if other components use it)
                # Actually, KafkaMessageBus.consumer is shared.
                # If StreamProcessor is using it, we have a problem if they are in same process.
                # StreamProcessor calls kafka_bus.subscribe() and poll().
                # If API runs in same process, they will fight over the consumer.
                # BUT: API and StreamProcessor usually run in separate processes.
                # If they run in same process (e.g. demo mode), we should be careful.
                # Assuming separate processes for production.
                # For demo/dev, if they share 'kafka_bus' instance, 'subscribe' overwrites subscription.
                # We should use a separate consumer for the bridge.
                
                # Create a temporary consumer for the bridge
                # Use a unique group ID to avoid conflicting with StreamProcessor if they consume same topics
                group_id = f"chorus-api-bridge-{int(time.time())}"
                consumer = kafka_bus.create_temporary_consumer(group_id=group_id)
                if not consumer:
                    time.sleep(5)
                    continue
                    
                consumer.subscribe(self.topics)
                
                while self.running:
                    msg = consumer.poll(1.0)
                    if msg is None:
                        continue
                    if msg.error():
                        continue
                        
                    try:
                        val = json.loads(msg.value().decode('utf-8'))
                        topic = msg.topic()
                        
                        # Map Kafka topics to EventBus events
                        if topic == settings.kafka.agent_decisions_topic:
                            event_bus.publish("decision_update", val)
                        elif topic == settings.kafka.system_alerts_topic:
                            event_bus.publish("system_alert", val)
                        elif topic == settings.kafka.causal_graph_updates_topic:
                            event_bus.publish("graph_update", val)
                        elif topic == settings.kafka.analytics_metrics_topic:
                            # Re-map to system_alert for frontend compatibility, or use new event type
                            # Frontend expects type='system_alert' and data.type='stream_metrics'
                            # The StreamProcessor sends {"type": "stream_metrics", ...} as value.
                            # So we can publish as system_alert
                            event_bus.publish("system_alert", val)
                            
                    except Exception as e:
                        logger.error(f"Bridge decode error: {e}")
                        
            except Exception as e:
                logger.error(f"Bridge loop error: {e}")
                time.sleep(2.0)

# Global instance
kafka_event_bridge = KafkaEventBridge()
