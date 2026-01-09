# Architecture

## Flow Diagram

```
Agent → Aegis Wrapper → Normalize Action → Evaluate Risk → 
  → Low/Medium Risk: Auto-approve → Log → Continue
  → High Risk: Pause → Human Approval → Log → Continue/Stop
```

### Detailed Flow

1. **Agent**: An existing LangChain agent that makes tool calls
2. **Aegis Wrapper**: Intercepts tool calls before execution
3. **Normalize Action**: Converts tool call to standard format (type, risk, metadata)
4. **Evaluate Risk**: Uses rules system to determine risk level and explanation
   - Calls `aegis.rules.evaluate_risk()` with action and cost_limit
   - Returns tuple: (risk_level, explanation)
5. **Risk Check**:
   - **Low/Medium Risk**: Auto-approve, log with explanation, continue execution
   - **High Risk**: Pause execution, log with explanation, request human approval
6. **Human Approval** (for high risk only):
   - FastAPI web server displays action details and explanation
   - Human reviews and approves or denies
   - Decision is logged with explanation
7. **Continue/Stop**: Based on human decision, execution resumes or stops

## Action Format

Actions are normalized to a standard format:

```python
{
    "type": "spend_money",  # Action type
    "risk": "high",         # Risk level: "low", "medium", or "high"
    "explanation": "...",   # Deterministic explanation
    "metadata": {...}       # Action-specific details
}
```

## Risk Evaluation

Risk is evaluated using `aegis.rules.evaluate_risk()`:

- **Cost-based rules** (e.g., spend_money): Risk calculated from cost thresholds
- **Fixed rules** (e.g., send_email): Risk level is pre-configured
- **Default rule**: Unknown actions default to "low" risk

Only "high" risk actions require human approval.

## Rules System

Rules are defined in `aegis/rules.py` as a Python dictionary (`DEFAULT_RULES`):

- Rules can be customized by modifying `DEFAULT_RULES`
- Two rule types: `"cost_based"` and `"fixed"`
- Rules are evaluated deterministically with explanations

## Logging

All decisions are logged to `logs.jsonl` with:
- timestamp
- action_type
- risk
- cost (if applicable)
- explanation
- decision ("allowed", "paused", "approved", "denied")
