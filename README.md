# Aegis

Aegis is a human-in-the-loop control layer that wraps existing LangChain-style agents and intercepts risky actions before execution.

## Problem

AI agents can make tool calls with real-world side effects (e.g., spending money). Aegis pauses execution when risky actions are detected and requires human approval before continuing.

## How it works

- Wraps a LangChain agent and intercepts tool calls
- Checks actions against simple rules (e.g., cost threshold)
- If action is safe, allows execution automatically
- If action is risky, pauses execution and starts a web server
- Human visits a URL to review and approve/deny the action
- Execution resumes or stops based on the decision
- All decisions are logged to a local JSONL file

## Usage

```python
from aegis.wrapper import AegisWrapper

# Create your agent
agent = YourLangChainAgent()

# Wrap it with Aegis (cost_limit in dollars)
wrapped = AegisWrapper(agent, cost_limit=100.0)

# Run the agent
result = wrapped.run("your input")
```

When a `spend_money` tool call exceeds the cost limit, execution pauses and a URL is printed to the console. Visit the URL to approve or deny the action.

## What v1 does NOT include

- Authentication or authorization
- Database persistence (approvals are in-memory only)
- Multiple action types (only `spend_money` is intercepted)
- Configuration files
- Production deployment features
- Full LangChain integration (wrapper is a demonstration)
- Rules engine (rules are hardcoded in the wrapper)

## Running the demo

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

2. Run the demo:
   ```bash
   python demo.py
   ```

3. The demo will:
   - Trigger an auto-approved action (cost <= limit)
   - Trigger an approval-required action (cost > limit)
   - Print a URL to visit for approval
   - Write logs to `logs.jsonl`

The FastAPI server runs on `http://127.0.0.1:8000` automatically when needed.

