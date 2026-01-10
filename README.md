# Aegis

Aegis is a human-in-the-loop control layer that wraps existing LangChain-style agents and intercepts risky actions before execution.

## 5-Minute Quickstart

Get Aegis running in under 5 minutes:

1. **Install the package:**
   ```bash
   pip install -e .
   ```

2. **Run the demo:**
   ```bash
   python demo.py
   ```

3. **When execution pauses**, open the approval URL in your browser (it will be printed to the console)

4. **Review the action** and enter your name/email, then click Approve or Deny

5. **View the logs:**
   ```bash
   cat logs.jsonl
   ```

That's it! You've seen Aegis in action.

## What You Will See When It Runs

### Console Output

When you run `demo.py`, you'll see output like this:

```
======================================================================
AEGIS DEMO - Human-in-the-Loop Control for AI Agents
======================================================================

Setting up Aegis with cost_limit=$100.00
(Actions costing more than $200 require human approval)

----------------------------------------------------------------------
ACTION 1: Low-cost operation (auto-approved)
----------------------------------------------------------------------
Agent wants to spend $50.00 on an API call
→ Cost is below threshold → Auto-approved

✓ Action auto-approved and logged

----------------------------------------------------------------------
ACTION 2: High-cost operation (requires approval)
----------------------------------------------------------------------
Agent wants to spend $250.00 on an expensive API call
→ Cost exceeds threshold → Human approval required

⏸  EXECUTION PAUSED - Waiting for human decision

📋 NEXT STEPS:
   1. A URL will appear below
   2. Open that URL in your browser
   3. Review the action details and explanation
   4. Enter your name/email and click Approve or Deny
   5. Execution will resume automatically

============================================================
AEGIS: Action requires human approval
Visit: http://127.0.0.1:8000/approve/550e8400-e29b-41d4-a716-446655440000
============================================================
```

### Approval Page

When you open the URL, you'll see a simple web page with:

- **Action**: spend_money
- **Cost**: $250.00
- **Reason**: "Cost $250.00 exceeds approval threshold of $200.00"
- **Details**: The action metadata
- **Two buttons**: 
  - Green "Approve" button (with required name/email field)
  - Red "Deny" button (with required name/email field)

After clicking Approve or Deny, you'll see a confirmation page and execution resumes.

### Log Entry

After the demo completes, `logs.jsonl` will contain entries like:

```json
{"timestamp": "2024-01-15T10:30:00", "policy_version": "v1", "action_type": "spend_money", "risk": "low", "cost": 50.0, "explanation": "Cost $50.00 is within auto-approval threshold of $100.00", "decision": "allowed"}
{"timestamp": "2024-01-15T10:30:01", "policy_version": "v1", "action_type": "spend_money", "risk": "high", "cost": 250.0, "explanation": "Cost $250.00 exceeds approval threshold of $200.00", "decision": "paused"}
{"timestamp": "2024-01-15T10:30:15", "policy_version": "v1", "action_type": "spend_money", "risk": "high", "cost": 250.0, "explanation": "Cost $250.00 exceeds approval threshold of $200.00", "decision": "approved", "approved_by": "alice@example.com"}
```

## System Status

**Status**: Vfinished (conceptually complete)

Aegis version 1.0.0 is a finished system artifact. The core functionality is complete and stable. No further development is planned without explicit scope decisions and version bumps.

## Problem

AI agents can make tool calls with real-world side effects (e.g., spending money, sending emails, calling APIs). Aegis evaluates actions for risk, automatically approves safe actions, and pauses execution for human approval when risky actions are detected.

## How it works

- Wraps a LangChain agent and intercepts tool calls
- Evaluates actions using configurable risk rules
- Actions are assigned risk levels: "low", "medium", or "high"
- Low and medium risk actions are auto-approved
- High risk actions pause execution and start a web server
- Human visits a URL to review the action with an explanation
- Human approves or denies the action
- Execution resumes or stops based on the decision
- All decisions are logged to a local JSONL file with explanations

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

When a high-risk action is detected, execution pauses and a URL is printed to the console. Visit the URL to review the action explanation and approve or deny.

## What Aegis Intercepts (and What It Does Not)

Aegis has clear boundaries on what it intercepts:

**✔ Intercepted:**
- Tool calls / actions (e.g., `spend_money`, `send_email`, `call_api`)
- Side-effecting operations (anything with real-world consequences)
- External API calls
- Financial transactions

