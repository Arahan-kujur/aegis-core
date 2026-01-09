"""
Read-only audit log viewer for Aegis.

Displays all logged decisions in a simple HTML table.
No authentication, filtering, or pagination.
"""

import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

LOG_FILE = Path("logs.jsonl")
app = FastAPI()


@app.get("/audit", response_class=HTMLResponse)
async def view_audit_log():
    """
    Display all audit log entries in a simple HTML table.
    """
    entries = []
    
    # Read log file if it exists
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
    
    # Sort by timestamp (newest first)
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Build HTML table
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aegis Audit Log</title>
        <style>
            body { font-family: monospace; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>Aegis Audit Log</h1>
        <p>Total entries: """ + str(len(entries)) + """</p>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Action Type</th>
                <th>Risk</th>
                <th>Cost</th>
                <th>Decision</th>
                <th>Approved By</th>
                <th>Explanation</th>
                <th>Policy Version</th>
            </tr>
    """
    
    for entry in entries:
        timestamp = entry.get("timestamp", "unknown")
        action_type = entry.get("action_type", "unknown")
        risk = entry.get("risk", "unknown")
        cost = entry.get("cost", 0.0)
        decision = entry.get("decision", "unknown")
        approved_by = entry.get("approved_by", "-")
        explanation = entry.get("explanation", "No explanation")
        policy_version = entry.get("policy_version", "unknown")
        
        html += f"""
            <tr>
                <td>{timestamp}</td>
                <td>{action_type}</td>
                <td>{risk}</td>
                <td>${cost:.2f}</td>
                <td>{decision}</td>
                <td>{approved_by}</td>
                <td>{explanation}</td>
                <td>{policy_version}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return HTMLResponse(html)


if __name__ == "__main__":
    print("Starting Aegis Audit Viewer...")
    print("Open http://127.0.0.1:8001/audit in your browser")
    uvicorn.run(app, host="127.0.0.1", port=8001)

