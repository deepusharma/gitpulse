# Changelog

All notable changes to the `gitpulse` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-04-02

### Added
- **Searchable Repository Selection**: New MultiSelect component for picking GitHub repositories dynamically.
- **Server-side Caching**: In-memory cache for GitHub API responses (Commits: 5m, Repos: 10m).
- **Advanced History Filtering**: Search by keyword and date-range (`start_date`, `end_date`) on the History page.
- **Data Export**: "Download as .md" button for generated standup summaries.
- **User Validation**: Live checking of GitHub usernames with avatar fetching.
- **Project Hardening**: Added edge-case tests for CLI and Core components.
- **Versioning Policy**: Atomic synchronization between Python and JS manifests.

### Changed
- Refactored `get_commits` to return a `(commits, errors)` tuple for granular error reporting.
- Updated `/summarise` and `/analytics` endpoints to handle partial repository failures gracefully.
- Pinning all dependencies in `package.json` and `pyproject.toml` for supply-chain security.

### Fixed
- Resolved 500 errors on the `/history` endpoint caused by malformed date strings (now returns 400).
- Fixed UI hydration and linting errors in the Next.js frontend.
- Corrected outdated milestone history in `AGENTS.md`.

## [0.5.0] - 2026-04-01

### Added
- **Analytics Dashboard**: Visual charts for commit activity and repository distribution using Recharts.
- **Database Persistence**: Saving all generated summaries to a PostgreSQL database.
- **History View**: Dedicated page to browse past generated summaries.

## [0.4.0] - 2026-03-31

### Added
- **CLI Configuration**: Support for `~/.gitpulse.toml` to store default repositories and settings.
- **Dry Run Mode**: `--dry-run` flag to preview commit collection without generating an AI summary.
- **UX Polish**: Added "Copy to Clipboard" and improved empty/error states in the web UI.

## [0.3.0] - 2026-03-29

### Added
- **GitHub OAuth**: Secure login using NextAuth.js and GitHub provider.
- **Layout Overhaul**: Professional Header/Footer and mobile-responsive grid.
- **Markdown Typography**: Enhanced rendering for summary results using `@tailwindcss/typography`.

## [0.2.0] - 2026-03-27

### Added
- **Web UI**: Next.js single-page application for non-local generation.
- **FastAPI Backend**: Asynchronous API layer to bridge Core and Web.
- **GitHub API Adapter**: Support for remote repository analysis via REST API.

## [0.1.0] - 2026-03-25

### Added
- **Core CLI**: Initial Python application for local git log analysis.
- **Groq AI Integration**: Automated summary generation using Llama 3.3.
- **Local Git Support**: Iterating over local `.git` folders.

---
*Created by [Antigravity](https://github.com/deepusharma/gitpulse)*
