# Interview guide

## One-minute explanation

This repository is a reproducible cloud-support practice environment. It pairs safe diagnostic commands with evidence capture, operational runbooks, an Azure infrastructure baseline, and a dashboard that makes common incident paths easy to navigate.

## Decisions I can explain

- Diagnostics have time limits so a support command cannot hang indefinitely.
- Evidence output redacts IP addresses and receives a SHA-256 checksum.
- Runbooks use the same pattern: confirm impact, collect evidence, make the least risky change, verify recovery, document closure.
- Terraform demonstrates repeatable infrastructure and cost-aware defaults.
- The dashboard is static so it remains usable during control-plane or API outages.

## Trade-offs

The Azure plan is a safe reference baseline and is not automatically deployed by CI. A real organization would add remote state, policy-as-code, environment approvals, organization naming rules, and a secrets-management integration.

## Interview demonstration

1. Open the operations dashboard and choose an incident path.
2. Run a DNS or HTTP diagnostic against an approved test endpoint.
3. Show the timestamped, redacted evidence and checksum.
4. Walk through the matching runbook and recovery verification.
5. Explain how the CI checks shell syntax and Terraform formatting.
