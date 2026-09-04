# ORES Chat test-fleet governance

This repository owns the machine-readable contract used by repositories in the
private `ores-chat-test` organization. It prevents a test repository from being
counted as coverage merely because the repository exists.

Every suite declares `suite.json` and identifies its trust planes, both required
environments, test assertions, evidence level, and owner. The shared action validates
that declaration in hosted CI.

## Evidence model

- `contract-only` is a useful specification and CI guard, but it is not product coverage.
- `live` requires at least one assertion backed by execution against a deployed surface.
- Promotion to `live` also requires the suite implementation to exercise both the main
  organization and its isolated test fixture where that surface exists.
- Public, customer, administrator, and internal-service identities stay distinct.

Consumer workflow:

```yaml
permissions:
  contents: read

steps:
  - uses: actions/checkout@v4
  - uses: ores-chat-test/.github@<full-commit-sha>
```

Pin the full commit SHA. A moving branch is not a reproducible test policy.

## Local validation

```console
python3 scripts/validate_suite.py suite.json
python3 scripts/validate_suite.py --self-test
```

The validator intentionally has no third-party runtime dependencies. The JSON Schema
is available at `schemas/test-suite.schema.json` for editors and generators.
