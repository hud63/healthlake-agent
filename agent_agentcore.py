"""AgentCore entrypoint.

Exposes the agent as a handler for Bedrock AgentCore Runtime. Its job is to build a SessionContext
from the verified identity on the request and bind it for the duration of the turn, so every tool
call the agent makes is scoped to that caller.
"""
from __future__ import annotations

from typing import Any

from agent import build_agent
from models.session import SessionContext, UserRole, set_current_session

_agent = build_agent()


def _session_from_event(event: dict[str, Any]) -> SessionContext:
    """Build a SessionContext from the verified identity claims on the request.

    Identity comes from the AgentCore identity context or Cognito claims, never from the prompt body.
    """
    claims = event.get("identity", {})
    return SessionContext(
        subject=claims.get("sub", "anonymous"),
        role=UserRole(claims.get("role", "patient")),
        entitled_patient_ids=tuple(claims.get("entitled_patient_ids", [])),
    )


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AgentCore runtime entrypoint."""
    ctx = _session_from_event(event)
    set_current_session(ctx)
    result = _agent(event["prompt"])
    return {"answer": str(result)}
