# Contributing to Aegis

Thank you for your interest in contributing to Aegis. This document explains how to contribute effectively.

## How to Open Issues

### Bug Reports

If you find a bug, please open an issue using the bug report template. Include:
- Expected behavior
- Actual behavior
- Steps to reproduce
- Relevant log entries (if applicable)

### Feature Requests

Aegis has a focused scope. Feature requests should be for:
- New action types that require human approval
- Improvements to existing approval flows
- Documentation improvements

Use the feature request template and explain:
- What action is missing
- Why it is risky
- Why human approval is needed

## How to Suggest Actions

To suggest a new action type:

1. Open a feature request issue
2. Explain what the action does
3. Explain why it is risky (financial, data-destructive, production-impacting)
4. Explain why it requires human approval
5. Suggest a default risk level (low, medium, or high)

The maintainers will evaluate whether the action fits Aegis's scope and add it to the rules if appropriate.

## What Will NOT Be Accepted

Aegis has firm boundaries. The following will NOT be accepted:

- **Authentication or authorization systems**: Aegis intentionally has no auth
- **Database persistence**: Approvals are in-memory only
- **LLM-based risk scoring**: Risk evaluation is rule-based only
- **Configuration file loaders**: Rules are Python dictionaries
- **Workflow orchestration**: Aegis only intercepts individual actions
- **Dashboards or analytics**: Aegis provides logs, not dashboards
- **Async rewrites**: Aegis uses synchronous blocking
- **Production deployment features**: No HTTPS, rate limiting, etc.

These boundaries are by design. If you need these features, Aegis may not be the right tool for your use case.

## Development Setup

1. Clone the repository
2. Install in development mode:
   ```bash
   pip install -e .
   ```
3. Run the demo:
   ```bash
   python demo.py
   ```

## Code Style

- Follow existing code style
- Keep functions focused and simple
- Add docstrings for public functions
- No unnecessary abstractions

## Pull Requests

Before submitting a pull request:

1. Ensure your changes fit Aegis's scope
2. Test that the demo still runs
3. Verify no core control logic is changed
4. Update documentation if needed

Pull requests that expand scope beyond Aegis's boundaries will be rejected.

