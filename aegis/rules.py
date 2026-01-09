"""
Rules module for Aegis.

Defines risk evaluation rules for different action types.
Rules are simple Python dictionaries that can be customized.
"""

from typing import Dict, Any, Tuple

# Policy version constant
POLICY_VERSION = "v1"

# Default rules that reproduce current v2 behavior
DEFAULT_RULES = {
    "spend_money": {
        "type": "cost_based",
        "low_threshold": None,  # Will be set from cost_limit
        "medium_threshold": None,  # Will be set from cost_limit * 2
        # cost <= low_threshold → low risk
        # low_threshold < cost <= medium_threshold → medium risk
        # cost > medium_threshold → high risk
    },
    "send_email": {
        "type": "fixed",
        "risk": "medium"
    },
    "call_api": {
        "type": "fixed",
        "risk": "medium"
    },
    # Default for unknown action types
    "_default": {
        "type": "fixed",
        "risk": "low"
    }
}


def evaluate_risk(action: dict, rules: dict = None, cost_limit: float = 100.0) -> Tuple[str, str]:
    """
    Evaluate risk level for an action based on rules.
    
    Args:
        action: Action dict with "type" and "metadata" fields
        rules: Rules dictionary (defaults to DEFAULT_RULES)
        cost_limit: Cost limit for spend_money actions (defaults to 100.0)
        
    Returns:
        Tuple of (risk_level, explanation):
        - risk_level: "low", "medium", or "high"
        - explanation: Plain English explanation of the decision
    """
    if rules is None:
        rules = DEFAULT_RULES
    
    action_type = action.get("type", "unknown")
    metadata = action.get("metadata", {})
    
    # Get rule for this action type, or use default
    rule = rules.get(action_type, rules.get("_default", {"type": "fixed", "risk": "low"}))
    
    rule_type = rule.get("type", "fixed")
    
    if rule_type == "cost_based":
        # Handle spend_money: cost-based risk calculation
        cost = metadata.get("cost", 0.0) if isinstance(metadata, dict) else 0.0
        
        # Calculate thresholds from cost_limit
        low_threshold = cost_limit
        medium_threshold = cost_limit * 2
        
        if cost <= low_threshold:
            explanation = f"Cost ${cost:.2f} is within auto-approval threshold of ${low_threshold:.2f}"
            return ("low", explanation)
        elif cost <= medium_threshold:
            explanation = f"Cost ${cost:.2f} exceeds low threshold (${low_threshold:.2f}) but is within medium threshold (${medium_threshold:.2f})"
            return ("medium", explanation)
        else:
            explanation = f"Cost ${cost:.2f} exceeds approval threshold of ${medium_threshold:.2f}"
            return ("high", explanation)
    
    elif rule_type == "fixed":
        # Fixed risk level for action type
        risk = rule.get("risk", "low")
        explanation = f"Action type '{action_type}' is configured as {risk} risk"
        return (risk, explanation)
    
    else:
        # Unknown rule type, default to low
        explanation = f"Unknown action type '{action_type}', defaulting to low risk"
        return ("low", explanation)
