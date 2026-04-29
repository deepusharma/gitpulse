# Sprint 21 Brief: Release Hardening & Packaging

## 1. Goal
Move GitPulse from "feature-complete" to "production-ready" for a stable PyPI release (v1.5.0). This sprint focuses on automation, resilience, and final polish to ensure a flawless onboarding experience for end-users.

## 2. Context
GitPulse has accumulated a massive feature set across CLI, Web UI, MCP, and VS Code. With the `gitpulse` package now isolated in its own namespace and the `core/` legacy directory removed, we must automate the PyPI publishing workflow and ensure the CLI degrades gracefully when environment variables are missing.

## 3. Scope & Requirements

### Epic 1: PyPI Publish Workflow (#103)
- Create a `.github/workflows/publish.yml` GitHub Action.
- Trigger on pushing semver tags (e.g., `v1.5.0`).
- Build the package using `uv build`.
- Publish to PyPI using Trusted Publishing (OIDC).
- *Constraint*: Must fail gracefully if tests fail before publishing.

### Epic 2: CLI Resilience & Auth Validation (#220)
- Update `gitpulse/cli/cli.py`.
- Add pre-flight checks for `GROQ_API_KEY` before attempting to run `get_activity`.
- Validate `~/.gitpulse.toml` schema integrity during initialization.
- Provide clear, actionable Rich panels for common setup failures (e.g., missing API keys, invalid paths).

### Epic 3: Final Integration Polish
- Ensure the `gitpulse init` command creates the config file correctly.
- Verify that `gitpulse generate` runs without warnings when no `GITHUB_TOKEN` is present (local mode).

## 4. Acceptance Criteria
- [ ] A GitHub release with a `v*` tag automatically triggers a PyPI publish.
- [ ] Running `gitpulse generate` without a `GROQ_API_KEY` immediately shows a helpful error message and exits cleanly (no traceback).
- [ ] `gitpulse init` successfully creates a valid `~/.gitpulse.toml` file.

## 5. Next Steps
Agent: Read this brief and immediately generate `sprint-21-plan.md` using the standard technical planning format. Wait for user approval before execution.
