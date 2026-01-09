# Aegis

Aegis is a human-in-the-loop control layer that wraps existing LangChain-style agents and intercepts risky actions before execution.

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

## Action Types

Aegis supports multiple action types:

- **spend_money**: Cost-based risk evaluation
  - Cost ≤ cost_limit → low risk (auto-approved)
  - cost_limit < Cost ≤ cost_limit × 2 → medium risk (auto-approved)
  - Cost > cost_limit × 2 → high risk (requires approval)

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

## Who This Is For

Aegis is suitable for:

- **Developers building AI agents** who need human oversight for risky actions
- **Organizations** requiring audit trails and approval workflows for agent operations
- **Teams** that need deterministic, rule-based risk evaluation without LLM dependencies
- **Projects** where simplicity and transparency are prioritized over feature richness

## Who This Is NOT For

Aegis is not suitable for:

- **Production deployments** requiring authentication, persistence, or high availability
- **Organizations** needing complex approval workflows, role-based access, or multi-user systems
- **Projects** requiring LLM-based risk assessment or adaptive risk evaluation
- **Teams** needing workflow orchestration, retry logic, or error handling
- **Use cases** requiring configuration file support or external rule management

## Creating a Release

To create a release of Aegis:

1. **Tag the release**: Create a git tag for the version (e.g., `v1.0.0`)
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Freeze main branch**: After tagging, no further commits should be made to main without:
   - Bumping the version number in `aegis/__init__.py`
   - Updating `docs/RELEASE_NOTES.md` with the new version
   - Making an explicit scope decision about what changes are included

3. **Scope decisions**: Any changes to Aegis require explicit decisions about:
   - Whether the change is within scope or requires a new version
   - Whether the change is a breaking change (requires major version bump)
   - Whether the change maintains backward compatibility

The version number in `aegis/__init__.py` is the single source of truth for the project version.
