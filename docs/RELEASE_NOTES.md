# Release Notes

## Version 1.0.0

### What Aegis Guarantees

Aegis provides the following guarantees:

1. **Deterministic risk evaluation**: All risk assessments are rule-based and deterministic. Given the same action and rules, the risk level and explanation will be identical.

2. **Human approval requirement**: High-risk actions (risk level "high") cannot proceed without explicit human approval via the web interface. There is no mechanism to bypass this requirement.

3. **Complete audit trail**: All intercepted actions are logged to `logs.jsonl` with:
   - Timestamp
   - Policy version
   - Action type
   - Risk level
   - Explanation
   - Decision (allowed, paused, approved, denied)
   - Human identity (for approved/denied decisions)

4. **Blocking execution**: When a high-risk action requires approval, agent execution blocks until a human makes a decision. Execution does not proceed until approval or denial is received.

5. **No autonomous overrides**: The system cannot override its own rules or bypass human approval requirements.

### What Problems Aegis Solves

Aegis addresses the following problems:

1. **Uncontrolled agent actions**: Prevents AI agents from executing risky actions without human oversight.

2. **Lack of audit trail**: Provides complete logging of all intercepted actions with explanations and human decisions.

3. **Inconsistent risk evaluation**: Offers a centralized, configurable rules system for evaluating action risk.

4. **No human-in-the-loop mechanism**: Provides a simple web-based interface for humans to review and approve/deny risky actions.

5. **Opaque decision-making**: Generates deterministic explanations for all risk evaluations, making decisions transparent and auditable.

### What is Intentionally Out of Scope

The following are explicitly not included in Aegis:

1. **Authentication and authorization**: No user authentication, role-based access control, or permission systems.

2. **Persistence**: Approvals are stored in-memory only. Server restarts lose pending approvals. Logs are local files with no backup or replication.

3. **LLM-based risk scoring**: Risk evaluation is rule-based only. No AI models are used to assess risk.

4. **Workflow orchestration**: Aegis does not manage agent workflows, retries, error handling, or task scheduling.

5. **Configuration file loaders**: Rules are defined as Python dictionaries. No YAML, JSON, or other configuration file formats are supported.

6. **Production deployment features**: No HTTPS, security headers, rate limiting, or deployment tooling.

7. **Full LangChain integration**: The wrapper demonstrates the control flow but does not fully integrate with LangChain's tool execution pipeline.

8. **Multiple approval workflows**: All action types use the same approval interface and flow.

9. **Rule validation or testing**: No built-in validation or testing framework for rules.

10. **Per-user or per-environment rules**: Rules are global. No support for user-specific or environment-specific rule sets.

### What Would Constitute a Breaking Change

The following changes would be considered breaking:

1. **API changes**: Modifying function signatures, return types, or class interfaces in `aegis.wrapper`, `aegis.rules`, `aegis.approvals`, or `aegis.logging`.

2. **Log format changes**: Changing the structure or required fields in log entries would break log parsing and analysis.

3. **Risk level semantics**: Changing the meaning of "low", "medium", or "high" risk levels or the approval requirements for each level.

4. **Action format changes**: Modifying the normalized action format (type, risk, explanation, metadata) would break compatibility.

5. **Rule system changes**: Changing how rules are defined, evaluated, or the rule types supported would break existing rule configurations.

6. **Approval flow changes**: Modifying how approvals are requested, stored, or processed would break the human-in-the-loop mechanism.

7. **Policy version changes**: Changing the policy version constant without corresponding documentation and migration guidance.

