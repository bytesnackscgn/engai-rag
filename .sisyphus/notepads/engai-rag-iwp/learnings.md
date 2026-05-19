# Epic 1: Project Setup & OpenKB Foundation

## Key Decisions
- **LLM Model**: deepseek/deepseek-chat via OpenRouter (strong German + domain knowledge)
- **Language**: German (de) for wiki output
- **PageIndex Threshold**: 20 pages (PDFs ≥20 pages use PageIndex tree indexing)
- **Directory Structure**: raw/kfws/, raw/sanierung/, raw/berechnungen/, raw/muster/

## OpenKB Architecture Notes
- OpenKB already provides: `openkb init`, `openkb add`, `openkb chat`, `openkb query`, `openkb lint`, `openkb watch`
- Wiki structure: sources/, summaries/, concepts/, explorations/, reports/
- No vector DB needed — PageIndex handles long docs via tree index
- AGENTS.md controls wiki compilation behavior — customize for KfW domain

## KfW Domain Context
- Förderprogramme: KfW 151-219 (Efficiency House, Individual Measures, etc.)
- Normen: EnEV, GEG, Energieausweis (EnEV/Energieeinsparverordnung → GEG/Gebäudeenergiegesetz)
- Fachbegriffe: U-Wert, Wärmedämmung, Lüftungsanlage, Solarthermie, etc.
- Quellenpflicht: Förderbeträge müssen mit doc_id + page nachprüfbar sein

## Blockers / Open Questions
- [x] LLM_API_KEY needs to be set in .env before openkb init — **BLOCKING**: Currently `placeholder`, not a real key. `openkb add` fails with `AuthenticationError: DeepseekException - Authentication Fails (governor)`. Must set real OpenRouter API key before any ingestion can proceed.
- [x] Actual KfW PDF documents need to be sourced for raw/ — **BLOCKING**: raw/ only contains 4x README.md placeholders. No actual PDF/MD documents exist yet. `openkb add ./raw/` found 4 files (the READMEs) but all failed at compilation step due to auth error.
- [ ] AGENTS.md needs domain expert review for accuracy
- [ ] Model mismatch: .openkb/config.yaml uses `deepseek/deepseek-chat` but INTEGRATION_PLAN specifies `z-ai/glm-4.7-flash` via OpenRouter. Needs alignment.

## Ingestion Attempt (engai-rag-wfy) — 2026-05-19
- `openkb add ./raw/` ran, found 4 files (all README.md placeholders)
- All 4 failed at LLM compilation step: `AuthenticationError: DeepseekException - Authentication Fails (governor)`
- Root cause: `LLM_API_KEY=placeholder` in .env — not a valid API key
- `openkb lint`: "Nothing to lint — no documents indexed yet"
- `openkb list`: "No documents indexed yet"
- **Next steps**: (1) Set real LLM_API_KEY in .env, (2) Populate raw/ with actual KfW PDFs, (3) Re-run ingestion
