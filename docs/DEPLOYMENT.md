# Deployment

## Prerequisites
- An AWS account with Bedrock and HealthLake enabled in your region.
- An approved Bedrock model (set `MODEL_ID`).
- Docker with ARM64 build support, the AWS CLI, and credentials carrying the policies in `iam/`.
- An identity provider (Cognito user pool or OIDC) issuing the claims the agent expects.

## Steps
1. **Configure.** `cp .env.template .env` and fill in datastore id, bucket, model id, and pool id.
2. **Datastore.** Create the HealthLake datastore and wait for `ACTIVE` (five to ten minutes). Load synthetic data, for example Synthea. Never load real PHI for testing.
3. **IAM.** Create roles and policies from `iam/healthlake_permissions.json` and `iam/ecr_permissions.json`, replacing the REGION, ACCOUNT_ID, DATASTORE_ID, and REPO_NAME placeholders.
4. **Image.** Build the ARM64 image and push it to ECR.
5. **Deploy.** Deploy the AgentCore runtime from the image.
6. **Verify.** Invoke with a request whose identity is entitled to one patient, then with an unentitled request, and confirm the second is denied.

PowerShell: `scripts/deploy_agentcore.ps1`. Cross-platform: `python scripts/deploy_with_verification.py`.

## Teardown
Delete the AgentCore runtime, the ECR images, and the HealthLake datastore to stop charges.
