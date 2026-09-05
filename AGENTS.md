# ORES Chat test-fleet policy

- Every repository must declare `suite.json` against the organization schema.
- `contract-only` means the suite validates its test plan but does not claim live coverage.
- `live` means CI executes against both the main-org and test-org target where the surface exists.
- Public, customer, administrator, and internal-service credentials are never interchangeable.
- Fixtures use synthetic tenant, principal, conversation, and context identifiers only.
- Logs and artifacts must not contain bearer tokens, provider credentials, prompts, answers, or database URLs.
- React, JSX, and TSX are outside the current ORES Chat scope.

## Repository-local Git worktrees

- Create or use a Git worktree only when the human operator explicitly authorizes it for the current task. Concurrency or a dirty checkout is not permission by itself.
- Put every authorized worktree at `<repository-root>/tmp/worktrees/<name>`; from the repository root, use `./tmp/worktrees/<name>`. Never place worktrees beside repositories or organization directories.
- Keep `tmp`, `temp`, `tmp/worktrees`, and `temp/worktrees` ignored in the repository-root `.gitignore`. Do not commit files from those directories.
- Relocate or remove a worktree only when the operator explicitly requests it. Before removal, preserve and publish intended changes, verify its commit is represented on the target branch, and confirm there are no tracked, untracked, ignored-sensitive, or in-use files that must survive. Remove it with `git worktree remove <path>` without `--force`; never delete a worktree directory with `rm`.
