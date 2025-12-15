"""
Advanced pattern detection engine for identifying complex emergent behaviors.
"""
from typing import List, Dict, Any
from .models.core import AgentIntention
from ..mapper.models import GraphMetrics

class PatternDetector:
    """
    Detects complex patterns in agent behavior and interaction topology.
    """
    
    def detect_resource_hoarding(self, agent_id: str, history: List[Dict]) -> bool:
        """
        Detect if an agent is hoarding resources.
        Criterion: High frequency of high-priority requests for same resource without release.
        """
        if not history:
            return False
            
        # Simplified logic: Check if last 5 requests are for high resources
        recent = history[-5:]
        if len(recent) < 5:
            return False
            
        high_usage_count = sum(1 for h in recent if h.get('adjustment', 0) < -10) # Assuming negative adjustment implies consumption
        return high_usage_count >= 4

    def detect_communication_cascade(self, metrics: GraphMetrics) -> bool:
        """
        Detect if a communication cascade is occurring.
        Criterion: Sudden spike in edge count or density.
        """
        # In a real system, we'd compare against baseline.
        # Here we check if density is dangerously high for a sparse network
        return metrics.density > 0.8 and metrics.node_count > 5

    def detect_byzantine_behavior(self, agent_id: str, history: List[Dict]) -> bool:
        """
        Detect inconsistent/Byzantine behavior.
        Criterion: Alternating between cooperation (positive score) and conflict (negative score).
        """
        if len(history) < 4:
            return False
            
        # Check for sign flips in score adjustments
        flips = 0
        for i in range(1, len(history)):
            prev = history[i-1].get('adjustment', 0)
            curr = history[i].get('adjustment', 0)
            if (prev > 0 and curr < 0) or (prev < 0 and curr > 0):
                flips += 1
                
        # High volatility in behavior
        return flips >= 3

# Global instance
pattern_detector = PatternDetector()
