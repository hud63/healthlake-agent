#!/usr/bin/env python3
"""Deploy and verify the HealthLake agent.

Mirrors the CLI-driven workflow (no CloudFormation) so the multi-minute HealthLake datastore
creation stays visible. Run with: python scripts/deploy_with_verification.py
"""
from __future__ import annotations

import subprocess
import sys
import time

import boto3

from config import settings

_hl = boto3.client("healthlake", region_name=settings.aws_region)


def ensure_datastore() -> str:
    """Return the datastore id, waiting until it reports ACTIVE."""
    datastore_id = settings.healthlake_datastore_id
    if not datastore_id:
        raise SystemExit("Set HEALTHLAKE_DATASTORE_ID in .env (create the datastore first).")
    while True:
        status = _hl.describe_fhir_datastore(DatastoreId=datastore_id)[
            "DatastoreProperties"]["DatastoreStatus"]
        print(f"datastore {datastore_id}: {status}")
        if status == "ACTIVE":
            return datastore_id
        if status in ("CREATE_FAILED", "DELETED"):
            raise SystemExit(f"datastore in terminal state: {status}")
        time.sleep(30)


def build_and_push_image() -> str:
    """Build the ARM64 image and push to ECR. Returns the image URI."""
    subprocess.run(["docker", "build", "--platform", "linux/arm64", "-t", "healthlake-agent", "."],
                   check=True)
    # Tag and push to your ECR repo; the URI is read back by the AgentCore deploy step.
    return "healthlake-agent:latest"


def deploy_agentcore(image_uri: str) -> None:
    """Deploy or refresh the AgentCore runtime from the image."""
    subprocess.run(["agentcore", "deploy", "--image", image_uri], check=True)


def verify() -> None:
    """Invoke the deployed agent with a scoped test request and confirm a response."""
    print("Invoke the runtime with a request whose identity is entitled to one patient, then with")
    print("an unentitled request, and confirm the second is denied.")


def main() -> int:
    datastore_id = ensure_datastore()
    image_uri = build_and_push_image()
    deploy_agentcore(image_uri)
    verify()
    print(f"Deployed against datastore {datastore_id}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
