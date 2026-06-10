"""Authorization helpers.

assert_in_scope is the in-application guard every tool calls before touching data. It is the SECOND
line of defense — the first is IAM + FHIR _security scoping at the data layer. Defense in depth:
even if a prompt tries to coax the agent out of scope, this raises before any AWS call.
"""
from __future__ import annotations

from models.session import SessionContext


class ScopeError(PermissionError):
    """Raised when a caller requests a resource outside their entitlement."""


def assert_in_scope(ctx: SessionContext, resource_type: str, resource_id: str | None) -> None:
    """Raise ScopeError if ctx is not entitled to (resource_type, resource_id).

    TODO: expand per resource type. The Patient/$everything and patient-linked resources are the
    sharp edge — resolve the patient the resource belongs to and check ctx.may_access_patient().
    """
    if resource_type == "Patient" and resource_id is not None:
        if not ctx.may_access_patient(resource_id):
            raise ScopeError(f"{ctx.subject} not entitled to Patient/{resource_id}")
    # Non-patient resource types (DatastoreInfo, Document, search) get role-based checks here.
    # TODO: implement per-type rules; default-deny for unknown types.
