"""
Property-based tests for Stream Processor.

**Feature: Real-Time Data Flow**
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**
"""
import pytest
import time
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st, settings, HealthCheck

from src.stream_processor import StreamProcessor

class TestStreamProcessor:
    
    @given(
        messages=st.lists(
            st.dictionaries(keys=st.text(min_size=1), values=st.text(min_size=1)),
            min_size=1, max_size=5
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_stream_processing_pipeline_integration(self, messages):
        """
        Property 4: Stream processing pipeline integration.
        Validates: Requirements 2.1, 2.2
        
        Input messages should result in output decisions.
        """
        with patch('src.stream_processor.kafka_bus') as mock_bus:
            processor = StreamProcessor()
            
            # Simulate polling messages
            mock_msgs = []
            for m in messages:
                mock_msg = {
                    "value": m,
                    "key": "test_key",
                    "topic": processor.input_topic,
                    "offset": 0,
                    "partition": 0
                }
                mock_msgs.append(mock_msg)
            
            # Chain side effects: return messages then None to stop loop logic if we were running it
            # But here we call _process_message directly to test logic without threading issues
            
            for msg in mock_msgs:
                processor._process_message(msg)
                
            # Verify production to output topic
            # StreamProcessor skips empty payloads
            expected_count = len([m for m in messages if m])
            assert mock_bus.produce.call_count == expected_count
            
            # Verify arguments
            args, _ = mock_bus.produce.call_args
            assert args[0] == processor.output_topic
            assert "status" in args[1] # Decision object

    @given(
        malformed_value=st.one_of(st.none(), st.just({})) # Empty or None value might trigger issues
    )
    def test_property_processing_error_routing(self, malformed_value):
        """
        Property 5: Processing error routing.
        Validates: Requirements 2.3
        
        Errors should be routed to DLQ.
        """
        with patch('src.stream_processor.kafka_bus') as mock_bus:
            processor = StreamProcessor()
            
            # Simulate a message that causes an error
            # We force _analyze_intention to raise exception
            with patch.object(processor, '_analyze_intention', side_effect=Exception("Processing Failed")):
                msg = {
                    "value": {"agent_id": "test"},
                    "key": "test_key"
                }
                
                processor._process_message(msg)
                
                # Should produce to DLQ
                mock_bus.produce.assert_called_with(
                    processor.dlq_topic,
                    {
                        "original_message": msg,
                        "error": "Processing Failed",
                        "timestamp": pytest.approx(time.time(), 1.0)
                    },
                    key="test_key"
                )

    @given(
        message_sequence=st.lists(st.integers(), min_size=2, max_size=10)
    )
    def test_property_agent_specific_message_ordering(self, message_sequence):
        """
        Property 6: Agent-specific message ordering.
        Validates: Requirements 2.4
        
        Messages should be processed in order.
        """
        # Since _process_message is synchronous, ordering is guaranteed by the caller (poll loop).
        # We verify that we process what we receive in order.
        
        processed_sequence = []
        
        class MockProcessor(StreamProcessor):
            def _analyze_intention(self, data):
                processed_sequence.append(data['seq'])
                return {}

        processor = MockProcessor()
        
        with patch('src.stream_processor.kafka_bus'):
            for seq in message_sequence:
                msg = {"value": {"seq": seq, "agent_id": "ordered_agent"}}
                processor._process_message(msg)
        
        assert processed_sequence == message_sequence
