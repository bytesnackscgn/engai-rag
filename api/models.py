"""
Pydantic models for the FastAPI wrapper around OpenKB.

These models define the public API contract.  They are deliberately
decoupled from OpenKB's internal types so the wrapper can evolve
independently.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Source(BaseModel):
    """A single source citation extracted from an OpenKB result."""

    doc_id: str = Field(..., description="Unique document identifier in OpenKB")
    title: str = Field(..., description="Human-readable document title")
    page: int = Field(..., description="Page number within the document")
    text: str = Field(..., description="Relevant text snippet from the source")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for this source (0–1)",
    )


class ChatRequest(BaseModel):
    """Incoming chat request from a client."""

    message: str = Field(..., description="User's question or message")
    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Prior conversation turns as list of {role, content} dicts",
    )
    save_context: bool = Field(
        default=False,
        description="Whether to persist this exchange in the session store",
    )


class ChatResponse(BaseModel):
    """Structured response returned to the client."""

    response: str = Field(..., description="LLM-generated answer")
    sources: List[Source] = Field(
        default_factory=list,
        description="Source citations backing the answer",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the answer (0–1)",
    )


class AnalysisRequest(BaseModel):
    """Request for a domain-specific analysis."""

    analysis_type: str = Field(
        ...,
        description=(
            "Type of analysis to run. "
            "Known values: kfw_qualification, energy_audit, "
            "renovation_potential, cost_benefit"
        ),
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary context data for the analysis (e.g. building specs)",
    )


class AnalysisResponse(BaseModel):
    """Structured analysis result returned to the client."""

    analysis: Dict[str, Any] = Field(
        ...,
        description="Analysis result as a structured dict",
    )
    sources: List[Source] = Field(
        default_factory=list,
        description="Source citations used in the analysis",
    )
