# ORES Chat test-fleet policy

- Every repository must declare `suite.json` against the organization schema.
- `contract-only` means the suite validates its test plan but does not claim live coverage.
- `live` means CI executes against both the main-org and test-org target where the surface exists.
- Public, customer, administrator, and internal-service credentials are never interchangeable.
- Fixtures use synthetic tenant, principal, conversation, and context identifiers only.
- Logs and artifacts must not contain bearer tokens, provider credentials, prompts, answers, or database URLs.
- React, JSX, and TSX are outside the current ORES Chat scope.
