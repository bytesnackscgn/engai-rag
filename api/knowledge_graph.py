"""
Knowledge Graph Builder for the wiki directory.

Parses markdown files to extract nodes (pages) and edges (wikilinks).
Provides a simple graph structure for visualization and analysis.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Wikilink pattern: [[link-name]] or [[link-name|display text]]
WIKILINK_PATTERN = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')


class KnowledgeGraphBuilder:
    """Builds a knowledge graph from wiki markdown files."""

    def __init__(self, wiki_dir: str = "./wiki") -> None:
        self.wiki_dir = Path(wiki_dir).resolve()
        self._nodes: List[Dict] = []
        self._edges: List[Dict] = []
        self._connection_counts: Dict[str, int] = {}

    def parse_wiki(self) -> Dict[str, List[Dict]]:
        """
        Walk the wiki directory and parse all .md files.

        Returns
        -------
        Dict with 'nodes' and 'edges' lists.
        - nodes: [{id, label, type, connections}]
        - edges: [{source, target, type}]
        """
        self._nodes = []
        self._edges = []
        self._connection_counts = {}

        if not self.wiki_dir.exists():
            return {"nodes": [], "edges": []}

        # First pass: collect all nodes from .md files
        for md_file in self.wiki_dir.rglob("*.md"):
            self._add_node_from_file(md_file)

        # Second pass: extract edges (wikilinks) from file contents
        for md_file in self.wiki_dir.rglob("*.md"):
            self._extract_edges_from_file(md_file)

        # Apply connection counts to nodes
        for node in self._nodes:
            node_id = node["id"]
            node["connections"] = self._connection_counts.get(node_id, 0)

        return {"nodes": self._nodes, "edges": self._edges}

    def _add_node_from_file(self, file_path: Path) -> None:
        """Create a node from a markdown file."""
        # Get relative path from wiki_dir, strip .md extension
        rel_path = file_path.relative_to(self.wiki_dir)
        node_id = str(rel_path.with_suffix(""))

        # Determine node type based on parent directory
        parent_dir = file_path.parent.name
        if parent_dir == "concepts":
            node_type = "concept"
        elif parent_dir == "summaries":
            node_type = "document"
        elif parent_dir == "sources":
            node_type = "document"
        elif parent_dir == "explorations":
            node_type = "exploration"
        elif file_path.name == "index.md":
            node_type = "document"
        elif file_path.name == "log.md":
            node_type = "document"
        elif file_path.name == "AGENTS.md":
            node_type = "document"
        else:
            node_type = "document"

        # Use filename (without path) as label, replace hyphens/underscores with spaces
        label = file_path.stem.replace("-", " ").replace("_", " ").title()

        # Check if node already exists (avoid duplicates)
        if not any(n["id"] == node_id for n in self._nodes):
            self._nodes.append({
                "id": node_id,
                "label": label,
                "type": node_type,
                "connections": 0,  # will be updated later
            })

    def _extract_edges_from_file(self, file_path: Path) -> None:
        """Parse file content for wikilinks and create edges."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return

        rel_path = file_path.relative_to(self.wiki_dir)
        source_id = str(rel_path.with_suffix(""))

        # Find all wikilinks
        for match in WIKILINK_PATTERN.finditer(content):
            target_link = match.group(1).strip()

            # Resolve target to node ID
            target_id = self._resolve_wikilink_target(target_link, file_path)

            if target_id and target_id != source_id:
                # Create edge
                edge = {
                    "source": source_id,
                    "target": target_id,
                    "type": "links",
                }
                if edge not in self._edges:
                    self._edges.append(edge)

                # Increment connection counts
                self._connection_counts[source_id] = self._connection_counts.get(source_id, 0) + 1
                self._connection_counts[target_id] = self._connection_counts.get(target_id, 0) + 1

    def _resolve_wikilink_target(self, link: str, source_file: Path) -> str | None:
        """
        Resolve a wikilink to a node ID.

        Handles:
        - Absolute paths: [[concepts/daemmung]] → concepts/daemmung
        - Relative paths: [[../index]] → index
        - Simple names: [[daemmung]] → concepts/daemmung (if exists) or summaries/daemmung
        """
        # Already a full path (contains /)
        if "/" in link:
            # Normalize: remove leading/trailing slashes, ensure no .md
            normalized = link.rstrip(".md").strip("/")
            # Check if this node exists
            candidate = self.wiki_dir / (normalized + ".md")
            if candidate.exists() or any(n["id"] == normalized for n in self._nodes):
                return normalized
            return None

        # Simple name - try to find in concepts/ first, then summaries/
        candidates = [
            f"concepts/{link}",
            f"summaries/{link}",
            f"explorations/{link}",
            link,  # root level
        ]

        for candidate in candidates:
            full_path = self.wiki_dir / (candidate + ".md")
            if full_path.exists() or any(n["id"] == candidate for n in self._nodes):
                return candidate

        return None
