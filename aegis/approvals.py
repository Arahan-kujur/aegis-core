"""
Web-based human-in-the-loop approval system for risky actions.

This module provides a minimal FastAPI web server for approving actions.
Execution blocks until a human approves or denies via the web interface.
"""

import uuid
import threading
from typing import Dict, Optional
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

# Global in-memory store for pending approvals
_pending_approvals: Dict[str, Dict] = {}
_approval_results: Dict[str, Optional[bool]] = {}
_approval_events: Dict[str, threading.Event] = {}

# FastAPI app instance
app = FastAPI()


@app.get("/approve/{approval_id}", response_class=HTMLResponse)
async def get_approval_page(approval_id: str):
    """
    Display approval page with action details and approve/deny buttons.
    """
    if approval_id not in _pending_approvals:
        return HTMLResponse("<h1>Approval not found</h1>", status_code=404)
    
    action = _pending_approvals[approval_id]
    action_name = action.get("action_name", "unknown")
    cost = action.get("cost", 0.0)
    details = action.get("details", {})
    
    # Simple HTML with approve/deny buttons
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aegis Approval</title>
    </head>
    <body>
        <h1>AEGIS: Action requires human approval</h1>
        <hr>
        <p><strong>Action:</strong> {action_name}</p>
        <p><strong>Cost:</strong> ${cost:.2f}</p>
        <p><strong>Details:</strong> {details}</p>
        <hr>
        <form method="post" action="/approve/{approval_id}">
            <input type="hidden" name="decision" value="approve">
            <button type="submit" style="background-color: green; color: white; padding: 10px 20px; font-size: 16px;">Approve</button>
        </form>
        <br>
        <form method="post" action="/approve/{approval_id}">
            <input type="hidden" name="decision" value="deny">
            <button type="submit" style="background-color: red; color: white; padding: 10px 20px; font-size: 16px;">Deny</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(html)


@app.post("/approve/{approval_id}")
async def post_approval_decision(approval_id: str, decision: str = Form(...)):
    """
    Record approval decision and unblock waiting agent.
    """
    if approval_id not in _pending_approvals:
        return HTMLResponse("<h1>Approval not found</h1>", status_code=404)
    
    # Record decision
    approved = decision.lower() == "approve"
    _approval_results[approval_id] = approved
    
    # Unblock the waiting agent
    if approval_id in _approval_events:
        _approval_events[approval_id].set()
    
    # Clean up
    del _pending_approvals[approval_id]
    
    result_text = "APPROVED" if approved else "DENIED"
    return HTMLResponse(f"<h1>Action {result_text}</h1><p>You can close this window.</p>")


def _start_server():
    """Start the FastAPI server in a background thread."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    return thread


# Start server on module import
_server_thread = None
if _server_thread is None:
    _server_thread = _start_server()


def request_approval(action: dict) -> bool:
    """
    Request human approval for a risky action via web interface.
    
    This function blocks execution, creates a web approval page,
    and waits for human input to approve or deny.
    
    Args:
        action: Dictionary containing action details including:
            - action_name: Name of the action (e.g., "spend_money")
            - cost: The cost associated with the action
            - details: Additional details about the action
            
    Returns:
        True if approved, False if denied
    """
    # Generate unique approval ID
    approval_id = str(uuid.uuid4())
    
    # Store action in memory
    _pending_approvals[approval_id] = action
    
    # Create event to block until decision is made
    event = threading.Event()
    _approval_events[approval_id] = event
    
    # Print approval URL to console
    url = f"http://127.0.0.1:8000/approve/{approval_id}"
    print(f"\n{'=' * 60}")
    print("AEGIS: Action requires human approval")
    print(f"Visit: {url}")
    print("=" * 60)
    
    # Block execution until approval is received
    event.wait()
    
    # Get the result
    result = _approval_results.pop(approval_id, False)
    del _approval_events[approval_id]
    
    return result
