"""AgentCore entrypoint wrapper (skeleton).

Exposes the agent as a handler for Bedrock AgentCore Runtime. The wrapper's job is to build a
SessionContext from the *authenticated* request (identity from Cognito / the AgentCore identity
context) and pass it into the agent so every downstream tool call is scoped.
"""
from __future__ import annotations

from typing import Any

from models.session import SessionContext, UserRole


def _session_from_event(event: dict[str, Any]) -> SessionContext:
    """Build a SessionContext from the authenticated request context.

    TODO: extract the verified identity (subject, role, entitled patient ids) from the AgentCore
    identity context / Cognito claims. NEVER trust identity fields supplied in the raw prompt body.
    """
    claims = event.get("identity", {})  # placeholder shape
    return SessionContext(
        subject=claims.get("sub", "anonymous"),
        role=UserRole(claims.get("role", "patient")),
        entitled_patient_ids=tuple(claims.get("entitled_patient_ids", [])),
    )


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AgentCore runtime entrypoint."""
    ctx = _session_from_event(event)
    _ = ctx  # passed into agent.invoke once build_agent() is implemented
    # TODO:
    #   from agent import build_agent
    #   agent = build_agent()
    #   return agent.invoke(prompt=event["prompt"], session=ctx)
    raise NotImplementedError("Build agent and invoke with the scoped SessionContext")
