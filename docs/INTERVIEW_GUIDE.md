# Interview guide

## One-minute explanation

This repository is a reproducible cloud-support practice environment. It pairs 30 guided exercises and 30 resolved incident patterns with API-backed run evidence, safe diagnostics, operational runbooks, an Azure infrastructure baseline, and a searchable dashboard.

## Decisions I can explain

- Diagnostics have time limits so a support command cannot hang indefinitely.
- Evidence output redacts IP addresses and receives a SHA-256 checksum.
- Runbooks use the same pattern: confirm impact, collect evidence, make the least risky change, verify recovery, document closure.
- Terraform demonstrates repeatable infrastructure and cost-aware defaults.
- The dashboard is static so it remains usable during control-plane or API outages.
- The optional local service persists validated runs in SQLite without making the review build dependent on cloud credentials.

## Trade-offs

The Azure plan is a safe reference baseline and is not automatically deployed by CI. A real organization would add remote state, policy-as-code, environment approvals, organization naming rules, and a secrets-management integration.

## Interview demonstration

1. Open the operations dashboard, search the 30-lab catalog, and choose an incident path.
2. Run a DNS or HTTP diagnostic against an approved test endpoint.
3. Show the timestamped, redacted evidence and checksum.
4. Walk through the matching runbook and recovery verification.
5. Record the verification result and explain how CI checks data depth, API behavior, shell syntax, and Terraform formatting.
