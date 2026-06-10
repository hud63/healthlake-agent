"""Agent response model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResponse:
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)  # tool name + resource refs
    tool_calls: list[str] = field(default_factory=list)
    truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "sources": self.sources,
            "tool_calls": self.tool_calls,
            "truncated": self.truncated,
        }
