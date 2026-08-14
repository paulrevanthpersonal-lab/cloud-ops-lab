# VM Access Failure

## Scope
SSH or RDP access to an Azure VM fails.

## Evidence
Capture timestamp, caller identity, target hint, source network, error text, Azure activity log, NSG effective rules, VM power state, and boot diagnostics.

## Safe workflow
1. Confirm blast radius and recent changes.
2. Validate the user or managed identity and RBAC scope.
3. Check VM state and guest-agent health.
4. Review effective NSG rules and route path.
5. Use Azure Bastion or serial console only through approved access.
6. Test the smallest reversible correction.

## Escalate when
The issue affects multiple subscriptions, indicates credential compromise, or requires emergency network-policy changes.

## Verify recovery
Confirm an authorized user can connect, audit logs record the access, and the temporary change is removed.

