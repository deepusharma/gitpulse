# Sprint Hygiene & PR Maintenance Plan (v0.7.0)

This document formalizes the automated Git Hygiene process for the GitPulse repository. It ensures that stale or superseded pull requests are identified and handled consistently during the release cycle.

## Policy: The Pre-Merge Hygiene Audit

Every AI agent working on GitPulse must perform a mandatory audit of open pull requests before every squash merge to `master`.

### Audit Requirements:
- **Reference Integrity**: Check for any open PRs that address the same issues as the current feature branch.
- **Atomic Closure**: Link related issues using `Closes #XXX` in PR descriptions.
- **Stale Backup**: Close any PRs that have been superseded by larger "total hardening" or "packaging" merges.

## Automation Workflow

### GitHub Action: `hygiene.yml`
A recurring workflow to identify and flag stale PRs.

```yaml
name: Git Hygiene Audit
on:
  schedule:
    - cron: '0 0 * * 0' # Weekly
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Audit Open PRs
        run: |
          gh pr list --state open --limit 50 --json number,title,createdAt,updatedAt
```

## Implementation Timeline

1.  **Phase 1**: Update `AGENTS.md` to establish the hygiene rule.
2.  **Phase 2**: Deploy `.github/workflows/hygiene.yml`.
3.  **Phase 3**: Perform baseline audit (Completed Apr 4, 2026).
