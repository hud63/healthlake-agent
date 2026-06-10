# Architecture

## Components

- **AgentCore Runtime** — serverless ARM64 container running the agent; provides session memory.
- **agent.py** — the agent + 7 tools. The LLM reasons over the conversation; tools do the data access.
- **AWS HealthLake** — FHIR R4 datastore. Accessed via SigV4-signed REST.
- **Amazon S3** — clinical documents; read directly or via presigned URLs.
- **Identity (Cognito / OIDC)** — the verified caller identity, propagated into every tool call.
- **CloudWatch** — logs/metrics; interaction logs carry digests, never raw PHI.

## Request flow

1. Authenticated request hits the AgentCore handler (`agent_agentcore.py`).
2. The handler builds a `SessionContext` from verified claims (subject, role, entitled patients).
3. The agent reasons and selects tools.
4. Each tool calls `assert_in_scope(ctx, ...)` before any AWS call.
5. Data-layer scoping (IAM policy + FHIR `_security` / patient filters) enforces the same boundary
   independently.
6. Coded FHIR values are translated to readable text before reaching the user.

## Why identity-at-the-data-layer

The sharp risk in a clinical agent is a **scope error** — returning a record that belongs to someone
else — not a reasoning error. A scheduling mistake is recoverable; a wrong-record disclosure is a
breach. So entitlement is enforced where data is fetched, by an identity the prompt cannot alter,
with the in-app `assert_in_scope` check as defense in depth.

## Deliberately no CloudFormation/CDK

Provisioning is CLI scripts so the multi-minute HealthLake datastore creation is observable and
re-runnable step by step. IAM lives as reviewable JSON templates in `iam/`.

## Diagram

`docs/generated-diagrams/` — TODO: add an architecture PNG.
