"""HealthLake agent and its seven tools.

Four FHIR tools read clinical data from AWS HealthLake, three S3 tools read documents. Every tool
resolves the caller's SessionContext and checks entitlement with assert_in_scope before it touches
AWS, so the model can never reach a record the caller is not allowed to see.
"""
from __future__ import annotations

import json
from typing import Any

import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from strands import Agent, tool

from config import settings
from models.session import get_current_session
from prompts.healthcare_assistant_prompt import SYSTEM_PROMPT
from utils.auth_helpers import assert_in_scope
from utils.fhir_code_translator import translate
from utils.retry_handler import with_retry

_session = boto3.Session(region_name=settings.aws_region)


def _signed_fhir_get(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    """Issue a SigV4-signed GET against the HealthLake FHIR endpoint and return parsed JSON."""
    url = settings.healthlake_base_url() + path
    request = AWSRequest(method="GET", url=url, params=params or {})
    SigV4Auth(_session.get_credentials(), "healthlake", settings.aws_region).add_auth(request)
    prepared = requests.Request(method="GET", url=url, params=params or {},
                                headers=dict(request.headers)).prepare()
    with requests.Session() as http:
        response = http.send(prepared, timeout=30)
    response.raise_for_status()
    return response.json()


# ----------------------------------------------------------------------------------------
# FHIR tools (AWS HealthLake)
# ----------------------------------------------------------------------------------------
@tool
@with_retry
def get_datastore_info() -> dict[str, Any]:
    """Return HealthLake datastore metadata: status, FHIR version, and endpoint."""
    ctx = get_current_session()
    assert_in_scope(ctx, resource_type="DatastoreInfo", resource_id=None)
    client = _session.client("healthlake")
    info = client.describe_fhir_datastore(DatastoreId=settings.healthlake_datastore_id)
    return info["DatastoreProperties"]


@tool
@with_retry
def search_fhir_resources(resource_type: str, query_params: dict[str, str] | None = None) -> dict[str, Any]:
    """Search a FHIR resource type (Patient, Condition, Observation, ...) with query parameters."""
    ctx = get_current_session()
    assert_in_scope(ctx, resource_type=resource_type, resource_id=None)
    params = dict(query_params or {})
    # Narrow results to the caller's entitled patients so scoping holds at the data layer too.
    if ctx.entitled_patient_ids and resource_type != "Patient":
        params.setdefault("patient", ",".join(ctx.entitled_patient_ids))
    bundle = _signed_fhir_get(resource_type, params)
    return translate(bundle)


@tool
@with_retry
def read_fhir_resource(resource_type: str, resource_id: str) -> dict[str, Any]:
    """Read one FHIR resource by type and id, with coded values translated to readable text."""
    ctx = get_current_session()
    assert_in_scope(ctx, resource_type=resource_type, resource_id=resource_id)
    resource = _signed_fhir_get(f"{resource_type}/{resource_id}")
    return translate(resource)


@tool
@with_retry
def patient_everything(patient_id: str, start: str | None = None, end: str | None = None) -> dict[str, Any]:
    """Run the FHIR $patient-everything operation for a patient, optionally date-bounded."""
    ctx = get_current_session()
    assert_in_scope(ctx, resource_type="Patient", resource_id=patient_id)
    params: dict[str, str] = {}
    if start:
        params["_since"] = start
    if end:
        params["_until"] = end
    bundle = _signed_fhir_get(f"Patient/{patient_id}/$everything", params)
    return translate(bundle)


# ----------------------------------------------------------------------------------------
# S3 document tools
# ----------------------------------------------------------------------------------------
@tool
@with_retry
def list_s3_documents(prefix: str | None = None) -> list[dict[str, Any]]:
    """List clinical documents under the configured bucket and prefix."""
    ctx = get_current_session()
    assert_in_scope(ctx, resource_type="Document", resource_id=None)
    s3 = _session.client("s3")
    result = s3.list_objects_v2(Bucket=settings.docs_s3_bucket, Prefix=prefix or settings.docs_s3_prefix)
    return [{"key": o["Key"], "size": o["Size"], "last_modified": o["LastModified"].isoformat()}
            for o in result.get("Contents", [])]


@tool
@with_retry
def read_s3_document(key: str) -> dict[str, Any]:
    """Read a document's content, bounded by MAX_DOCUMENT_BYTES."""
    ctx = get_current_session()
    assert_in_scope(ctx, resource_type="Document", resource_id=key)
    s3 = _session.client("s3")
    head = s3.head_object(Bucket=settings.docs_s3_bucket, Key=key)
    if head["ContentLength"] > settings.max_document_bytes:
        return {"key": key, "truncated": True, "reason": "exceeds MAX_DOCUMENT_BYTES"}
    body = s3.get_object(Bucket=settings.docs_s3_bucket, Key=key)["Body"].read()
    try:
        return {"key": key, "content": body.decode("utf-8"), "encoding": "utf-8"}
    except UnicodeDecodeError:
        import base64
        return {"key": key, "content": base64.b64encode(body).decode("ascii"), "encoding": "base64"}


@tool
@with_retry
def generate_s3_presigned_url(key: str, ttl_seconds: int | None = None) -> str:
    """Create a time-limited download URL for a document (default TTL from config)."""
    ctx = get_current_session()
    assert_in_scope(ctx, resource_type="Document", resource_id=key)
    ttl = min(ttl_seconds or settings.presigned_url_ttl_seconds, 7 * 24 * 3600)
    s3 = _session.client("s3")
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": settings.docs_s3_bucket, "Key": key}, ExpiresIn=ttl
    )


TOOLS = [
    get_datastore_info,
    search_fhir_resources,
    read_fhir_resource,
    patient_everything,
    list_s3_documents,
    read_s3_document,
    generate_s3_presigned_url,
]


def build_agent() -> Agent:
    """Construct the agent with the configured model, system prompt, and tools."""
    return Agent(model=settings.model_id, system_prompt=SYSTEM_PROMPT, tools=TOOLS)


if __name__ == "__main__":
    print(json.dumps([t.__name__ for t in TOOLS], indent=2))
