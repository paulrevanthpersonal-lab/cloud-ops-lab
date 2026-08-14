# Security and Safety Boundaries

- Diagnostic targets must be systems the operator is authorized to test.
- Output redacts IPv4 addresses and stores a content hash beside each evidence file.
- Terraform contains no credentials or tenant identifiers.
- Runbooks prefer reversible, least-privilege actions and explicit escalation.
- The lab does not automate destructive recovery actions.
- Real production evidence may contain sensitive identifiers and must follow the employer's retention policy.

