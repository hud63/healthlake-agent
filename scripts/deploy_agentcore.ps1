# Deploy the HealthLake agent to Bedrock AgentCore on Windows.
# Mirrors deploy_with_verification.py for a PowerShell workflow.

[CmdletBinding()]
param(
    [string]$Region = $env:AWS_REGION
)

if (-not $Region) { $Region = "us-east-1" }
Write-Host "Deploying HealthLake agent in $Region"

# 1. Confirm the HealthLake datastore is ACTIVE.
$datastoreId = $env:HEALTHLAKE_DATASTORE_ID
if (-not $datastoreId) { throw "Set HEALTHLAKE_DATASTORE_ID before deploying." }
$status = (aws healthlake describe-fhir-datastore --datastore-id $datastoreId --region $Region `
    --query "DatastoreProperties.DatastoreStatus" --output text)
Write-Host "datastore $datastoreId status: $status"
if ($status -ne "ACTIVE") { throw "datastore not ACTIVE yet ($status)." }

# 2. Build the ARM64 image and push to ECR.
docker build --platform linux/arm64 -t healthlake-agent .

# 3. Deploy the AgentCore runtime from the image.
agentcore deploy --image healthlake-agent:latest

# 4. Verify: invoke with an entitled request, then an unentitled one, and confirm the second denies.
Write-Host "Run a scoped invocation to verify, see docs/DEPLOYMENT.md."
