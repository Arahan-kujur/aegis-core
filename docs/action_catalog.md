# Action Catalog

This document describes all action types supported by Aegis, their risk characteristics, and approval requirements.

## spend_money

**Description**: Actions that involve spending money or incurring costs (e.g., API calls with usage fees, purchases, subscriptions).

**Why it is risky**: Financial transactions have direct monetary impact. Uncontrolled spending can lead to budget overruns, unexpected charges, or financial loss.

**Default risk level**: Variable (cost-based)
- Low risk: Cost ≤ cost_limit (auto-approved)
- Medium risk: cost_limit < Cost ≤ cost_limit × 2 (auto-approved)
- High risk: Cost > cost_limit × 2 (requires human approval)

**Requires human approval**: Yes, when cost exceeds cost_limit × 2

**Rationale**: Cost-based risk evaluation allows safe, low-cost operations to proceed automatically while requiring human oversight for expensive actions. The threshold system provides a graduated response: very low costs are always safe, moderate costs are logged but auto-approved, and high costs require explicit human consent.

## send_email

**Description**: Actions that send email messages to recipients.

**Why it is risky**: Email actions can have privacy, security, and reputation consequences. Sending emails to wrong recipients, containing sensitive information, or in bulk can cause data breaches, spam complaints, or damage to sender reputation.

**Default risk level**: Medium (fixed)

**Requires human approval**: No (auto-approved)

**Rationale**: Email sending is a common, generally safe operation when properly configured. Medium risk classification ensures it is logged and monitored, but does not require approval for every message. Organizations can modify this rule if they require approval for all emails.

## call_api

**Description**: Actions that make external API calls to third-party services.

**Why it is risky**: API calls can expose sensitive data, incur costs, trigger side effects in external systems, or create dependencies on external services. Malformed requests or excessive calls can cause service disruptions or security issues.

**Default risk level**: Medium (fixed)

**Requires human approval**: No (auto-approved)

**Rationale**: API calls are a fundamental operation for many agents. While they carry some risk (data exposure, costs, side effects), they are typically safe when properly scoped. Medium risk ensures logging and monitoring without blocking every API call. Organizations can customize this rule to require approval for specific API endpoints or patterns.

## delete_data

**Description**: Actions that delete data from databases, file systems, or storage systems.

**Why it is risky**: Data deletion is irreversible. Once data is deleted, it cannot be recovered unless backups exist. Accidental deletion can cause permanent data loss, compliance violations, or business disruption.

**Default risk level**: High (fixed)

**Requires human approval**: Yes (always)

**Rationale**: Data deletion has permanent consequences. Even with backups, recovery is time-consuming and may cause service disruption. Requiring human approval for all deletion actions ensures that data loss is intentional and authorized.

## send_bulk_email

**Description**: Actions that send email messages to multiple recipients (typically 10+ recipients or bulk mailing operations).

**Why it is risky**: Bulk email operations can trigger spam filters, damage sender reputation, violate anti-spam laws, or expose sensitive information to wrong recipients. Once sent, emails cannot be recalled.

**Default risk level**: High (fixed)

**Requires human approval**: Yes (always)

**Rationale**: Bulk email has reputation and legal consequences. A single mistake can blacklist your domain or violate regulations. Requiring human approval ensures bulk operations are reviewed for recipient lists, content, and compliance before sending.

## deploy_code

**Description**: Actions that deploy code or configuration changes to production systems.

**Why it is risky**: Production deployments can cause system failures, service outages, or security vulnerabilities. A bad deployment can affect all users immediately and may require rollback procedures.

**Default risk level**: High (fixed)

**Requires human approval**: Yes (always)

**Rationale**: Production changes have immediate impact on all users. Even with testing, production environments can behave differently. Requiring human approval ensures deployments are reviewed for correctness, timing, and rollback plans before execution.

