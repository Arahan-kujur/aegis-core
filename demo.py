"""
Demo script for Aegis.

This demo shows how Aegis intercepts risky actions and requires human approval.
"""

import time
from aegis.wrapper import AegisWrapper


class ExampleAgent:
    """Example agent that makes tool calls with real-world side effects."""
    
    def __init__(self):
        self.name = "ExampleAgent"
    
    def run(self, input_text: str):
        """Simulate agent execution."""
        return f"Agent processed: {input_text}"


def main():
    print("=" * 70)
    print("AEGIS DEMO - Human-in-the-Loop Control for AI Agents")
    print("=" * 70)
    print()
    
    # Create example agent
    agent = ExampleAgent()
    
    # Wrap with Aegis (cost limit: $100)
    print("Setting up Aegis with cost_limit=$100.00")
    print("(Actions costing more than $200 require human approval)")
    print()
    wrapped = AegisWrapper(agent, cost_limit=100.0)
    
    # Action 1: Auto-approved action
    print("-" * 70)
    print("ACTION 1: Low-cost operation (auto-approved)")
    print("-" * 70)
    print("Agent wants to spend $50.00 on an API call")
    print("→ Cost is below threshold → Auto-approved")
    print()
    
    # Simulate tool call interception
    approved = wrapped._intercept_tool_call(
        tool_name="spend_money",
        tool_input={"cost": 50.0, "description": "API call"}
    )
    
    print("✓ Action auto-approved and logged")
    print()
    time.sleep(1)
    
    # Action 2: High-risk action requiring approval
    print("-" * 70)
    print("ACTION 2: High-cost operation (requires approval)")
    print("-" * 70)
    print("Agent wants to spend $250.00 on an expensive API call")
    print("→ Cost exceeds threshold → Human approval required")
    print()
    print("⏸  EXECUTION PAUSED - Waiting for human decision")
    print()
    print("📋 NEXT STEPS:")
    print("   1. A URL will appear below")
    print("   2. Open that URL in your browser")
    print("   3. Review the action details and explanation")
    print("   4. Enter your name/email and click Approve or Deny")
    print("   5. Execution will resume automatically")
    print()
    
    # Simulate tool call interception
    approved = wrapped._intercept_tool_call(
        tool_name="spend_money",
        tool_input={"cost": 250.0, "description": "Expensive API call"}
    )
    
    print()
    print("▶  EXECUTION RESUMED")
    if approved:
        print("✓ Action was approved by human")
    else:
        print("✗ Action was denied by human")
    print()
    time.sleep(1)
    
    # Action 3: Data-destructive action requiring approval
    print("-" * 70)
    print("ACTION 3: Data-destructive operation (requires approval)")
    print("-" * 70)
    print("Agent wants to delete data from the database")
    print("→ Data deletion is irreversible → Human approval required")
    print()
    print("⏸  EXECUTION PAUSED - Waiting for human decision")
    print()
    print("📋 NEXT STEPS:")
    print("   1. A URL will appear below")
    print("   2. Open that URL in your browser")
    print("   3. Review the action details and explanation")
    print("   4. Enter your name/email and click Approve or Deny")
    print("   5. Execution will resume automatically")
    print()
    
    # Simulate tool call interception
    approved = wrapped._intercept_tool_call(
        tool_name="delete_data",
        tool_input={"table": "users", "condition": "status='inactive'", "count": 150}
    )
    
    print()
    print("▶  EXECUTION RESUMED")
    if approved:
        print("✓ Action was approved by human")
    else:
        print("✗ Action was denied by human")
    print()
    
    # Summary
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("📊 Check logs.jsonl to see all logged events:")
    print("   - allowed: Auto-approved actions")
    print("   - paused: Actions that required approval")
    print("   - approved: Human-approved actions")
    print("   - denied: Human-denied actions")
    print()


if __name__ == "__main__":
    main()

