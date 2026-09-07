# API contract

- `GET /api/health` reports service readiness.
- `GET /api/labs` returns 30 guided exercises and supports text, category, and difficulty filters.
- `GET /api/incidents` returns 30 incident patterns with root cause, safe remediation, and verification.
- `POST /api/runs` validates and stores an exercise result in SQLite.
- `GET /api/runs` returns recent validation runs.
- `GET /api/summary` returns catalog and completion counts.

The API accepts practice evidence only. Credentials, production logs, customer data, and destructive automation are intentionally out of scope.

Unknown GET API routes return HTTP 404 with a JSON error. There is no voltage API;
the catalog models support exercises and incident patterns, not voltage telemetry.

Static file GET/HEAD access is limited to public dashboard, catalog, documentation
and runbook files. See [the security boundaries](SECURITY.md) for the allowed content
and the remaining unauthenticated API limitations.
