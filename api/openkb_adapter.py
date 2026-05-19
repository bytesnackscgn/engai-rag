"""
OpenKBAdapter — thin translation layer between the FastAPI wrapper and OpenKB.

This module is intentionally a **skeleton**.  Actual OpenKB integration
(importing the client, making real calls) is deferred to a later task so
the architecture can be reviewed and approved first.

Layer contract
--------------
- The adapter owns *how* OpenKB is called.
- The HTTP layer (main.py) owns *when* and *with which payloads*.
- Neither layer reimplements retrieval, wiki compilation, or chat sessions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from api.models import AnalysisResponse, ChatResponse, Source

logger = logging.getLogger(__name__)


class OpenKBAdapter:
    """
    Thin adapter wrapping the OpenKB client.

    Parameters
    ----------
    config_path:
        Path to the OpenKB configuration file (e.g. ``openkb.yaml``).
        Stored for later use when the real client is wired up.
    """

    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        # TODO (engai-rag-kdw): initialise the real OpenKB client here.
        # from openkb import OpenKBClient
        # self._kb = OpenKBClient(config_path=config_path)
        logger.info("OpenKBAdapter initialised with config_path=%s", config_path)


    async def chat(
        self,
        message: str,
        history: List[Dict[str, Any]],
    ) -> ChatResponse:
        """
        Send a chat message to OpenKB and return a structured response.

        Parameters
        ----------
        message:
            The user's question.
        history:
            Prior conversation turns as ``[{role, content}, …]``.

        Returns
        -------
        ChatResponse
            Structured answer with sources and confidence score.
        """
        logger.debug("OpenKBAdapter.chat called: message=%r", message)
        # TODO (engai-rag-kdw): replace stub with real OpenKB call.
        # result = self._kb.query(question=message, context=history)
        # return ChatResponse(
        #     response=result.answer,
        #     sources=self._extract_sources(result),
        #     confidence=result.confidence,
        # )
        raise NotImplementedError(
            "OpenKBAdapter.chat is a skeleton — wire up the OpenKB client first."
        )

    async def analyze(
        self,
        analysis_type: str,
        context: Dict[str, Any],
    ) -> AnalysisResponse:
        """
        Run a domain-specific analysis via one or more OpenKB queries.

        Parameters
        ----------
        analysis_type:
            One of ``kfw_qualification``, ``energy_audit``,
            ``renovation_potential``, ``cost_benefit``.
        context:
            Arbitrary key-value data driving the analysis
            (e.g. ``{"building_age": 1975, "heating_type": "gas"}``).

        Returns
        -------
        AnalysisResponse
            Structured analysis result with supporting sources.
        """
        logger.debug(
            "OpenKBAdapter.analyze called: analysis_type=%r context=%r",
            analysis_type,
            context,
        )
        # TODO (engai-rag-kdw): implement per-analysis-type query orchestration.
        raise NotImplementedError(
            "OpenKBAdapter.analyze is a skeleton — implement query orchestration first."
        )

    def retrieve_source(self, doc_id: str) -> Source:
        """
        Fetch a single source document by its OpenKB document ID.

        Parameters
        ----------
        doc_id:
            The OpenKB document identifier.

        Returns
        -------
        Source
            Normalised source object.
        """
        logger.debug("OpenKBAdapter.retrieve_source called: doc_id=%r", doc_id)
        # TODO (engai-rag-kdw): replace stub with real OpenKB call.
        raise NotImplementedError(
            "OpenKBAdapter.retrieve_source is a skeleton — wire up the OpenKB client first."
        )


    def _extract_sources(self, openkb_result: Any) -> List[Source]:
        """
        Normalise OpenKB query output into a list of :class:`Source` objects.

        OpenKB may return sources as plain dicts, named tuples, or objects
        with attribute access.  This helper handles all three shapes so the
        rest of the adapter never needs to know the raw format.

        Parameters
        ----------
        openkb_result:
            The raw return value from an OpenKB query/chat call.

        Returns
        -------
        List[Source]
            Zero or more normalised source citations.
        """
        # TODO (engai-rag-kdw): inspect actual OpenKB return type and
        # implement the extraction logic here.
        logger.debug(
            "OpenKBAdapter._extract_sources called — stub returning empty list"
        )
        return []
