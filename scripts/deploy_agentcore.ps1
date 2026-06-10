# Deploy the HealthLake agent to Bedrock AgentCore (skeleton).
# Mirrors deploy_with_verification.py for a Windows/PowerShell workflow.
# Nothing here runs real deploys yet — each step is a TODO.

[CmdletBinding()]
param(
    [string]$Region = $env:AWS_REGION
)

Write-Host "[skeleton] HealthLake agent deploy — implement the TODOs before using." -ForegroundColor Yellow

# TODO 1: Ensure HealthLake datastore exists and is ACTIVE (aws healthlake describe-fhir-datastore).
# TODO 2: Build ARM64 image and push to ECR.
# TODO 3: Configure + deploy AgentCore runtime from the image.
# TODO 4: Invoke a scoped test payload and confirm a non-error response.

Write-Host "Region: $Region"
Write-Host "Planned: datastore -> image -> agentcore deploy -> verify"
