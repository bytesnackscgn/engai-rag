"""
Knowledge Graph Builder for the wiki directory.

Parses markdown files to extract nodes (pages) and edges (wikilinks).
Provides a simple graph structure for visualization and analysis.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

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
        rel_path = file_path.relative_to(self.wiki_dir)
        node_id = str(rel_path.with_suffix(""))

        parent_dir = file_path.parent.name
        if parent_dir == "concepts":
            node_type = "concept"
        elif parent_dir == "summaries":
            node_type = "document"
        elif parent_dir == "sources":
            node_type = "document"
        elif parent_dir == "explorations":
            node_type = "exploration"
        elif file_path.name in ("index.md", "log.md", "AGENTS.md"):
            node_type = "document"
        else:
            node_type = "document"

        label = file_path.stem.replace("-", " ").replace("_", " ").title()

        if not any(n["id"] == node_id for n in self._nodes):
            self._nodes.append({
                "id": node_id,
                "label": label,
                "type": node_type,
                "connections": 0,
            })

    def _extract_edges_from_file(self, file_path: Path) -> None:
        """Parse file content for wikilinks and create edges."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return

        rel_path = file_path.relative_to(self.wiki_dir)
        source_id = str(rel_path.with_suffix(""))

        for match in WIKILINK_PATTERN.finditer(content):
            target_link = match.group(1).strip()
            target_id = self._resolve_wikilink_target(target_link, file_path)

            if target_id and target_id != source_id:
                edge = {
                    "source": source_id,
                    "target": target_id,
                    "type": "links",
                }
                if edge not in self._edges:
                    self._edges.append(edge)

                self._connection_counts[source_id] = self._connection_counts.get(source_id, 0) + 1
                self._connection_counts[target_id] = self._connection_counts.get(target_id, 0) + 1

    def _resolve_wikilink_target(self, link: str, source_file: Path) -> str | None:
        if "/" in link:
            normalized = link.rstrip(".md").strip("/")
            candidate = self.wiki_dir / (normalized + ".md")
            if candidate.exists() or any(n["id"] == normalized for n in self._nodes):
                return normalized
            return None

        candidates = [
            f"concepts/{link}",
            f"summaries/{link}",
            f"explorations/{link}",
            link,
        ]

        for candidate in candidates:
            full_path = self.wiki_dir / (candidate + ".md")
            if full_path.exists() or any(n["id"] == candidate for n in self._nodes):
                return candidate

        return None

        candidates = [
            f"concepts/{link}",
            f"summaries/{link}",
            f"explorations/{link}",
            link,
        ]

        for candidate in candidates:
            full_path = self.wiki_dir / (candidate + ".md")
            if full_path.exists() or any(n["id"] == candidate for n in self._nodes):
                return candidate

        return None
