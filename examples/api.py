"""FastAPI front door over the agent for local testing.

Run after configuring .env:
    uvicorn examples.api:app --reload
"""
from __future__ import annotations

from fastapi import Depends, FastAPI

from agent import build_agent
from models.session import SessionContext, UserRole, set_current_session

app = FastAPI(title="HealthLake Agent")
_agent = build_agent()


def get_session() -> SessionContext:
    """Resolve the caller's verified identity into a SessionContext.

    Validate the bearer token or OIDC claims here. Do not accept identity from the request body.
    """
    # Replace with real token validation against your identity provider.
    return SessionContext(subject="local-dev", role=UserRole.ADMIN)


@app.post("/ask")
def ask(prompt: str, session: SessionContext = Depends(get_session)) -> dict[str, str]:
    set_current_session(session)
    return {"answer": str(_agent(prompt))}
