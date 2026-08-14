# DNS Resolution Drift

## Evidence
Collect resolver configuration, record type, answers from two approved resolvers, TTL values, recent DNS changes, and affected subnets.

## Workflow
1. Reproduce from affected and healthy networks.
2. Compare authoritative and recursive answers.
3. Check private DNS links and conditional forwarders.
4. Review TTL and caching behavior.
5. Correct the record or link with a documented rollback.
6. Flush only the necessary cache and verify resolution plus application recovery.

