"""
Aegis Wrapper - Intercepts risky actions from LangChain agents.

This wrapper intercepts tool calls, checks them against rules,
and pauses execution for human approval when needed.

Action Format:
Actions are represented as dictionaries with the following structure:
- type (str): Action type (e.g., "spend_money", "send_email", "call_api")
- risk (str): Risk level - "low", "medium", or "high"
- metadata (dict): Action-specific details (e.g., cost, recipient, endpoint)
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
    
    def _normalize_action(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert tool call to normalized action format.
        
        For spend_money: maps cost to risk level based on cost_limit.
        For other actions: expects action dict with type, risk, metadata.
        
        Args:
            tool_name: Name of the tool being called
            tool_input: Arguments passed to the tool
            
        Returns:
            Normalized action dict with type, risk, metadata
        """
        # Handle spend_money: map cost to risk level
        if tool_name == "spend_money":
            cost = tool_input.get("cost", 0.0)
            # Map cost thresholds to risk levels
            if cost <= self.cost_limit:
                risk = "low"
            elif cost <= self.cost_limit * 2:
                risk = "medium"
            else:
                risk = "high"
            
            return {
                "type": "spend_money",
                "risk": risk,
                "metadata": tool_input
            }
        
        # For other actions, expect normalized format
        # If already in normalized format, return as-is
        if "type" in tool_input and "risk" in tool_input and "metadata" in tool_input:
            return tool_input
        
        # Default: treat as low risk if format is unknown
        return {
            "type": tool_name,
            "risk": "low",
            "metadata": tool_input
        }
    
    def _intercept_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """
        Intercept and check a tool call before execution.
        
        Supports both legacy spend_money format and new generic action format.
        Only actions with risk == "high" require approval.
        
        Args:
            tool_name: Name of the tool being called
            tool_input: Arguments passed to the tool (or normalized action dict)
            
        Returns:
            True if the action should proceed, False if denied
        """
        # Normalize action to standard format
        action = self._normalize_action(tool_name, tool_input)
        
        action_type = action["type"]
        risk = action["risk"]
        metadata = action["metadata"]
        
        # Extract cost for logging (if present)
        cost = metadata.get("cost", 0.0) if isinstance(metadata, dict) else 0.0
        
        # Rule check: only "high" risk requires approval
        if risk != "high":
            # Auto-approve low and medium risk actions
            log_event({
                "timestamp": datetime.utcnow().isoformat(),
                "action_type": action_type,
                "risk": risk,
                "cost": cost,
                "decision": "allowed"
            })
            return True
        
        # High risk: pause and request human approval
        log_event({
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "risk": risk,
            "cost": cost,
            "decision": "paused"
        })
        
        # Convert to format expected by request_approval
        # Maintain backward compatibility with spend_money
        if action_type == "spend_money":
            action_dict = {
                "action_name": action_type,
                "cost": cost,
                "details": metadata
            }
        else:
            # Generic action format for approval UI
            action_dict = {
                "action_name": action_type,
                "cost": cost if cost > 0 else 0.0,
                "details": metadata
            }
        
        approved = request_approval(action_dict)
        
        # Log human decision
        log_event({
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "risk": risk,
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
        
        Now intercepts all tool calls to check for risk levels.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if this tool should be checked
        """
        return True

