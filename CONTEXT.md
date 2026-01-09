---
# Aegis – Project Context

## What this is
Aegis is a human-in-the-loop control layer for AI agents.
It wraps existing LangChain-style agents and intercepts risky actions
(e.g. spending money), pauses execution, and asks a human to approve
or deny before continuing.

## What this is NOT
- Not an agent framework
- Not a workflow builder
- Not a model host
- Not autonomous by default

## Core concepts
- Agent: an existing LangChain agent
- Action: a tool call with real-world side effects
- Rule: simple thresholds (e.g. cost > X)
- Human approval: pause + approve/deny
- Log: record of every intercepted action

## v1 scope
- LangChain only
- One risky action: spending money
- One human approval flow
- Simple rule-based checks
---

