"""
Aegis Wrapper - Intercepts risky actions from LangChain agents.

This wrapper intercepts tool calls, checks them against rules,
and pauses execution for human approval when needed.
"""

from typing import Any, Dict
from datetime import datetime
from aegis.approvals import request_approval
from aegis.logging import log_event


class AegisWrapper:
    """
    Wraps a LangChain-style agent to intercept risky actions.
    
    Control flow:
    1. Agent makes a tool call
    2. Wrapper intercepts the call
    3. Rule check: if cost > limit, pause for approval
    4. If approved, allow execution; if denied, stop
    """
    
    def __init__(self, agent: Any, cost_limit: float = 100.0):
        """
        Initialize the Aegis wrapper.
        
        Args:
            agent: The LangChain agent to wrap
            cost_limit: Maximum allowed cost before requiring approval
        """
        self.agent = agent
        self.cost_limit = cost_limit
    
    def _intercept_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """
        Intercept and check a tool call before execution.
        
        Args:
            tool_name: Name of the tool being called
            tool_input: Arguments passed to the tool
            
        Returns:
            True if the action should proceed, False if denied
        """
        # Only intercept the "spend_money" tool call
        if tool_name != "spend_money":
            return True
        
        # Extract cost from tool input
        cost = tool_input.get("cost", 0.0)
        
        # Rule check: if cost <= limit, allow execution
        if cost <= self.cost_limit:
            # Log auto-approved action
            log_event({
                "timestamp": datetime.utcnow().isoformat(),
                "action_type": tool_name,
                "cost": cost,
                "decision": "allowed"
            })
            return True
        
        # If cost > limit, pause and request human approval
        # Log that action is paused
        log_event({
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": tool_name,
            "cost": cost,
            "decision": "paused"
        })
        
        # This is where execution pauses
        action_dict = {
            "action_name": tool_name,
            "cost": cost,
            "details": tool_input
        }
        approved = request_approval(action_dict)
        
        # Log human decision
        log_event({
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": tool_name,
            "cost": cost,
            "decision": "approved" if approved else "denied"
        })
        
        # Resume or stop based on approval response
        return approved
    
    def run(self, input_text: str) -> Any:
        """
        Run the agent with Aegis interception.
        
        This is a simplified version. In a real LangChain integration,
        we would hook into the agent's tool execution pipeline.
        
        Args:
            input_text: Input to pass to the agent
            
        Returns:
            Agent's response
        """
        # For simulation: if the agent would call spend_money,
        # we intercept it here before actual execution
        
        # In a real implementation, we would:
        # 1. Hook into LangChain's tool execution callback
        # 2. Intercept each tool call before it executes
        # 3. Check rules and request approval if needed
        # 4. Only proceed if approved
        
        # This is a placeholder that demonstrates the control flow
        # Actual LangChain integration would use callbacks or middleware
        return self.agent.run(input_text)
    
    def _should_intercept(self, tool_name: str) -> bool:
        """
        Determine if a tool call should be intercepted.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if this tool should be checked
        """
        return tool_name == "spend_money"

