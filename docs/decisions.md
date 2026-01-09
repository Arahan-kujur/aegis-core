# Architecture Decisions

## Decision: Only intercept actions (tool calls), not prompts
**Reason**: Prompts are cheap; actions cause real-world damage.

## Decision: Risk-based evaluation with three levels
**Reason**: Simple, deterministic classification that maps cleanly to approval requirements.
- Low/Medium risk: Auto-approved (no human intervention needed)
- High risk: Requires human approval

## Decision: Deterministic explanations for all risk decisions
**Reason**: Humans need to understand why an action was auto-approved or requires approval. Explanations are generated from rule evaluation logic, not LLMs.

## Decision: Externalize rules in rules.py
**Reason**: Allows users to customize risk evaluation without modifying wrapper logic. Rules are plain Python dictionaries, not configuration files.

## Decision: Single approval flow for all high-risk actions
**Reason**: Keeps the system simple. All action types use the same web-based approval interface, regardless of action type.

## Decision: Append-only JSONL logging
**Reason**: Simple, human-readable format that preserves all decision context including explanations. No aggregation or analysis needed.
