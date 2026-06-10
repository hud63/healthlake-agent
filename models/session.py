"""Session and identity models.

SessionContext carries the verified caller identity into every tool call. Authorization decisions
read from this object, never from anything in the model prompt. The context var lets the AgentCore
entrypoint bind the caller for a turn so the framework-managed tools can read it.
"""
from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum


class UserRole(str, Enum):
    PATIENT = "patient"
    NURSE = "nurse"
    DOCTOR = "doctor"
    ADMIN = "admin"


@dataclass(frozen=True)
class SessionContext:
    subject: str  # stable identity id, for example a Cognito sub
    role: UserRole = UserRole.PATIENT
    # Patient ids this caller is entitled to, for example a guardian's dependents. Empty means none.
    entitled_patient_ids: tuple[str, ...] = field(default_factory=tuple)

    def may_access_patient(self, patient_id: str) -> bool:
        """Coarse in-app scope check. The data layer (IAM, FHIR _security) is the real boundary.

        Clinical roles still need a care-team relationship check; wire that to your entitlement
        service rather than granting blanket access.
        """
        if self.role in (UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN):
            return True
        return patient_id in self.entitled_patient_ids


_current_session: ContextVar[SessionContext | None] = ContextVar("current_session", default=None)


def set_current_session(ctx: SessionContext) -> None:
    """Bind the caller's session for the current turn."""
    _current_session.set(ctx)


def get_current_session() -> SessionContext:
    """Return the bound session, or raise if no caller has been established."""
    ctx = _current_session.get()
    if ctx is None:
        raise PermissionError("No authenticated session is bound for this request")
    return ctx
