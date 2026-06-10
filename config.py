"""Central configuration for the HealthLake agent skeleton.

Loads settings from environment (see .env.template). No secrets are hardcoded.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv is optional at runtime
    pass


@dataclass(frozen=True)
class Settings:
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")

    # Model id is a placeholder — set MODEL_ID to your approved Claude model.
    model_id: str = os.getenv("MODEL_ID", "REPLACE_WITH_YOUR_CLAUDE_MODEL_ID")

    healthlake_datastore_id: str = os.getenv("HEALTHLAKE_DATASTORE_ID", "")
    healthlake_endpoint: str = os.getenv("HEALTHLAKE_ENDPOINT", "")

    docs_s3_bucket: str = os.getenv("DOCS_S3_BUCKET", "")
    docs_s3_prefix: str = os.getenv("DOCS_S3_PREFIX", "clinical/")

    identity_provider: str = os.getenv("IDENTITY_PROVIDER", "cognito")
    cognito_user_pool_id: str = os.getenv("COGNITO_USER_POOL_ID", "")

    max_document_bytes: int = int(os.getenv("MAX_DOCUMENT_BYTES", str(50 * 1024 * 1024)))
    presigned_url_ttl_seconds: int = int(os.getenv("PRESIGNED_URL_TTL_SECONDS", "3600"))

    def healthlake_base_url(self) -> str:
        """Derive the FHIR endpoint if not explicitly set. TODO: verify path for your region."""
        if self.healthlake_endpoint:
            return self.healthlake_endpoint
        if not self.healthlake_datastore_id:
            raise ValueError("HEALTHLAKE_DATASTORE_ID is required")
        return (
            f"https://healthlake.{self.aws_region}.amazonaws.com/datastore/"
            f"{self.healthlake_datastore_id}/r4/"
        )


settings = Settings()
