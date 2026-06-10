"""FastAPI wrapper example (skeleton).

A thin REST front door over the agent for local testing. Run only after implementing the agent.
    uvicorn examples.api:app --reload
"""
from __future__ import annotations

# from fastapi import FastAPI, Depends, HTTPException
# from agent import build_agent
# from models.session import SessionContext, UserRole

# app = FastAPI(title="HealthLake Agent (skeleton)")


def get_session():
    """Resolve the caller's verified identity into a SessionContext.

    TODO: validate the bearer token / OIDC claims here. Do NOT accept identity from the request body.
    """
    raise NotImplementedError("Validate caller identity -> SessionContext")


# @app.post("/ask")
# def ask(prompt: str, session=Depends(get_session)):
#     agent = build_agent()
#     return agent.invoke(prompt=prompt, session=session)
