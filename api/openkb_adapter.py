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
        save_context: bool = False,
    ) -> ChatResponse:
        """
        Send a chat message to OpenKB and return a structured response.

        Parameters
        ----------
        message:
            The user's question.
        history:
            Prior conversation turns as ``[{role, content}, …]``.
        save_context:
            Whether to persist this exchange in the session store.

        Returns
        -------
        ChatResponse
            Structured answer with sources and confidence score.

        Raises
        ------
        RuntimeError
            If the OpenKB client is not initialized or the query fails.
        """
        logger.debug("OpenKBAdapter.chat called: message=%r save_context=%s", message, save_context)
        try:
            if not hasattr(self, "_kb"):
                from openkb import OpenKBClient
                self._kb = OpenKBClient(config_path=self.config_path)
                logger.info("OpenKB client initialized")

            try:
                result = self._kb.query(question=message, context=history, save=save_context)
            except TypeError:
                try:
                    result = self._kb.query(question=message, context=history, persist=save_context)
                except TypeError:
                    result = self._kb.query(question=message, context=history)
                    if save_context:
                        logger.warning("OpenKB query does not support save_context - it will be ignored")

            sources = self._extract_sources(result)

            return ChatResponse(
                response=result.answer,
                sources=sources,
                confidence=result.confidence,
            )
        except ImportError as e:
            logger.error("Failed to import OpenKB client: %s", e)
            raise RuntimeError("OpenKB client not available") from e
        except Exception as e:
            logger.exception("OpenKB query failed")
            raise RuntimeError(f"OpenKB query failed: {e}") from e

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
        
        # Build system prompt based on analysis type
        system_prompt = self._build_system_prompt(analysis_type)
        
        # Construct user prompt with building context
        user_prompt = self._build_user_prompt(context)
        
        # TODO (engai-rag-6ya): Replace with actual OpenKB query call
        # For now, we'll simulate the OpenKB query structure
        # result = await self._kb.analyze(
        #     system_prompt=system_prompt,
        #     user_prompt=user_prompt,
        #     analysis_type=analysis_type,
        # )
        
        # Simulate OpenKB result for now (to be replaced with real integration)
        # This structure should match what OpenKB returns
        class MockResult:
            def __init__(self):
                self.answer = "Analysis recommendations will appear here after OpenKB integration."
                self.sources = []
                self.confidence = 0.0
        
        result = MockResult()
        
        # Parse the result into structured recommendations
        recommendations = self._parse_recommendations(result, analysis_type)
        
        return AnalysisResponse(
            analysis={
                "analysis_type": analysis_type,
                "recommendations": recommendations,
                "summary": result.answer,
            },
            sources=self._extract_sources(result),
        )

    def _build_system_prompt(self, analysis_type: str) -> str:
        """Build the system prompt based on analysis type."""
        prompts = {
            "kfw_qualification": (
                "Du bist ein KfW-Förderberater. "
                "Welche KfW-Programme passen zu diesem Gebäude?"
            ),
            "energy_audit": (
                "Du bist ein Energieberater. "
                "Welche Sanierungsmaßnahmen empfehlen sich?"
            ),
            "renovation_potential": (
                "Analysiere das Sanierungspotenzial dieses Gebäudes."
            ),
            "cost_benefit": (
                "Erstelle eine Wirtschaftlichkeitsanalyse der empfohlenen Maßnahmen."
            ),
        }
        return prompts.get(analysis_type, "Führe eine Analyse durch.")

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build the user prompt with building context.
        
        Parameters
        ----------
        context:
            Building specifications and relevant data
            
        Returns
        -------
        str
            Formatted user prompt with context
        """
        if not context:
            return "Bitte analysiere das Gebäude."
        
        context_lines = ["Gebäudedaten:"]
        for key, value in context.items():
            context_lines.append(f"- {key}: {value}")
        
        return "\n".join(context_lines)

    def _parse_recommendations(
        self, openkb_result: Any, analysis_type: str
    ) -> List[Dict[str, Any]]:
        """
        Parse OpenKB result into structured recommendations.
        
        The recommendations should follow the format:
        [
            {
                "action": "Description of recommended action",
                "priority": "high|medium|low",
                "kfw_product": "KfW program number if applicable"
            },
            ...
        ]
        
        This is a placeholder implementation. When OpenKB integration
        is complete, this should parse the actual LLM response or
        structured data returned by OpenKB.
        """
        # TODO (engai-rag-kdw): Implement actual parsing logic based on
        # OpenKB's return format. For now, return empty list.
        logger.debug(
            "OpenKBAdapter._parse_recommendations called — returning empty list (stub)"
        )
        return []

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
        Normalise OpenKB query output into a list of Source objects.

        Handles dicts, objects with attributes, and nested structures.
        Expected source fields: doc_id, title, page, text (or snippet), confidence.
        """
        sources = []
        raw_sources = getattr(openkb_result, "sources", None)

        if raw_sources is None:
            logger.warning("OpenKB result has no 'sources' attribute")
            return []

        for src in raw_sources:
            try:
                if isinstance(src, dict):
                    doc_id = src.get("doc_id") or src.get("id") or src.get("document_id")
                    title = src.get("title") or src.get("doc_title") or ""
                    page = src.get("page") or src.get("page_number") or 0
                    text = src.get("text") or src.get("snippet") or src.get("content") or ""
                    confidence = src.get("confidence") or src.get("score") or 0.0
                else:
                    doc_id = getattr(src, "doc_id", None) or getattr(src, "id", None) or getattr(src, "document_id", None)
                    title = getattr(src, "title", None) or getattr(src, "doc_title", "") or ""
                    page = getattr(src, "page", None) or getattr(src, "page_number", 0) or 0
                    text = getattr(src, "text", None) or getattr(src, "snippet", None) or getattr(src, "content", None) or ""
                    confidence = getattr(src, "confidence", None) or getattr(src, "score", None) or 0.0

                if doc_id is None:
                    logger.warning("Skipping source with missing doc_id: %r", src)
                    continue

                sources.append(
                    Source(
                        doc_id=str(doc_id),
                        title=str(title),
                        page=int(page),
                        text=str(text),
                        confidence=float(confidence),
                    )
                )
            except (TypeError, ValueError) as e:
                logger.warning("Failed to extract source %r: %s", src, e)
                continue

        logger.debug("Extracted %d sources from OpenKB result", len(sources))
        return sources
