"""
Property-based tests for Kafka integration.

**Feature: Real-Time Data Flow**
**Validates: Requirements 1.2, 1.3, 1.5**
"""
import pytest
import json
from unittest.mock import MagicMock, patch, ANY
from hypothesis import given, strategies as st, settings, HealthCheck

from src.integrations.kafka_client import KafkaMessageBus, KafkaOperationError
from src.error_handling import CircuitBreaker

@pytest.fixture
def mock_kafka_deps():
    with patch('src.integrations.kafka_client.Producer') as MockProducer, \
         patch('src.integrations.kafka_client.Consumer') as MockConsumer:
        yield MockProducer, MockConsumer

class TestKafkaIntegration:
    
    @given(
        topic=st.text(min_size=1, alphabet='abcdefghijklmnopqrstuvwxyz'),
        message=st.dictionaries(keys=st.text(min_size=1), values=st.text(min_size=1)),
        key=st.one_of(st.none(), st.text(min_size=1))
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_message_serialization_round_trip(self, mock_kafka_deps, topic, message, key):
        """
        Property 1: Message serialization round trip.
        Validates: Requirements 1.2
        """
        MockProducer, MockConsumer = mock_kafka_deps
        
        # Setup
        kafka_bus = KafkaMessageBus()
        # Force enable
        kafka_bus.enabled = True
        kafka_bus.producer = MockProducer.return_value
        
        # Act - Produce
        kafka_bus.produce(topic, message, key=key)
        
        # Assert - Verify serialization
        expected_value = json.dumps(message).encode('utf-8')
        expected_key = key.encode('utf-8') if key else None
        
        kafka_bus.producer.produce.assert_called_with(
            topic,
            value=expected_value,
            key=expected_key,
            headers=None,
            callback=ANY
        )

        # Mock Consumer behavior for deserialization check
        kafka_bus.consumer = MockConsumer.return_value
        
        # Mock message object
        mock_msg = MagicMock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = expected_value
        mock_msg.key.return_value = expected_key
        mock_msg.topic.return_value = topic
        mock_msg.partition.return_value = 0
        mock_msg.offset.return_value = 1
        mock_msg.timestamp.return_value = (1, 1000)
        
        kafka_bus.consumer.poll.return_value = mock_msg
        
        # Act - Poll
        result = kafka_bus.poll(timeout=0.1)
        
        # Assert - Verify deserialization
        assert result is not None
        assert result['value'] == message
        assert result['key'] == key
        assert result['topic'] == topic

    @given(
        fail_count=st.integers(min_value=1, max_value=4)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_property_kafka_error_handling_retry(self, mock_kafka_deps, fail_count):
        """
        Property 2: Kafka error handling with retry.
        Validates: Requirements 1.3
        
        Verify that produce operation retries on failure.
        """
        MockProducer, _ = mock_kafka_deps
        # Reset mock for hypothesis iteration
        MockProducer.return_value.reset_mock()
        
        kafka_bus = KafkaMessageBus()
        kafka_bus.enabled = True
        kafka_bus.producer = MockProducer.return_value
        
        # Reset circuit breaker
        kafka_bus.circuit_breaker = CircuitBreaker(
            failure_threshold=10, 
            recovery_timeout=0.1, 
            expected_exception=(KafkaOperationError, Exception)
        )
        
        # Setup mock to fail N times then succeed
        # Note: retry_with_exponential_backoff catches KafkaOperationError.
        # But KafkaMessageBus.produce catches generic Exception and raises KafkaOperationError.
        # So we can raise generic Exception from producer.produce
        
        side_effects = [Exception("Kafka Error")] * fail_count + [None]
        kafka_bus.producer.produce.side_effect = side_effects
        
        # We need to mock the logger to avoid spamming output and verify retries?
        # Ideally we just check call count.
        
        # However, retry_with_exponential_backoff has max_retries=3.
        # If fail_count > 3, it should raise.
        
        if fail_count <= 3:
            kafka_bus.produce("test-topic", {"data": "test"})
            # Should have called fail_count + 1 times (failures + 1 success)
            assert kafka_bus.producer.produce.call_count == fail_count + 1
        else:
            with pytest.raises(KafkaOperationError):
                kafka_bus.produce("test-topic", {"data": "test"})
            # Should have called max_retries + 1 times (3 + 1 = 4)
            assert kafka_bus.producer.produce.call_count == 4

    def test_circuit_breaker_activation(self, mock_kafka_deps):
        """
        Test that circuit breaker opens after threshold.
        """
        MockProducer, _ = mock_kafka_deps
        kafka_bus = KafkaMessageBus()
        kafka_bus.enabled = True
        kafka_bus.producer = MockProducer.return_value
        
        # Configure sensitive breaker
        kafka_bus.circuit_breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=60,
            expected_exception=(KafkaOperationError,)
        )
        
        kafka_bus.producer.produce.side_effect = Exception("Persistent Error")
        
        # 1. Failure 1
        with pytest.raises(KafkaOperationError):
            kafka_bus.produce("topic", {})
            
        # 2. Failure 2 (Threshold reached, state becomes OPEN)
        with pytest.raises(KafkaOperationError):
            kafka_bus.produce("topic", {})
            
        assert kafka_bus.circuit_breaker.state == "OPEN"
        
        # 3. Next call should be blocked immediately (SystemRecoveryError wrapped or raised)
        # Note: CircuitBreaker raises SystemRecoveryError, but produce might wrap it?
        # produce wraps _do_produce. CircuitBreaker protects _do_produce.
        # So SystemRecoveryError propagates up.
        
        from src.error_handling import SystemRecoveryError
        
        # Retry decorator might catch SystemRecoveryError?
        # No, retry expects (KafkaOperationError,). SystemRecoveryError is ChorusError.
        
        with pytest.raises(SystemRecoveryError):
            kafka_bus.produce("topic", {})
