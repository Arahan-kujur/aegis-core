"""
Demo script for Aegis v1.

Demonstrates:
- Auto-approved action (cost <= limit)
- Approval-required action (cost > limit)
- Web-based approval flow
- Logging to logs.jsonl
"""

import time
from aegis.wrapper import AegisWrapper


class MockAgent:
    """Mock agent for demonstration purposes."""
    
    def __init__(self):
        self.name = "MockAgent"
    
    def run(self, input_text: str):
        """Simulate agent execution."""
        return f"Agent processed: {input_text}"


def main():
    print("=" * 60)
    print("AEGIS v1 DEMO")
    print("=" * 60)
    print()
    
    # Create mock agent
    agent = MockAgent()
    
    # Wrap with Aegis (cost limit: $100)
    print("Initializing Aegis wrapper with cost_limit=$100.00")
    wrapped = AegisWrapper(agent, cost_limit=100.0)
    print()
    
    # Demo 1: Auto-approved action (cost <= limit)
    print("-" * 60)
    print("DEMO 1: Auto-approved action")
    print("-" * 60)
    print("Simulating spend_money action with cost=$50.00")
    print("(This should be auto-approved and logged)")
    print()
    
    # Simulate tool call interception
    approved = wrapped._intercept_tool_call(
        tool_name="spend_money",
        tool_input={"cost": 50.0, "description": "API call"}
    )
    
    if approved:
        print("✓ Action was auto-approved (cost <= limit)")
    print()
    time.sleep(1)
    
    # Demo 2: Approval-required action (cost > limit)
    print("-" * 60)
    print("DEMO 2: Approval-required action")
    print("-" * 60)
    print("Simulating spend_money action with cost=$150.00")
    print("(This requires human approval via web interface)")
    print()
    print("NOTE: Execution will pause until you approve/deny")
    print("      Visit the URL shown below in your browser")
    print()
    
    # Simulate tool call interception
    approved = wrapped._intercept_tool_call(
        tool_name="spend_money",
        tool_input={"cost": 150.0, "description": "Expensive API call"}
    )
    
    if approved:
        print("✓ Action was approved by human")
    else:
        print("✗ Action was denied by human")
    print()
    
    # Summary
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("Check logs.jsonl for event log entries:")
    print("  - allowed: Auto-approved actions")
    print("  - paused: Actions requiring approval")
    print("  - approved: Human-approved actions")
    print("  - denied: Human-denied actions")
    print()


if __name__ == "__main__":
    main()

