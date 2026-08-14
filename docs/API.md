# API contract

- `GET /api/health` reports service readiness.
- `GET /api/labs` returns 30 guided exercises and supports text, category, and difficulty filters.
- `GET /api/incidents` returns 30 incident patterns with root cause, safe remediation, and verification.
- `POST /api/runs` validates and stores an exercise result in SQLite.
- `GET /api/runs` returns recent validation runs.
- `GET /api/summary` returns catalog and completion counts.

The API accepts practice evidence only. Credentials, production logs, customer data, and destructive automation are intentionally out of scope.
