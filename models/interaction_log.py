"""Interaction logging model.

One record per agent turn for auditability: who asked, what tools ran, and which requests were
denied for scope, with a digest of the prompt rather than raw PHI in the clear.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InteractionLog:
    subject: str
    role: str
    prompt_digest: str  # hash or truncation of the prompt, never raw PHI
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

    # Emit to CloudWatch Logs or a FHIR AuditEvent. Scrub PHI before write.
