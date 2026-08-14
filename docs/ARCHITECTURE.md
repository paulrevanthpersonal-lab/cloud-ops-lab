# Architecture

```mermaid
flowchart TB
  UI[Operations dashboard] --> API[Python standard-library API]
  API --> CATALOG[30 labs and 30 incident patterns]
  API --> RUNS[(SQLite validation runs)]
  UI --> DOCS[Symptom-based runbooks]
  OPS[Operator] --> CLI[Redacting diagnostic CLI]
  CLI --> EVIDENCE[Hashed evidence bundle]
  TF[Terraform] --> AZURE[Azure lab resources]
  AZURE --> LOGS[Log Analytics]
  LOGS --> ALERTS[Action group]
```

The lab separates presentation, immutable practice content, persisted validation evidence, safe diagnostic collection, runbook decisions, and infrastructure. The dashboard can read the versioned catalog directly on GitHub Pages; running `server.py` adds API filtering and SQLite-backed run records. Real credentials and production endpoints are intentionally excluded.
