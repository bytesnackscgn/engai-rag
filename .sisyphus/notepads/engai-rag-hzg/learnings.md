# Epic 4: Web UI & Production Readiness

## Key Decisions
- **Web UI**: Vanilla HTML/JS — no framework overhead for MVP
- **Docker**: Multi-service compose (api + cli)
- **Monitoring**: /api/health, /api/ready, /api/metrics (Prometheus format)
- **Deployment**: Docker-first, bare-metal as fallback

## Service Architecture (Docker)
```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    volumes: [./raw:/app/raw, ./wiki:/app/wiki, ./cache:/app/cache]
  cli:
    build: .
    volumes: [./raw:/app/raw, ./wiki:/app/wiki]
    depends_on: [api]
```

## Health Endpoints
- `GET /api/health` → 200 OK (liveness)
- `GET /api/ready` → 200/503 (readiness + OpenKB check)
- `GET /api/metrics` → Prometheus text format

## Blockers / Open Questions
- [ ] Web UI design: chat-only or also source browser?
- [ ] Multi-tenant: separate wiki/ per tenant or single wiki with filtering?
- [ ] Monitoring: Prometheus + Grafana or simple health checks only?