**❌ NOT Intercepted:**
- Prompts sent to LLMs
- Model outputs / text generation
- Internal reasoning steps
- Non-side-effecting function calls
- Agent planning or decision-making logic

Aegis only intercepts actions that have real-world side effects. It does not inspect or modify agent reasoning, prompts, or model outputs.

## Integration Examples

### Basic Integration

Wrap any agent in one line:

```python
from aegis.wrapper import AegisWrapper

# Your existing agent
agent = YourAgent()

# Wrap with Aegis
wrapped = AegisWrapper(agent, cost_limit=100.0)

# Use as normal
result = wrapped.run("your input")
```

### LangChain Integration

Use the convenience constructor for LangChain agents:

```python
from aegis.wrapper import AegisWrapper
from langchain.agents import initialize_agent

# Create your LangChain agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")

# Wrap with Aegis (one line)
wrapped = AegisWrapper.from_langchain(agent, cost_limit=50.0)

# Agent runs with Aegis protection
result = wrapped.run("your query")
```

### Dev vs Prod Mode

Switch between development and production modes:

```python
# Development mode (default) - verbose console output
wrapped = AegisWrapper(agent, cost_limit=100.0, mode="dev")

# Production mode - explicit blocking messages
wrapped = AegisWrapper(agent, cost_limit=100.0, mode="prod")
```

Mode affects console messaging only. Risk evaluation and approval flow are identical in both modes.

## Action Types

Aegis supports multiple action types across three categories:

**Financial actions:**
- **spend_money**: Cost-based risk evaluation
  - Cost ≤ cost_limit → low risk (auto-approved)
  - cost_limit < Cost ≤ cost_limit × 2 → medium risk (auto-approved)
  - Cost > cost_limit × 2 → high risk (requires approval)

**Data-destructive actions:**
- **delete_data**: Always high risk (requires approval)

**Production-impacting actions:**
- **send_bulk_email**: Always high risk (requires approval)
- **deploy_code**: Always high risk (requires approval)

**Other actions:**
- **send_email**: Fixed medium risk (auto-approved)
- **call_api**: Fixed medium risk (auto-approved)
- **Custom actions**: Can be added via rules configuration

## Rules System

Risk evaluation is handled by `aegis.rules.evaluate_risk()`, which:
- Returns a risk level ("low", "medium", "high")
- Returns a deterministic explanation for the decision
- Uses `DEFAULT_RULES` dictionary for configuration
- Supports cost-based rules (for spend_money) and fixed risk rules (for other actions)

Users can customize rules by modifying `DEFAULT_RULES` in `aegis/rules.py`.

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
   - Trigger an auto-approved action (low/medium risk)
   - Trigger an approval-required action (high risk)
   - Print a URL to visit for approval
   - Display action explanations in the approval UI
   - Write logs with explanations to `logs.jsonl`

The FastAPI server runs on `http://127.0.0.1:8000` automatically when needed.

## What Aegis Explicitly Does NOT Do

Aegis has firm boundaries on what it does not provide:

- **No LLM-based risk scoring**: All risk evaluations are deterministic and rule-based. No AI models are used to assess risk.

- **No autonomous overrides**: High-risk actions cannot bypass human approval. There is no mechanism for the system to override its own rules.

- **No auth system**: The approval interface has no authentication. Anyone with the approval URL can approve or deny actions. This is intentional for simplicity.

- **No persistence guarantees**: Approvals are stored in-memory only. Server restarts lose pending approvals. Logs are append-only files with no backup or replication.

- **No workflow orchestration**: Aegis does not manage agent workflows, retries, or error handling. It only intercepts and approves individual actions.

These boundaries are by design to keep Aegis focused on its core purpose: human-in-the-loop control for risky actions.

## Who Should Use Aegis

Aegis is designed for:

- **Agentic AI teams**: Teams building AI agents that make real-world decisions and need human oversight
- **AI startups**: Early-stage companies prototyping agent systems that need safety controls without infrastructure overhead
- **Research labs**: Academic or research teams experimenting with agent behavior who need audit trails and control mechanisms
- **Hackathon builders**: Developers building agent demos quickly who need human-in-the-loop functionality without complex setup

If you need deterministic risk evaluation, complete audit trails, and simple human approval workflows, Aegis fits your needs.

## Who Should NOT Use Aegis

Aegis is explicitly NOT for:

- **People looking for autonomous agents**: Aegis requires human approval for high-risk actions. If you want fully autonomous agents, Aegis will block your use case.
- **People wanting AI risk scoring**: Aegis uses rule-based risk evaluation, not LLM-based assessment. If you need AI to evaluate risk, Aegis does not provide this.
- **People expecting dashboards**: Aegis provides logs and a simple audit viewer. If you need analytics dashboards, metrics, or visualizations, Aegis does not include these.

