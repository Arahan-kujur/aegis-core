---
# Aegis – Project Context

## What this is
Aegis is a human-in-the-loop control layer for AI agents.
It wraps existing LangChain-style agents and intercepts risky actions
(e.g. spending money, sending emails, calling APIs), evaluates their risk,
and asks a human to approve or deny high-risk actions before continuing.

## What this is NOT
- Not an agent framework
- Not a workflow builder
- Not a model host
- Not autonomous by default

## Core concepts
- Agent: an existing LangChain agent
- Action: a tool call with real-world side effects
- Risk level: "low", "medium", or "high" (determines if approval is needed)
- Rule: configuration that maps actions to risk levels
- Explanation: deterministic reason for risk assignment
- Human approval: pause + approve/deny via web interface
- Log: record of every intercepted action with explanation

## v1 scope
- LangChain-style agents
- Multiple action types (spend_money, send_email, call_api, and extensible)
- Risk-based evaluation (low/medium auto-approved, high requires approval)
- Rules system (externalized in rules.py)
- Web-based approval flow (FastAPI)
- Deterministic explanations for all decisions
- Append-only JSONL logging
---
