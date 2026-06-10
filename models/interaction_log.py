"""Interaction logging model.

One record per agent turn. The point is auditability: who asked, what tools ran, what scope check
result, and a digest of what was returned — WITHOUT logging PHI in the clear.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InteractionLog:
    subject: str
    role: str
    prompt_digest: str  # hash/truncation of the prompt — never raw PHI
    tools_invoked: list[str] = field(default_factory=list)
    scope_denied: list[str] = field(default_factory=list)
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "role": self.role,
            "prompt_digest": self.prompt_digest,
            "tools_invoked": self.tools_invoked,
            "scope_denied": self.scope_denied,
            "ts": self.ts,
        }

    # TODO: emit to CloudWatch Logs / a FHIR AuditEvent. Scrub PHI before write.
