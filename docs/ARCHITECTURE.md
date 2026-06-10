# Architecture

## Components

- **AgentCore Runtime** runs the agent in a containerized ARM64 environment and provides session memory.
- **agent.py** holds the agent and its seven tools. The model reasons over the conversation; the tools do the data access.
- **AWS HealthLake** is the FHIR R4 datastore, reached over SigV4-signed REST.
- **Amazon S3** holds clinical documents, read directly or through presigned URLs.
- **Identity (Cognito or OIDC)** supplies the verified caller identity, propagated into every tool call.
- **CloudWatch** carries logs and metrics; interaction logs hold digests, never raw PHI.

## Request flow

1. An authenticated request reaches the AgentCore handler in `agent_agentcore.py`.
2. The handler builds a `SessionContext` from verified claims (subject, role, entitled patients) and binds it for the turn.
3. The agent reasons and selects tools.
4. Each tool reads the bound session and calls `assert_in_scope` before any AWS call.
5. Data-layer scoping (IAM policy plus FHIR `_security` and patient filters) enforces the same boundary independently.
6. Coded FHIR values are translated to readable text before they reach the user.

## Why identity rides into every call

The sharp risk in a clinical agent is a scope error, returning a record that belongs to someone
else, not a reasoning error. A scheduling mistake is recoverable; a wrong-record disclosure is a
breach. So entitlement is enforced where data is fetched, by an identity the prompt cannot alter,
with the in-app `assert_in_scope` check as defense in depth.

## Why no CloudFormation

Provisioning is CLI plus boto3 so the multi-minute HealthLake datastore creation is observable and
re-runnable step by step. IAM lives as reviewable JSON in `iam/`.

## Diagram

`docs/generated-diagrams/` holds the architecture image.
