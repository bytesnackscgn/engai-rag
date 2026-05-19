"""
FastAPI wrapper around OpenKB.

Provides HTTP endpoints for chat and analysis functionality,
with API-key authentication and structured request/response validation.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from api.knowledge_graph import KnowledgeGraphBuilder
from api.models import AnalysisRequest, AnalysisResponse, ChatRequest, ChatResponse
from api.openkb_adapter import OpenKBAdapter
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

# Global adapter instance (initialized at startup)
_adapter: OpenKBAdapter | None = None


def get_adapter() -> OpenKBAdapter:
    """Dependency that returns the initialized OpenKBAdapter."""
    if _adapter is None:
        raise HTTPException(status_code=500, detail="OpenKB adapter not initialized")
    return _adapter


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    """
    API key authentication middleware.
    
    Raises HTTPException if the API key is invalid.
    """
    valid_keys = os.getenv("API_KEYS", "").split(",")
    valid_keys = [k.strip() for k in valid_keys if k.strip()]
    
    if not valid_keys or x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


app = FastAPI(title="EngAI RAG API", version="1.0.0")

# CORS configuration (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize the OpenKB adapter on application startup."""
    global _adapter
    
    config_path = os.getenv("OPENKB_CONFIG", "openkb.yaml")
    logger.info("Initializing OpenKBAdapter with config_path=%s", config_path)
    
    try:
        _adapter = OpenKBAdapter(config_path=config_path)
        logger.info("OpenKBAdapter initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize OpenKBAdapter: %s", e)
        raise


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    adapter: OpenKBAdapter = Depends(get_adapter),
    _: None = Depends(verify_api_key),
) -> ChatResponse:
    """
    Chat endpoint for general Q&A.
    
    Accepts a user message and optional conversation history,
    returns an LLM-generated answer with source citations.
    """
    logger.info(
        "Received chat request: message_len=%d history_len=%d save_context=%s",
        len(request.message),
        len(request.history),
        request.save_context,
    )
    
    try:
        response = await adapter.chat(
            message=request.message,
            history=request.history,
            save_context=request.save_context,
        )
        return response
    except NotImplementedError as e:
        logger.error("Adapter not implemented: %s", e)
        raise HTTPException(status_code=503, detail="Chat service not ready")
    except RuntimeError as e:
        logger.error("OpenKB query failed: %s", e)
        raise HTTPException(status_code=503, detail="Knowledge base unavailable")
    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(
    request: AnalysisRequest,
    adapter: OpenKBAdapter = Depends(get_adapter),
    _: None = Depends(verify_api_key),
) -> AnalysisResponse:
    """
    Domain-specific analysis endpoint.

    Supported analysis types:
    - kfw_qualification: Identify applicable KfW funding programs
    - energy_audit: Recommend energy-saving measures
    - renovation_potential: Analyze renovation potential
    - cost_benefit: Cost-benefit analysis of recommended measures

    The context dict should contain building specifications and any
    relevant data for the analysis.
    """
    logger.debug(
        "Received analyze request: analysis_type=%r context=%r",
        request.analysis_type,
        request.context,
    )

    # Validate analysis_type
    valid_types = {"kfw_qualification", "energy_audit", "renovation_potential", "cost_benefit"}
    if request.analysis_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid analysis_type. Must be one of: {', '.join(sorted(valid_types))}",
        )

    try:
        result = await adapter.analyze(request.analysis_type, request.context)
        return result
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.exception("Error in analyze endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/knowledge-graph")
async def knowledge_graph_endpoint(
    _: None = Depends(verify_api_key),
) -> Dict[str, List[Dict]]:
    """
    Return the knowledge graph built from wiki markdown files.

    Parses wiki/ directory for .md files and extracts:
    - Nodes: all markdown pages with id, label, type, and connection count
    - Edges: wikilinks [[...]] between pages

    The graph is rebuilt on each request (no caching).
    """
    logger.debug("Generating knowledge graph from wiki/")
    try:
        builder = KnowledgeGraphBuilder(wiki_dir="./wiki")
        graph = builder.parse_wiki()
        return graph
    except Exception as e:
        logger.exception("Error generating knowledge graph")
        raise HTTPException(status_code=500, detail="Failed to generate knowledge graph") from e
