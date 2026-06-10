"""Authorization helpers.

assert_in_scope is the in-application guard every tool calls before touching data. It is the second
line of defense; the first is IAM plus FHIR _security scoping at the data layer. Defense in depth
means even if a prompt tries to coax the agent out of scope, this raises before any AWS call.
"""
from __future__ import annotations

from models.session import SessionContext, UserRole


class ScopeError(PermissionError):
    """Raised when a caller requests a resource outside their entitlement."""


# Resource types only clinical and admin roles may read at all.
_CLINICAL_ONLY = {"DatastoreInfo"}


def assert_in_scope(ctx: SessionContext, resource_type: str, resource_id: str | None) -> None:
    """Raise ScopeError if ctx is not entitled to (resource_type, resource_id)."""
    if resource_type == "Patient" and resource_id is not None:
        if not ctx.may_access_patient(resource_id):
            raise ScopeError(f"{ctx.subject} is not entitled to Patient/{resource_id}")
        return

    if resource_type in _CLINICAL_ONLY and ctx.role == UserRole.PATIENT:
        raise ScopeError(f"role {ctx.role} may not read {resource_type}")

    # Patient-linked searches and documents are filtered to the caller's entitled patients at the
    # data layer (see search_fhir_resources). A patient with no entitlements gets nothing.
    if ctx.role == UserRole.PATIENT and not ctx.entitled_patient_ids:
        raise ScopeError(f"{ctx.subject} has no entitled patients")
