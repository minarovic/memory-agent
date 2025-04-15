"""Define the shared values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated

from memory_agent.analyzer import AnalysisResult


@dataclass(kw_only=True)
class State:
    """Main graph state."""

    messages: Annotated[list[AnyMessage], add_messages]
    """The messages in the conversation."""
    
    company_analysis: Optional[AnalysisResult] = None
    """Výsledek analýzy společností z uživatelského dotazu."""


__all__ = [
    "State",
]
