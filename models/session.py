"""Session + identity models.

SessionContext carries the *verified* caller identity into every tool call. Authorization decisions
read from this object, not from anything in the model prompt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class UserRole(str, Enum):
    PATIENT = "patient"
    NURSE = "nurse"
    DOCTOR = "doctor"
    ADMIN = "admin"


@dataclass(frozen=True)
class SessionContext:
    subject: str  # stable identity id (e.g. Cognito sub)
    role: UserRole = UserRole.PATIENT
    # Patient ids this caller is entitled to (e.g. a guardian's dependents). Empty = none.
    entitled_patient_ids: tuple[str, ...] = field(default_factory=tuple)

    def may_access_patient(self, patient_id: str) -> bool:
        """Coarse, in-app scope check. The data layer (IAM / FHIR _security) is the real boundary.

        TODO: for clinical roles, replace tuple membership with your entitlement service.
        """
        if self.role in (UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN):
            return True  # TODO: still scope to care-team relationships, not blanket access
        return patient_id in self.entitled_patient_ids