If you need authentication, persistence, production deployment features, or complex workflows, Aegis is not the right tool. Use a different system designed for those requirements.


## When Aegis Matters

Here are concrete scenarios where Aegis prevents problems:

### Runaway API Spend

**Without Aegis:**
- Agent makes repeated API calls in a loop
- Each call costs $0.10
- Loop runs 10,000 times
- Result: $1,000 charged unexpectedly
- Discovery: Only after billing statement arrives

**With Aegis:**
- First few calls auto-approved (below threshold)
- When cumulative cost exceeds threshold, execution pauses
- Human reviews the action and sees the loop pattern
- Human denies the action
- Result: Loop stopped before significant cost
- Evidence: Log shows denial with human identity and explanation

### Accidental Data Deletion

**Without Aegis:**
- Agent receives instruction to "clean up old files"
- Agent interprets this as "delete all files older than 1 day"
- Agent executes deletion tool on production database
- Result: Critical data permanently lost
- Discovery: When users report missing data

**With Aegis:**
- Deletion action is flagged as high-risk (if configured)
- Execution pauses before deletion
- Human reviews the action and sees "delete all files older than 1 day"
- Human denies the action
- Result: Data preserved
- Evidence: Log shows denial with explanation of why it was risky

### Risky Production Change

**Without Aegis:**
- Agent is asked to "update the production API endpoint"
- Agent calls deployment tool to change production configuration
- Agent uses wrong endpoint URL
- Result: Production system breaks
- Discovery: When production goes down

**With Aegis:**
- Production deployment action is flagged as high-risk
- Execution pauses before deployment
- Human reviews the action and sees the endpoint URL
- Human notices the URL is incorrect
- Human denies the action
- Result: Production remains stable
- Evidence: Log shows denial with human identity and policy version

## Replaying an Incident

When something goes wrong (or right), you can replay exactly what happened:

1. **Open the log file:**
   ```bash
   cat logs.jsonl
   ```
   Or use the audit viewer:
   ```bash
   python audit_viewer.py
   # Then open http://127.0.0.1:8001/audit
   ```

2. **Find the incident:**
   - Search for the timestamp when the incident occurred
   - Look for the action type involved (e.g., `spend_money`, `send_email`)
   - Find entries with `decision: "paused"` (these required approval)

3. **See why it was paused:**
   - Check the `explanation` field
   - Example: "Cost $250.00 exceeds approval threshold of $200.00"
   - This shows the exact rule that triggered the pause

4. **See who made the decision:**
   - Look for entries with `decision: "approved"` or `decision: "denied"`
   - Check the `approved_by` field
   - Example: `"approved_by": "alice@example.com"`
   - This shows which human reviewed and decided

5. **Verify the policy version:**
   - Check the `policy_version` field
   - Example: `"policy_version": "v1"`
   - This confirms which rules were active at the time
   - If rules change, you can see which version applied to each decision

6. **Trace the full sequence:**
   - Find the `"paused"` entry (when approval was requested)
   - Find the corresponding `"approved"` or `"denied"` entry (human decision)
   - Compare timestamps to see how long approval took
   - Review the explanation to understand the reasoning

## What Evidence Exists After a Decision?

Every decision leaves a complete audit trail in `logs.jsonl`:

- **Explanations**: Every log entry includes an `explanation` field that shows why the action was auto-approved or required approval. This is deterministic and reproducible.

- **Human identity**: For approved/denied decisions, the `approved_by` field records who made the decision. This is required before approving or denying, so every human decision is attributed.

- **Policy version**: Every log entry includes `policy_version` (e.g., "v1"). This ties each decision to the specific rules that were active at that time. If you change rules, you can see which version applied to each historical decision.

- **Append-only format**: Logs are written in JSONL format (one JSON object per line). Logs are append-only - entries are never modified or deleted. This ensures the audit trail cannot be tampered with.

**How do we prove a human was involved?**

1. Find the log entry with `decision: "paused"` - this shows the action was intercepted
2. Find the corresponding entry with `decision: "approved"` or `"denied"` - this shows a human decision was made
3. Check `approved_by` field - this shows which human made the decision
4. Verify `policy_version` matches the rules you expect
5. The explanation field shows why the action required approval

All of this is in plain JSON that can be read, searched, and analyzed with standard tools.
