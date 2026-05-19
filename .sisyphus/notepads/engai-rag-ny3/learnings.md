# Epic 3: Knowledge Graph & Quality Assurance

## Key Decisions
- **Knowledge graph source**: wiki/concepts/*.md + wiki/summaries/*.md (wikilinks = edges)
- **Graph format**: nodes [{id, label, type, connections}], edges [{source, target, type}]
- **Lint automation**: GitHub Actions on push/PR to main
- **Obsidian**: Primary graph viewer — wiki/ is already an Obsidian vault

## Wiki Structure as Graph
```
wiki/
├── index.md          → node: "index" (hub node)
├── concepts/         → nodes: "daemmung", "kfw-215", "energieausweis", ...
│   └── *.md          → edges: [[daemmung]] links to [[kfw-215]]
├── summaries/        → nodes: "doc-001-summary", ...
└── explorations/     → nodes: saved queries
```

## Lint Checks (openkb lint)
- Contradictions between concept pages
- Orphan pages (no incoming links)
- Stale content (not updated after new document added)
- Missing summaries for indexed documents

## Blockers / Open Questions
- [ ] Confirm wiki/ structure after first openkb add run
- [ ] Determine caching strategy for /knowledge-graph endpoint
- [ ] Review checklist needs domain expert sign-off
