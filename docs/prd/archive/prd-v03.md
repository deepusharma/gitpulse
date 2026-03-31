# PRD — gitpulse v0.3 UI Polish

**Version:** 0.1  
**Status:** Draft  
**Author:** Deepak Sharma  
**Date:** 2026-03-22  
**Milestone:** v0.3 — UI Polish

---

## 1. Problem Statement

With v0.2, the core functionality of generating summaries via a web UI was completed entirely. However, the UI currently lacks polish (e.g. absent structural header/footer layout, primitive markdown rendering, minimal typography scaling) and users cannot authenticate their sessions to securely expand their GitHub rate limits or lay the groundwork for accessing private enterprise repositories.

## 2. Goals

- Implement robust user-level GitHub OAuth login via NextAuth.js.
- Formalize a persistent top-level application header and footer layout.
- Standardize and polish markdown rendering logic utilizing `@tailwindcss/typography`.
- Overhaul form elements and results column layout scaling for an immaculate user experience.

---

## 3. Non-Goals / Out of Scope (v0.3)

- Private GitHub repo support (Targeting v0.4+)
- Persisting summaries to a structured database
- Real-time webhooks or bidirectional syncing

---

## 4. User Stories

> As a persistent user, I want a polished, authenticated web experience allowing secure application usage and well-formatted visual summaries.

| ID   | Story                               | Priority |
| ---- | ----------------------------------- | -------- |
| #65  | GitHub OAuth login with NextAuth.js | High     |
| #66  | Header and footer                   | High     |
| #67  | Fix markdown rendering              | High     |
| #68  | Improve form and results layout     | Medium   |

---

## 5. Technical Decisions

- **Authentication**: `NextAuth.js` with structured GitHub Provider variables.
- **Styling**: `@tailwindcss/typography` plugin injection inside Tailwind config file to expose `prose` styling layers automatically for markdown strings.

---

## 6. Success Criteria

- [ ] NextAuth successfully intercepts and provisions GitHub OAuth sessions.
- [ ] Interface layout wraps seamlessly into a unified header and footer shell.
- [ ] Markdown strings perfectly cast into robust HTML components via `prose` classes.
- [ ] Results layouts are fully constrained, responsive, and visually cohesive.
