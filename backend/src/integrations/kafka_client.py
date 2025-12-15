"""
Kafka integration client for message streaming.
"""
import json
import logging
import socket
from typing import Dict, Any, Optional, Callable, List
import time

try:
    from confluent_kafka import Producer, Consumer, KafkaError, Message, KafkaException
    from confluent_kafka.admin import AdminClient, NewTopic
except ImportError:
    Producer = None
    Consumer = None
    KafkaError = None
    Message = None
    KafkaException = None
    AdminClient = None
    NewTopic = None

from ..config import settings
from ..error_handling import (
    CircuitBreaker, 
    retry_with_exponential_backoff, 
    ChorusError
)
from ..logging_config import get_agent_logger

agent_logger = get_agent_logger(__name__)

class KafkaOperationError(ChorusError):
    """Exception for Kafka operation errors."""
    pass

class KafkaMessageBus:
    """
    Client for interacting with Confluent Kafka.
    """
    
    def __init__(self):
        """Initialize Kafka client."""
        self.enabled = settings.kafka.enabled
        self.bootstrap_servers = settings.kafka.bootstrap_servers
        self.security_protocol = settings.kafka.security_protocol
        self.sasl_mechanism = settings.kafka.sasl_mechanism
        self.sasl_username = settings.kafka.sasl_username
        self.sasl_password = settings.kafka.sasl_password
        
        self.producer = None
        self.consumer = None
        self._producer_config = {}
        self._consumer_config = {}
        
        # Define circuit breaker for Kafka operations
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30.0,
            expected_exception=(KafkaOperationError, Exception),
            service_name="kafka"
        )
        
        if self.enabled and Producer:
            self._initialize_config()
            self._initialize_producer()
    
    def _initialize_config(self):
        """Initialize Kafka configuration."""
        base_config = {
            'bootstrap.servers': self.bootstrap_servers,
            'security.protocol': self.security_protocol,
            'client.id': socket.gethostname(),
        }
        
        if self.sasl_mechanism and self.sasl_username and self.sasl_password:
            base_config.update({
                'sasl.mechanism': self.sasl_mechanism,
                'sasl.username': self.sasl_username,
                'sasl.password': self.sasl_password,
            })
            
        self._producer_config = base_config.copy()
        
        self._consumer_config = base_config.copy()
        self._consumer_config.update({
            'group.id': 'chorus-backend-group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,  # We will commit manually for reliability
        })

    def _initialize_producer(self):
        """Initialize Kafka producer."""
        try:
            self.producer = Producer(self._producer_config)
            agent_logger.log_agent_action(
                "INFO",
                "Kafka producer initialized",
                action_type="kafka_init"
            )
        except Exception as e:
            agent_logger.log_system_error(e, "kafka_client", "init_producer")
            self.enabled = False

    @retry_with_exponential_backoff(max_retries=3, base_delay=0.1, exceptions=(KafkaOperationError,))
    def produce(self, topic: str, value: Dict[str, Any], key: Optional[str] = None, headers: Optional[Dict[str, str]] = None) -> None:
        """
        Produce a message to a Kafka topic.
        
        Args:
            topic: Target topic
            value: Message body (will be JSON serialized)
            key: Message key (optional)
            headers: Message headers (optional)
        """
        if not self.enabled or not self.producer:
            # If disabled, just log (or could raise error depending on requirement)
            # For now we log warning to avoid crashing logic that expects it to work if configured off
            if settings.kafka.enabled: 
                agent_logger.log_agent_action("WARNING", "Kafka producer not available", action_type="kafka_produce_skipped")
            return

        @self.circuit_breaker
        def _do_produce():
            try:
                # Callback for delivery reports
                def delivery_report(err, msg):
                    if err is not None:
                        agent_logger.log_system_error(
                            Exception(f"Message delivery failed: {err}"), 
                            "kafka_client", 
                            "delivery_report",
                            context={"topic": topic}
                        )
                    else:
                        # Success logging (debug level to avoid spam)
                        pass

                # Serialize value
                json_value = json.dumps(value).encode('utf-8')
                encoded_key = key.encode('utf-8') if key else None
                
                # Convert headers to list of tuples if present
                kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()] if headers else None

                self.producer.produce(
                    topic,
                    value=json_value,
                    key=encoded_key,
                    headers=kafka_headers,
                    callback=delivery_report
                )
                
                # Trigger any available delivery report callbacks from previous produce() calls
                self.producer.poll(0)
                
            except Exception as e:
                raise KafkaOperationError(
                    f"Failed to produce message to {topic}: {str(e)}",
                    component="kafka_client",
                    operation="produce",
                    context={"topic": topic}
                ) from e

        _do_produce()

    def subscribe(self, topics: List[str]):
        """
        Subscribe consumer to topics.
        """
        if not self.enabled:
            return

        if not self.consumer:
            try:
                self.consumer = Consumer(self._consumer_config)
            except Exception as e:
                agent_logger.log_system_error(e, "kafka_client", "init_consumer")
                return

        try:
            self.consumer.subscribe(topics)
            agent_logger.log_agent_action("INFO", f"Subscribed to topics: {topics}", action_type="kafka_subscribe")
        except Exception as e:
            agent_logger.log_system_error(e, "kafka_client", "subscribe")

    def poll(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Poll for new messages.
        
        Returns:
            Dictionary with message data (value, key, topic, partition, offset) or None
        """
        if not self.consumer:
            return None

        try:
            msg = self.consumer.poll(timeout)
            
            if msg is None:
                return None
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    return None
                else:
                    agent_logger.log_system_error(
                        Exception(msg.error()), 
                        "kafka_client", 
                        "poll_error"
                    )
                    return None
            
            # Deserialize value
            try:
                value = json.loads(msg.value().decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Return raw bytes if not JSON
                value = msg.value()
                
            return {
                "value": value,
                "key": msg.key().decode('utf-8') if msg.key() else None,
                "topic": msg.topic(),
                "partition": msg.partition(),
                "offset": msg.offset(),
                "timestamp": msg.timestamp()[1] # (type, timestamp)
            }
            
        except Exception as e:
            agent_logger.log_system_error(e, "kafka_client", "poll")
            return None

    def commit(self, asynchronous: bool = True):
        """Commit offsets."""
        if self.consumer:
            try:
                self.consumer.commit(asynchronous=asynchronous)
            except Exception as e:
                 agent_logger.log_system_error(e, "kafka_client", "commit")

    def close(self):
        """Close producer and consumer."""
        if self.producer:
            self.producer.flush()
        if self.consumer:
            self.consumer.close()

    def flush(self, timeout: float = 10.0) -> int:
        """Flush producer queue."""
        if self.producer:
            return self.producer.flush(timeout)
        return 0

    def create_topics(self, topics: List[str], num_partitions: int = 1, replication_factor: int = 1):
        """
        Create topics if they don't exist.
        
        Args:
            topics: List of topic names
            num_partitions: Number of partitions
            replication_factor: Replication factor
        """
        if not self.enabled or not AdminClient:
            return

        admin_client = AdminClient(self._producer_config)
        
        new_topics = [
            NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)
            for topic in topics
        ]
        
        # Call create_topics to asynchronously create topics.
        fs = admin_client.create_topics(new_topics)

        # Wait for each operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                agent_logger.log_agent_action(
                    "INFO", 
                    f"Topic created: {topic}", 
                    action_type="kafka_topic_create"
                )
            except Exception as e:
                # Continue if topic already exists
                if "TopicExists" in str(e) or (hasattr(e, 'args') and "TOPIC_ALREADY_EXISTS" in str(e.args[0])):
                    pass 
                else:
                    agent_logger.log_system_error(e, "kafka_client", "create_topics", context={"topic": topic})

# Global instance
kafka_bus = KafkaMessageBus()
