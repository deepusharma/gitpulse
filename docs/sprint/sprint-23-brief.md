# Sprint 23 Brief: Release Hardening & v1.5 Launch

## Objective
Finalize the v1.5 "Release Hardening" milestone. This sprint focuses on ensuring the codebase is production-ready, CI/CD pipelines are fully operational, and the package can be flawlessly published to PyPI. We will address any lingering technical debt, tighten up type-checking/linting, and verify our GitHub Actions.

## Key Deliverables
1. **CI/CD Refinement**: Review and finalize `.github/workflows/publish.yml` and `test.yml` to ensure tests run reliably and releases trigger correctly on version tags.
2. **Code Health Sweep**: Run `ruff` and `pyright`/`mypy` (if applicable) across the Python backend, and `npm run lint` / `npm run build` across the Next.js frontend to squash any warnings.
3. **TestPyPI Validation**: Configure or verify a dry-run/TestPyPI deployment to guarantee the final PyPI release will succeed.
4. **Documentation Sync**: Do a final review of `README.md` and docs to ensure setup instructions, environment variables (like `RESEND_API_KEY`), and screenshots are up-to-date.

## Constraints & Rules
- Do not introduce new features during this sprint. The sole focus is stabilization and release readiness.
- Ensure all CI workflow changes are syntax-checked.
- Strictly adhere to the project's semantic versioning.

---

## AI Planning Prompt
```text
@antigravity Review this sprint brief. Analyze the current state of `.github/workflows/` and the linting rules. Create `docs/sprint/sprint-23-plan.md` with a step-by-step checklist to execute this release hardening sprint.
```
