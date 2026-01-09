"""
Simple append-only logging for intercepted actions.

Logs all decision points to a local JSONL file.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


LOG_FILE = Path("logs.jsonl")


def log_event(event: dict) -> None:
    """
    Append an event to the log file as JSON.
    
    Each event must include:
    - timestamp: When the event occurred
    - action_type: Type of action (e.g., "spend_money", "send_email")
    - risk: Risk level ("low", "medium", "high")
    - cost: Cost associated with the action (if applicable)
    - explanation: Explanation of why the action was auto-approved or requires approval
    - decision: One of "allowed", "paused", "approved", "denied"
    
    Args:
        event: Dictionary containing event data
    """
    # Ensure event has required fields
    log_entry = {
        "timestamp": event.get("timestamp", datetime.utcnow().isoformat()),
        "action_type": event.get("action_type", "unknown"),
        "risk": event.get("risk", "unknown"),
        "cost": event.get("cost", 0.0),
        "decision": event.get("decision", "unknown")
    }
    
    # Add any additional fields from the event
    for key, value in event.items():
        if key not in log_entry:
            log_entry[key] = value
    
    # Append to log file (create if doesn't exist)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

