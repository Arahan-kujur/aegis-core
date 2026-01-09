# Architecture

## Flow Diagram

```
Agent → Aegis Wrapper → Rule Check → Allow OR Pause → Human → Continue
```

### Explanation

1. **Agent**: An existing LangChain agent that makes tool calls
2. **Aegis Wrapper**: Intercepts tool calls before execution
3. **Rule Check**: Evaluates if the action meets risky criteria (e.g., cost threshold)
4. **Allow OR Pause**: 
   - If safe: Allow the action to proceed
   - If risky: Pause execution
5. **Human**: Human reviews the paused action
6. **Continue**: Based on human decision (approve/deny), execution continues or stops

