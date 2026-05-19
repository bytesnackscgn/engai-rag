# Epic 2: FastAPI Wrapper & Chat API

## Key Decisions
- **Thin wrapper only**: OpenKB already handles chat, query, sessions — wrapper adds HTTP layer + auth
- **No reimplementation**: Never rebuild what OpenKB provides natively
- **Source citation format**: {doc_id, title, page, text_snippet, confidence}
- **Auth**: X-API-Key header, multiple keys via .env

## OpenKB Client Integration
```python
class OpenKBAdapter:
    def __init__(self, config_path: str):
        from openkb import OpenKBClient  # or subprocess for CLI
        self.kb = OpenKBClient(config_path=config_path)
    
    async def chat(self, message, history):
        result = self.kb.query(question=message, context=history)
        return ChatResponse(
            response=result.answer,
            sources=self._extract_sources(result),
            confidence=result.confidence
        )
```

## Analysis Types
- `kfw_qualification`: Which KfW programs apply?
- `energy_audit`: Energy audit recommendations
- `renovation_potential`: Renovation potential analysis
- `cost_benefit`: Cost-benefit analysis

## Blockers / Open Questions
- [ ] Confirm OpenKB Python API availability (vs CLI-only)
- [ ] Determine if OpenKB query returns structured sources or just text
- [ ] Rate limiting strategy for OpenRouter API
