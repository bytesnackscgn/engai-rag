# FastAPI Wrapper Architecture

## Why a Thin Wrapper?

OpenKB already provides a complete knowledge-base engine: chat/query sessions,
wiki compilation, retrieval, and linting. Reimplementing any of that inside the
API layer would duplicate logic, create two sources of truth, and slow down
feature delivery.

This wrapper exists to do **three things** OpenKB does not:

1. **Expose OpenKB over HTTP** — so frontends, scripts, and third-party tools
   can call it without embedding the Python client.
2. **Add structured API concerns** — API-key auth, Pydantic request/response
   validation, and a stable contract that can evolve independently of OpenKB.
3. **Add the `/analyze` endpoint** — domain-specific analysis types (KfW
   qualification, energy audit, renovation potential, cost-benefit) that combine
   multiple OpenKB queries into a single structured response.

## Layer Responsibilities

```
┌─────────────────────────────────────────────────────────┐
│  HTTP Layer  (FastAPI routes, middleware, auth)         │
│  - Parse & validate requests (Pydantic)                 │
│  - X-API-Key authentication                              │
│  - Route to adapter methods                             │
│  - Return structured JSON responses                     │
├─────────────────────────────────────────────────────────┤
│  Adapter Layer  (OpenKBAdapter)                         │
│  - Translate API models → OpenKB calls                  │
│  - Extract & normalise source citations                 │
│  - Combine multiple OpenKB queries for /analyze         │
│  - Hide OpenKB internals from the HTTP layer            │
├─────────────────────────────────────────────────────────┤
│  OpenKB  (openkb chat / query / status / lint)          │
│  - Retrieval, wiki compilation, chat sessions           │
│  - LLM orchestration via OpenRouter                     │
│  - Confidence scoring                                   │
├─────────────────────────────────────────────────────────┤
│  LLM  (openrouter/z-ai/glm-4.7-flash via litellm/openrouter)   │
│  - Answer generation                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### What the Wrapper Adds

| Concern          | Handled by Wrapper | Handled by OpenKB |
|------------------|--------------------|--------------------|
| HTTP routing     | ✅                 | ❌                 |
| API-key auth     | ✅                 | ❌                 |
| Request/response validation | ✅        | ❌                 |
| Source citation extraction & normalisation | ✅ | ❌         |
| `/analyze` endpoint (multi-query orchestration) | ✅ | ❌ |
| Retrieval        | ❌                 | ✅                 |
| Wiki compilation | ❌                 | ✅                 |
| Chat sessions    | ❌                 | ✅                 |
| LLM calls        | ❌                 | ✅                 |

### What the Wrapper Does NOT Reimplement

- **Retrieval** — OpenKB's `query` / `chat` handles document lookup.
- **Wiki compilation** — OpenKB builds context windows from retrieved docs.
- **Chat sessions** — OpenKB manages conversation history and context.
- **LLM orchestration** — OpenKB routes to OpenRouter (deepseek/deepseek-chat).

## Module Layout

```
api/
├── ARCHITECTURE.md      # This file
├── models.py            # Pydantic request/response models
├── openkb_adapter.py    # OpenKBAdapter — thin translation layer
└── main.py              # FastAPI app (routes, auth middleware)
```

## Dependency Flow

```
main.py  →  OpenKBAdapter  →  OpenKB client  →  OpenRouter / LLM
   │            │
   │            └─ _extract_sources() normalises OpenKB output
   │               into List[Source] for structured responses
   │
   └─ Pydantic models enforce the public API contract
```

## Source Citation Format

Every response carries a `sources` list. Each source is:

```python
Source(
    doc_id="kfw-304-2024",
    title="KfW Efficiency House Standard",
    page=12,
    text="The maximum loan amount is EUR 120,000 …",
    confidence=0.87,
)
```

The adapter's `_extract_sources()` helper converts whatever OpenKB returns
(raw text, dicts, or objects) into this canonical format.

## Analysis Endpoint

`POST /analyze` accepts an `analysis_type` and `context` dict, then delegates
to OpenKBAdapter.analyze(), which runs one or more OpenKB queries and returns a
structured `AnalysisResponse`. Analysis types are defined in the epic notepad
and can be extended without touching the HTTP layer.
