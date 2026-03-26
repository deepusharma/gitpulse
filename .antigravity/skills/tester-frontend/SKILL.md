# Frontend Test Engineer — gitpulse

## Extends

Global tester-frontend skill — see ~/.antigravity/skills/tester-frontend/SKILL.md

## Project-specific additions

### gitpulse test location

- web/tests/ — all frontend tests

### gitpulse mocking patterns

- Mock POST /summarise with MSW
- Mock NextAuth session with SessionProvider wrapper
- Test form auto-fill when session has username

### gitpulse API mock shape

```typescript
{
  display: "### gitpulse\n  - a1b2c3 ...",
  summary: "## WHAT I DID\n...",
  repos: ["gitpulse"],
  days: 7,
  generated_at: "2026-03-22T10:00:00Z"
}
```

### Before starting

- Read docs/api/api-contract.md
- Check web/components/ structure
