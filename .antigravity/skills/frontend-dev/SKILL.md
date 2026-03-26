# Frontend Developer — gitpulse

## Extends

Global frontend-dev skill — see ~/.antigravity/skills/frontend-dev/SKILL.md

## Project-specific additions

### gitpulse stack

- Next.js 14 App Router in web/
- NextAuth.js with GitHub OAuth
- react-markdown with prose prose-invert for summary rendering
- NEXT_PUBLIC_API_URL points to Railway backend

### gitpulse patterns

- useSession() to get GitHub username for form auto-fill
- GitHub-inspired dark theme — see sprint-04.md for color palette
- Form transitions to drawer after results appear

### gitpulse structure

- web/app/ — Next.js App Router
- web/components/ — Hero, SummaryForm, Results, Header, Footer
- web/lib/api.ts — API client

### Before starting

- Read AGENTS.md
- Read docs/api/api-contract.md
- Check current sprint in docs/sprint/
