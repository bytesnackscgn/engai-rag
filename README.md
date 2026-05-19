# KfW Energieberater Assistent

> Vectorless RAG-basierter Chat-Assistent für KfW-Förderberatung und Energieberatung

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![OpenKB](https://img.shields.io/badge/OpenKB-0.2.1-orange.svg)](https://github.com/VectifyAI/OpenKB)
[![Lint](https://github.com/vectifyai/engai-rag/workflows/lint/badge.svg)](https://github.com/vectifyai/engai-rag/actions/workflows/lint.yml)

## 📋 Projektübersicht

Der **KfW Energieberater Assistent** ist ein intelligenter Chatbot, der Energieberater, Sanierungsberater und KfW-Antragsteller bei Fragen zu Förderprogrammen, energetischer Sanierung und Gebäudeeffizienz unterstützt. Das System nutzt **OpenKB** als Wissensbasis mit Vectorless RAG-Technologie und antwortet präzise auf Basis offizieller KfW-Dokumentation und technischer Richtlinien.

### Kern-Features

- 🗃️ **Automatisierte Wissensbasis**: OpenKB generiert aus PDFs/Texten eine durchsuchbare Wiki-Struktur
- 💬 **Kontext-sensitive Chats**: Versteht Gesprächsverlauf und liefert quellengestützte Antworten
- 🔍 **Quellen-Nachweise**: Jede Antwort zeigt die genauen Dokumentenreferenzen
- 📊 **Knowledge Graph**: Visualisiert Zusammenhänge zwischen Konzepten
- 🚀 **Einfache Deployment**: Docker Compose oder Bare-Metal
- 🔐 **API-Key Auth**: Sichere Zugriffskontrolle für Produktionsbetrieb

### Zielgruppe

- KfW-Berater und Energieberater
- Antragsteller für Sanierungsmaßnahmen
- Architekten und Planer
- Kommunale Energiebeauftragte

---

## 🏗️ Architektur

### System-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                    REPOSITORY                           │
│  (externe Ordnerstruktur mit Dokumenten)                │
└─────────────┬───────────────────────────────────────────┘
              │
              │ (neue/veränderte Dateien)
              ▼
┌─────────────────────────────────────────────────────────┐
│                  INDEX MANAGER CLI                       │
│  - Prüft status.json                                     │
│  - Identifiziert neue Dokumente                         │
│  - Steuert OpenKB Integration                            │
└─────┬───────────────────────────────────────────────────┘
      │
      │ (updates Wiki)
      ▼
┌─────────────────────────────────────────────────────────┐
│                   OPENKB WIKI                           │
│  - wiki/index.md (Übersicht)                             │
│  - wiki/concepts/ (Synthese-Konzepte)                   │
│  - wiki/summaries/ (Dokument-Zusammenfassungen)         │
│  - wiki/sources/ (Volltext-Exporte)                     │
└─────┬───────────────────────────────────────────────────┘
      │
      │ (Wissensabfrage)
      ▼
┌─────────────────────────────────────────────────────────┐
│                    FASTAPI SERVER                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Endpoints:                                       │   │
│  │  - POST /chat                                       │   │
│  │  - POST /chat/context-aware                        │   │
│  │  - GET /sources/<doc_id>                            │   │
│  │  - GET /knowledge-graph                            │   │
│  │  - GET /status                                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────┬───────────────────────────────────────────────────┘
      │
      │ (LLM-Anfrage)
      ▼
┌─────────────────────────────────────────────────────────┐
│                  LLM (OpenRouter)                       │
│  Model: z-ai/glm-4.7-flash                               │
└─────────────────────────────────────────────────────────┘
```

### Datenfluss

1. **Dokumente** liegen im `raw/`-Ordner (PDFs, TXT, DOCX)
2. **Index Manager CLI** erkennt neue/geänderte Dateien über `status.json`
3. **OpenKB** verarbeitet Dokumente → generiert Wiki in `wiki/`
4. **FastAPI** bedient HTTP-Anfragen, fragt Wiki ab
5. **LLM** (OpenRouter) erstellt Antworten basierend auf Wiki-Kontext
6. **Quellen** werden aus Wiki referenziert und zurückgeliefert

---

## 🚀 Quick Start

### Voraussetzungen

- Python 3.11+
- OpenRouter API-Key (kostenpflichtig, aber günstig)
- Git
- (Optional) Docker & Docker Compose

### 1. Repository klonen

```bash
git clone <repository-url>
cd engai-rag
```

### 2. Python-Umgebung einrichten

```bash
# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# CLI installieren (editable)
pip install -e .
```

### 3. Konfiguration

```bash
# .env.example kopieren
cp .env.example .env

# .env mit deinem OpenRouter API-Key editieren:
# OPENROUTER_API_KEY=sk-or-...
# API_KEY=dein_geheimer_api_key_fuer_die_api
```

### 4. OpenKB initialisieren

```bash
# OpenKB Konfiguration erstellen
mkdir -p .openkb
cat > .openkb/config.yaml <<EOF
model: z-ai/glm-4.7-flash
language: de
pageindex_threshold: 20
EOF
```

### 5. Dokumente hinzufügen

```bash
# Dokumente in raw/ kopieren
mkdir -p raw/kfws raw/sanierung
# Kopiere deine PDFs/Dateien nach raw/
```

### 6. Ersten Index durchführen

```bash
# Repository sync (optional, wenn externe Quelle)
engaichat repo sync

# Index status prüfen
engaichat index check

# Ersten Index laufen lassen
engaichat index run
```

Das kann einige Minuten dauern, abhängig von Dokumentenanzahl.

### 7. FastAPI Server starten

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. API testen

```bash
# Health Check
curl http://localhost:8000/api/health

# Chat testen
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dein_api_key" \
  -d '{"message": "Was sind die KfW-Förderungen für Wärmedämmung?"}'
```

### 9. Swagger UI öffnen

Navigiere zu: http://localhost:8000/docs

Hier kannst du die API interaktiv testen.

---

## 📖 OpenKB Setup

OpenKB ist das Herzstück der Wissensbasis. Es wandelt Dokumente in eine durchsuchbare Wiki-Struktur um.

### OpenKB Grundlagen

OpenKB arbeitet in zwei Phasen:
1. **PageIndex**: Teilt lange Dokumente in Seiten auf (Chunking)
2. **Synthese**: LLM erstellt Konzepte und Verbindungen

### OpenKB Commands

Die CLI `engaichat` bietet folgende Befehle:

```bash
# Status anzeigen
engaichat status

# Index-Management
engaichat index check       # Status von index_status.json prüfen
engaichat index scan        # Repository nach neuen Dateien scannen
engaichat index sync        # Dateien aus externem Repository syncen
engaichat index run         # Hybrid-Index durchführen (inkrementell)
engaichat index force       # Voll-Index aller Dateien (reset)

# Wiki-Validierung
engaichat validate          # Wiki-Integrität prüfen

# Chat-Test (ohne API)
engaichat chat test         # Chat-Endpunkt testen

# Repository-Management
engaichat repo sync         # Alle Dateien aus externem Repo syncen
engaichat repo status       # Repo-Status anzeigen
```

### OpenKB Konfiguration

Die Konfiguration liegt in `.openkb/config.yaml`:

```yaml
# LLM Model (OpenRouter)
model: z-ai/glm-4.7-flash

# Sprache
language: de

# PageIndex Threshold (Seitenlänge in Tokens)
pageindex_threshold: 20

# Optional: Custom Prompt Templates
# prompts:
#   concept_synthesis: "templates/concept_prompt.txt"
```

### Wiki-Struktur

Nach dem Index steht das Wiki unter `wiki/`:

```
wiki/
├── index.md              # Hauptseite mit Übersicht
├── AGENTS.md             # Governance (wer was editieren darf)
├── log.md                # Änderungsprotokoll
├── sources/              # Volltext-Exporte aller Dokumente
│   ├── doc_001.md
│   └── doc_002.md
├── summaries/            # Automatische Zusammenfassungen
│   ├── doc_001_summary.md
│   └── doc_002_summary.md
├── concepts/             # Synthese-Konzepte (LLM-generiert)
│   ├── daemmung.md
│   ├── kfw_foerderung.md
│   └── energieausweis.md
└── explorations/         # Manuelle Ergänzungen
    └── faq.md
```

---

## 🔌 API Dokumentation

### Base URL

```
http://localhost:8000
```

### Authentifizierung

Alle Endpoints (außer `/health`, `/ready`, `/metrics`) erfordern einen API-Key im Header:

```
X-API-Key: dein_geheimer_key
```

Konfiguriert in `.env`:
```
API_KEY=dein_geheimer_api_key
API_KEYS_DEMO=demo_key  # für Demo-Zugang
```

### Endpoints

#### 1. Health & Monitoring

##### `GET /api/health`

Liveness-Check für Kubernetes/Container.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

##### `GET /api/ready`

Readiness-Check (prüft OpenKB-Verfügbarkeit).

**Response:**
```json
{
  "status": "ready",
  "openkb_available": true,
  "wiki_health": 95,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

##### `GET /api/metrics`

Prometheus-kompatible Metriken.

**Response:**
```
# HELP api_requests_total Total number of API requests
# TYPE api_requests_total counter
api_requests_total 1234

# HELP wiki_documents_total Total number of documents in wiki
# TYPE wiki_documents_total gauge
wiki_documents_total 150

# HELP index_pending_files Number of files pending indexing
# TYPE index_pending_files gauge
index_pending_files 5
```

#### 2. Chat API

##### `POST /api/chat`

Kontext-sensitive Chat-Anfrage.

**Request:**
```json
{
  "message": "Was sind die KfW-Förderungen für Wärmedämmung?",
  "history": [
    {
      "role": "user",
      "content": "Erkläre die Grundlagen der energetischen Sanierung."
    },
    {
      "role": "assistant",
      "content": "Energetische Sanierung umfasst Maßnahmen..."
    }
  ],
  "save_context": true,
  "max_sources": 5
}
```

**Response:**
```json
{
  "response": "Die KfW bietet verschiedene Förderprogramme für Wärmedämmung an. Das Programm KfW 215 fördert Einzelmaßnahmen wie Außenwanddämmung mit bis zu 20% Zuschuss...",
  "sources": [
    {
      "doc_id": "doc_001",
      "title": "KfW-Pflichtenheft 2024",
      "page": 15,
      "text": "Bei der Außenwanddämmung ist ein U-Wert von ≤ 0,15 W/(m²K) für die Förderung erforderlich.",
      "confidence": 0.95
    }
  ],
  "confidence": 0.92,
  "tokens_used": 1450
}
```

##### `POST /api/chat/context-aware`

Erweiterter Chat mit explizitem Kontext.

**Request:**
```json
{
  "message": "Welche Förderung passt für mein Gebäude?",
  "context": {
    "building_type": "Wohnhaus",
    "year_built": 1980,
    "heating_system": "Gasheizung",
    "planned_measures": ["Daemmung Aussenwand", "Dachdaemmung"]
  }
}
```

**Response:**
```json
{
  "response": "Für Ihr 1980 gebautes Wohnhaus mit Gasheizung empfehle ich die KfW 215 (Einzelmaßnahmen) für die geplante Außenwand- und Dachdämmung...",
  "recommended_programs": [
    {
      "program": "KfW 215",
      "type": "Zuschuss",
      "max_amount": "25.000 €",
      "requirements": ["U-Wert ≤ 0,15", "Fachplanung"]
    }
  ],
  "sources": [...]
}
```

#### 3. Source Retrieval

##### `GET /api/sources/{doc_id}`

Lädt ein spezifisches Dokument aus dem Wiki.

**Response:**
```json
{
  "id": "doc_001",
  "title": "KfW-Pflichtenheft 2024",
  "content": "Vollständiger Text des Dokuments...",
  "summary": "Zusammenfassung des Dokuments...",
  "metadata": {
    "source_path": "raw/kfws/pflichtenheft_2024.pdf",
    "indexed_at": "2024-01-15T10:45:00Z",
    "pages": 45
  }
}
```

#### 4. Knowledge Graph

##### `GET /api/knowledge-graph`

Gibt den Wissensgraphen als JSON zurück.

**Query Parameters:**
- `min_connections` (default: 2) — Mindestanzahl Verbindungen pro Knoten
- `concept_type` (optional) — Filter nach Konzepttyp

**Response:**
```json
{
  "nodes": [
    {"id": "daemmwand", "label": "Wärmedämmung", "type": "concept", "connections": 12},
    {"id": "kfw_215", "label": "KfW 215", "type": "program", "connections": 8},
    {"id": "u_wert", "label": "U-Wert", "type": "metric", "connections": 6}
  ],
  "edges": [
    {"source": "daemmwand", "target": "kfw_215", "type": "mentioned_in", "weight": 0.9},
    {"source": "daemmwand", "target": "u_wert", "type": "has_metric", "weight": 0.8}
  ]
}
```

#### 5. Status & Admin

##### `GET /api/status`

Systemstatus.

**Response:**
```json
{
  "index_status": {
    "last_scan": "2024-01-15T10:30:00Z",
    "total_documents": 150,
    "last_indexed": "2024-01-15T10:45:00Z",
    "pending_files": 5,
    "index_health": 0.95
  },
  "wiki_status": {
    "total_concepts": 45,
    "total_summaries": 150,
    "health_score": 95
  },
  "api_status": {
    "uptime": "99.9%",
    "active_sessions": 3,
    "requests_today": 1240
  }
}
```

##### `POST /api/index/trigger`

Manuellen Index-Trigger starten.

**Request:**
```json
{
  "full_index": false,
  "sync_first": true
}
```

**Response:**
```json
{
  "job_id": "idx_20240115_1030",
  "status": "started",
  "message": "Hybrid index started"
}
```

---

## 🐳 Deployment

### Docker Compose (Empfohlen)

#### 1. Dockerfile erstellen

```dockerfile
# api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

# CLI installieren
RUN pip install -e .

# Port
EXPOSE 8000

# Command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: api/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - API_KEY=${API_KEY}
      - OPENKB_CONFIG_PATH=/app/.openkb/config.yaml
      - RAW_DATA_DIR=/app/raw
      - WIKI_DIR=/app/wiki
    volumes:
      - ./raw:/app/raw
      - ./wiki:/app/wiki
      - ./cache:/app/cache
      - ./.openkb:/app/.openkb
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  cli:
    build:
      context: .
      dockerfile: api/Dockerfile
    volumes:
      - ./raw:/app/raw
      - ./wiki:/app/wiki
      - ./.openkb:/app/.openkb
      - ./logs:/app/logs
    depends_on:
      - api
    # CLI manuell aufrufen, z.B.:
    # docker-compose run --rm cli engaichat index run
```

#### 3. Deployment starten

```bash
# Environment variables setzen
export LLM_API_KEY=sk-or-...
export API_KEY=dein_geheimer_key

# Services starten
docker-compose up -d

# Logs ansehen
docker-compose logs -f api

# CLI-Befehl ausführen
docker-compose run --rm cli engaichat index run
```

#### 4. Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name kfw-assistent.deine-domain.de;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Bare-Metal Deployment

#### 1. Systemd Service

```ini
# /etc/systemd/system/kfw-assistent.service
[Unit]
Description=KfW Energieberater Assistent
After=network.target

[Service]
Type=simple
User=dein_user
WorkingDirectory=/opt/engai-rag
Environment="PATH=/opt/engai-rag/venv/bin"
Environment="LLM_API_KEY=sk-or-..."
Environment="API_KEY=dein_geheimer_key"
ExecStart=/opt/engai-rag/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren
sudo systemctl daemon-reload
sudo systemctl enable kfw-assistent
sudo systemctl start kfw-assistent

# Status checken
sudo systemctl status kfw-assistent

# Logs
sudo journalctl -u kfw-assistent -f
```

#### 2. Gunicorn für Production

```bash
pip install gunicorn

# Start mit Gunicorn
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

---

## 📁 Verzeichnisstruktur

```
engai-rag/
├── raw/                          # Originaldokumente (PDFs, TXT, DOCX)
│   ├── kfws/                     # KfW-Programmdokumente
│   ├── sanierung/                # Sanierungsrichtlinien
│   ├── berechnungen/             # Berechnungstools
│   └── muster/                   # Musteranträge
├── wiki/                         # OpenKB Knowledge Base (generiert)
│   ├── index.md                  # Hauptseite
│   ├── AGENTS.md                 # Wiki-Governance
│   ├── log.md                    # Änderungsprotokoll
│   ├── sources/                  # Volltext-Exporte
│   ├── summaries/                # Dokument-Zusammenfassungen
│   ├── concepts/                 # Synthese-Konzepte
│   └── explorations/             # Manuelle Ergänzungen
├── .openkb/                      # OpenKB Konfiguration
│   └── config.yaml
├── api/                          # FastAPI Backend
│   ├── __init__.py
│   ├── main.py                   # FastAPI App Entry Point
│   ├── models.py                 # Pydantic Models
│   ├── chat_service.py           # Chat-Logik
│   ├── index_service.py          # Index-Management
│   ├── auth.py                   # API-Key Authentifizierung
│   └── middleware.py              # Custom Middleware
├── cli/                          # Command Line Interface
│   ├── __init__.py
│   ├── commands.py               # CLI Commands (Click)
│   ├── index_manager.py          # Index-Logik
│   ├── repo_manager.py           # Repository-Sync
│   └── utils.py                  # Hilfsfunktionen
├── scripts/                      # Utility Scripts
│   ├── sync_from_repo.py         # Sync von externem Repo
│   ├── trigger_index.py          # Index-Trigger
│   ├── generate_report.py        # Berichtserstellung
│   └── backup_wiki.py            # Wiki-Backup
├── cache/                        # Caching Layer
│   ├── index_status.json         # Status-Tracking
│   ├── file_list.json            # Datei-Liste
│   └── query_cache/              # Abfrage-Cache (optional)
├── logs/                         # Logs
│   ├── api.log
│   ├── cli.log
│   └── index.log
├── .env                          # Umgebungsvariablen (nicht committen!)
├── .env.example                  # Beispiel-Konfiguration
├── requirements.txt              # Python Dependencies
├── docker-compose.yml            # Docker Compose Config
├── Dockerfile                    # Docker Image
├── README.md                     # Diese Datei
└── INTEGRATION_PLAN_KFW_ENERGIEBERATER.md  # Detaillierter Plan
```

---

## 🐛 Troubleshooting

### Häufige Probleme & Lösungen

#### 1. OpenKB nicht erreichbar / Initialisierung fehlgeschlagen

**Symptom:** `openkb init` oder Index-Vorgang schlägt fehl mit "OpenKB not available".

**Lösung:**
```bash
# 1. Prüfe .openkb/config.yaml
cat .openkb/config.yaml

# 2. Stelle sicher, dass OPENROUTER_API_KEY gesetzt ist
echo $OPENROUTER_API_KEY

# 3. Teste OpenRouter direkt
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models

# 4. OpenKB manuell initialisieren
openkb init --config .openkb/config.yaml
```

#### 2. Index-Status hängt in "pending"

**Symptom:** `engaichat index check` zeigt viele Dateien als "pending" an, Index läuft nicht.

**Lösung:**
```bash
# 1. Prüfe raw/ Ordner
ls -la raw/

# 2. Prüfe index_status.json
cat cache/index_status.json

# 3. Falls korrupt, neu starten
rm cache/index_status.json
engaichat index force

# 4. Logs checken
tail -f logs/cli.log
```

#### 3. LLM Timeout / Rate Limit

**Symptom:** API-Antworten dauern sehr lange oder schlagen fehl mit "timeout".

**Lösung:**
```bash
# 1. Timeout in .env erhöhen
OPENROUTER_TIMEOUT=120

# 2. Rate Limit prüfen (OpenRouter)
# OpenRouter hat Limits je nach Plan

# 3. Fallback-Modus: Lokales Modell (wenn verfügbar)
# In .openkb/config.yaml:
# model: local-model-name

# 4. Caching aktivieren (in api/chat_service.py)
# Cache-Lebensdauer auf 24h setzen
```

#### 4. Wiki-Lint Fehler

**Symptom:** `engaichat validate` zeigt Konflikte oder Lücken.

**Lösung:**
```bash
# 1. Lint-Report ansehen
engaichat validate --report

# 2. Konflikte manuell auflösen in wiki/
# - AGENTS.md prüfen (wer darf was editieren)
# - Doppelte Seiten zusammenführen

# 3. Wiki-Health Score prüfen
cat wiki/log.md | tail -20

# 4. Falls nötig: Wiki-Backup wiederherstellen
./scripts/backup_wiki.py --restore backup_20240115/
```

#### 5. API gibt 401 Unauthorized

**Symptom:** Alle API-Aufrufe schlagen fehl mit 401.

**Lösung:**
```bash
# 1. API-Key in .env prüfen
cat .env | grep API_KEY

# 2. API-Key im Request-Header korrekt setzen
curl -H "X-API-Key: dein_key" ...

# 3. Demo-Key verwenden (falls in .env gesetzt)
# API_KEYS_DEMO=demo_key
curl -H "X-API-Key: demo_key" ...
```

#### 6. Docker Compose: Volumes nicht gemountet

**Symptom:** Änderungen in `raw/` oder `wiki/` sind im Container nicht sichtbar.

**Lösung:**
```yaml
# docker-compose.yml prüfen:
volumes:
  - ./raw:/app/raw   # RELATIVER PFAD, nicht absolut!
  - ./wiki:/app/wiki
```

#### 7. OpenKB generiert keine Konzepte

**Symptom:** `wiki/concepts/` ist leer nach Index.

**Lösung:**
```bash
# 1. Prüfe, ob Summaries generiert wurden
ls wiki/summaries/

# 2. Falls nein: PageIndex Threshold anpassen
# In .openkb/config.yaml:
pageindex_threshold: 50  # für längere Dokumente

# 3. Manuellen Konzept-Synthesis anstoßen
openkb synthesize --all

# 4. Logs prüfen
tail -f logs/index.log
```

#### 8. Performance: Langsame API-Antworten

**Symptom:** Chat-Antworten dauern >30 Sekunden.

**Lösung:**
```bash
# 1. Query-Cache aktivieren
# In api/chat_service.py:
cache_ttl = 3600  # 1 Stunde

# 2. Wiki-Health prüfen (zu viele Konzepte?)
cat wiki/index.md | grep "## Concepts"

# 3. OpenRouter Modell wechseln (schnelleres)
# In .openkb/config.yaml:
model: z-ai/glm-4.7-flash  # ist bereits schnell

# 4. Max Sources reduzieren
# Im Request: "max_sources": 3 statt 5
```

#### 9. Speicherplatz voll

**Symptom:** Disk full, Index bricht ab.

**Lösung:**
```bash
# 1. Cache leeren
rm -rf cache/query_cache/*

# 2. Alte Logs löschen
find logs/ -name "*.log" -mtime +30 -delete

# 3. Wiki-Backups aufräumen
ls scripts/backups/

# 4. Große raw/Dateien prüfen
du -sh raw/* | sort -hr | head -10
```

#### 10. Git Merge Conflicts in Wiki

**Symptom:** `wiki/` hat Merge-Conflicts nach Git-Pull.

**Lösung:**
```bash
# 1. AGENTS.md prüfen — wer ist verantwortlich?
cat wiki/AGENTS.md

# 2. Konflikte manuell auflösen
# - <<<<<<< HEAD
# - =======
# - >>>>>>> branch-name
# entfernen und konsolidieren

# 3. Wiki validieren
engaichat validate

# 4. Commit mit klarer Message
git add wiki/
git commit -m "docs: resolve wiki merge conflicts"
```

---

## 🤝 Contributing

### Dokumente hinzufügen

1. **Dokumente in `raw/` ablegen**
   ```bash
   cp mein_dokument.pdf raw/kfws/
   ```

2. **Index auslösen**
   ```bash
   engaichat index run
   ```

3. **Wiki prüfen**
   ```bash
   # Sieh nach, ob Konzepte korrekt generiert wurden
   ls wiki/concepts/
   cat wiki/concepts/daemmung.md
   ```

4. **Bei Bedarf manuell ergänzen**
   - Im `wiki/explorations/`-Ordner manuelle Ergänzungen erstellen
   - `wiki/AGENTS.md` beachten (Governance)

### Wiki-Review

1. **Health Check**
   ```bash
   engaichat validate --report
   ```

2. **Konzepte prüfen**
   - Sind alle wichtigen Themen abgedeckt?
   - Gibt es Duplikate?
   - Sind Quellen korrekt verlinkt?

3. **Logs prüfen**
   ```bash
   tail -f wiki/log.md
   ```

4. **Pull Request stellen**
   - Nur `wiki/`-Änderungen (keine `raw/`-Dateien!)
   - Klare Commit-Messages: `docs: add concept for KfW 215`
   - Review durch Team-Member einholen

### Code-Beiträge

- **API-Endpoints**: `api/`-Ordner
- **CLI-Commands**: `cli/commands.py`
- **Tests**: `tests/` (noch nicht vorhanden, bitte einrichten!)

### Style Guide

- **Python**: PEP 8, Black formatting
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`)
- **Wiki**: Deutsche Sprache, klare Quellenangaben

---

## 📚 Weiterentwicklung

### Geplante Features

- [ ] **Web-UI**: Einfaches HTML/JS Frontend für Chat
- [ ] **Knowledge Graph Visualization**: D3.js oder Cytoscape
- [ ] **Export**: PDF-Reports für Beratungen
- [ ] **Multi-Tenant**: Separate Wikis pro Kunde
- [ ] **Analytics**: Häufigste Fragen, Knowledge Gaps
- [ ] **Mobile App**: React Native

### Bekannte Einschränkungen

- **Keine Echtzeit-Indexierung**: Änderungen erfordern manuellen Index-Trigger
- **Keine User-Management**: API-Key ist einzige Auth
- **Keine Rate-Limiting**: Bei öffentlichem Zugang muss hinzugefügt werden
- **OpenRouter-Kosten**: Pro Token, für Production Budget planen

---

## 📞 Support & Wartung

### Verantwortliche Teams

- **Backend**: FastAPI & Index-Management
- **AI/LLM**: Prompt Engineering & Model-Optimierung
- **Infrastructure**: Containerisierung & Monitoring
- **Domain Expertise**: KfW / Sanierungsberatung

### Maintenance Schedule

- **Täglich**: Log-Checks, Status-Überprüfung
- **Wöchentlich**: Wiki Lint, Health Checks
- **Monatlich**: Performance Review, Feature Updates

### Monitoring

```bash
# Health Check (Cronjob)
*/5 * * * * curl -f http://localhost:8000/api/health || systemctl restart kfw-assistent

# Metrics sammeln (Prometheus)
curl http://localhost:8000/api/metrics > /var/lib/prometheus/textfile_collector/kfw-assistent.prom
```

---

## 📄 Lizenz

MIT License — siehe LICENSE-Datei.

---

## 🙏 Danksagung

- [OpenKB](https://github.com/VectifyAI/OpenKB) von VectifyAI
- [FastAPI](https://fastapi.tiangolo.com/) von Sebastián Ramírez
- [OpenRouter](https://openrouter.ai/) für LLM-Zugang
- KfW für öffentliche Dokumentation

---

**Stand:** Januar 2024  
**Letzte Aktualisierung:** 2024-01-15  
**Kontakt:** support@engai-rag.de
