# Deployment

> Skeleton. Implement the `TODO`s in `scripts/` and `agent.py` first.

## Prerequisites
- AWS account with Bedrock + HealthLake enabled in your region.
- An approved Bedrock model (set `MODEL_ID`).
- Docker (ARM64 build support), AWS CLI, and credentials with the policies in `iam/`.
- An identity provider (Cognito user pool or OIDC) issuing the claims the agent expects.

## Steps
1. **Configure**: `cp .env.template .env`; fill in datastore id, bucket, model id, pool id.
2. **Datastore**: create the HealthLake datastore; wait for `ACTIVE` (5–10 min). Optionally load
   **synthetic** sample data (never real PHI for demos).
3. **IAM**: create roles/policies from `iam/healthlake_permissions.json` and `iam/ecr_permissions.json`
   (replace REGION / ACCOUNT_ID / DATASTORE_ID / REPO_NAME placeholders).
4. **Image**: build the ARM64 image, push to ECR.
5. **Deploy**: deploy the AgentCore runtime from the image.
6. **Verify**: invoke with a scoped test payload; confirm a non-error response and that an
   out-of-scope request is denied.

PowerShell: `scripts/deploy_agentcore.ps1`. Cross-platform: `python scripts/deploy_with_verification.py`.

## Teardown
Delete the AgentCore runtime, ECR images, and the HealthLake datastore to stop charges.
