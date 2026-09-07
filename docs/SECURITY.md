# Security and Safety Boundaries

- Diagnostic targets must be systems the operator is authorized to test.
- Output redacts IPv4 addresses and stores a content hash beside each evidence file.
- Terraform contains no credentials or tenant identifiers.
- Runbooks prefer reversible, least-privilege actions and explicit escalation.
- The lab does not automate destructive recovery actions.
- Real production evidence may contain sensitive identifiers and must follow the employer's retention policy.

## Local HTTP boundary

The Python service is an unauthenticated, local practice application. Use synthetic
run evidence only and do not expose it directly to the internet. The run APIs are
still readable and writable by anyone who can reach the service; restricting static
files does not add authentication or protect evidence submitted through the API.

Static GET and HEAD requests serve only the landing page, README/license, public
catalog, dashboard HTML/CSS/JavaScript, documentation Markdown/PNG images, and
Markdown runbooks. Those directories are intentionally public. Do not put private
content in them. Repository internals, infrastructure files, local databases and
diagnostic evidence are outside this public-file boundary. Directory listings,
dot paths and symbolic links are rejected.

Run the regression suite with `python3 -m unittest discover -s tests -v`. HTTP tests
use a temporary directory, synthetic private fixtures, an isolated SQLite database
and a loopback server on an automatically selected port. They require permission
to open a local socket and never contact Azure or execute diagnostic commands.
