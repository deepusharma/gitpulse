# Sprint 11 — Open Source Ready

**Sprint goal:** Make gitpulse ready to share publicly — comprehensive README, contributing guide, docs site, and automated releases.
**Milestone:** v0.8 — Open Source Ready
**Duration:** Day 7 (Weekend — ~3-4 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- All previous sprints complete
- App fully working end to end
- PyPI package published (Sprint 09)

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-11-brief.md
- README.md
- docs/architecture/overview.md
- docs/prd/prd-v01.md
- docs/prd/prd-v02.md
- docs/prd/prd-v03.md

We are planning Sprint 11 — Open Source Ready.

Before writing any code:
1. Review stories #108, #109, #110, #111
2. Review current README.md — what's missing
3. Review existing docs structure
4. Decide between MkDocs vs Mintlify for docs site
5. Plan GitHub issue and PR templates
6. Plan release workflow
7. Propose step-by-step execution plan
8. Save plan to docs/sprint/sprint-11-plan.md

Do not write any code yet. Planning only.
```

### Execution Prompt — Stream 1: README + Contributing (Fast Mode)
```
Read these files before starting:
- AGENTS.md
- docs/sprint/sprint-11-brief.md
- docs/sprint/sprint-11-plan.md
- README.md

Execute stories #108, #109 — README and contributing guide.
Branch: feature/sprint-11-open-source

For #108:
- Rewrite README.md to be comprehensive and compelling
- Add architecture diagram (mermaid)
- Add installation section (pip install gitpulse)
- Add quick start guide
- Add badges: CI, PyPI version, license, coverage
- Leave placeholder for demo GIF

For #109:
- Create CONTRIBUTING.md
- Create CODE_OF_CONDUCT.md
- Create .github/ISSUE_TEMPLATE/bug_report.md
- Create .github/ISSUE_TEMPLATE/feature_request.md
- Create .github/PULL_REQUEST_TEMPLATE.md

Commit: "docs: comprehensive README and contributing guide (S#108-S#109)"
Push — do NOT create PR yet.
```

### Execution Prompt — Stream 2: Docs Site + Releases (Fast Mode)
```
Stream 1 is complete. Execute stories #110, #111.
Still on branch: feature/sprint-11-open-source

For #110 — set up MkDocs documentation site:
- Create mkdocs.yml
- Create docs/ folder with:
  - index.md (getting started)
  - configuration.md
  - api-reference.md
  - contributing.md
- Add .github/workflows/docs.yml to deploy to GitHub Pages

For #111 — release workflow:
- Create .github/workflows/release.yml
- Triggers on version tag (v*)
- Auto-generates changelog from conventional commits
- Creates GitHub release
- Triggers PyPI publish

Run all checks before committing.
Commit: "docs: add MkDocs site and release workflow (S#110-S#111)"
Push and create PR.
Closes #108
Closes #109
Closes #110
Closes #111
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| #108 | S11.1: write comprehensive README with demo | 🔵 This Sprint | High |
| #109 | S11.2: add contributing guide and code of conduct | 🔵 This Sprint | High |
| #110 | S11.3: set up documentation site | 🔵 This Sprint | Medium |
| #111 | S11.4: add GitHub release workflow | 🔵 This Sprint | Medium |
| #220 | S11.5: implement CLI pre-flight auth & env validation | 🔵 This Sprint | Medium |

---

## Story Details

### #108 — Comprehensive README

**Sections to include:**
- Hero — what gitpulse does in one sentence
- Demo GIF (placeholder)
- Features list
- Installation — pip install and from source
- Quick start — 3 commands to first summary
- Configuration — .gitpulse.toml reference
- Web UI — screenshot
- API — brief endpoint reference
- Architecture diagram
- Contributing link
- License

**Badges:**
```markdown
![CI](https://github.com/deepusharma/gitpulse/workflows/CI/badge.svg)
![PyPI](https://img.shields.io/pypi/v/gitpulse)
![License](https://img.shields.io/badge/license-MIT-green)
```

**Done when:**
- [ ] README tells the full story
- [ ] Installation clear for new users
- [ ] Quick start works in under 5 minutes
- [ ] Badges accurate

---

### #109 — Contributing guide

**Files to create:**
- `CONTRIBUTING.md` — setup, development workflow, PR process
- `CODE_OF_CONDUCT.md` — standard contributor covenant
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

**Done when:**
- [ ] New contributor can set up in under 10 minutes
- [ ] PR template matches our workflow
- [ ] Issue templates reduce back-and-forth

---

### #110 — Documentation site

**Tool:** MkDocs with Material theme (free, GitHub Pages)

**Structure:**
```
docs/
├── index.md          # Getting started
├── installation.md   # Install options
├── configuration.md  # .gitpulse.toml reference
├── cli-reference.md  # All CLI flags
├── api-reference.md  # API endpoints
├── web-ui.md         # Web UI guide
└── contributing.md   # How to contribute
```

**Deploy:** GitHub Actions → GitHub Pages on every push to master

**Done when:**
- [ ] Docs site live at deepusharma.github.io/gitpulse
- [ ] All sections have content
- [ ] Linked from README

---

### #111 — Release workflow

**File:** `.github/workflows/release.yml`

**Trigger:** Push tag matching `v*` (e.g. v0.8.0)

**Steps:**
1. Run full test suite
2. Build package
3. Generate changelog from conventional commits
4. Create GitHub release with changelog
5. Publish to PyPI

**Versioning convention:** semantic versioning — MAJOR.MINOR.PATCH

**Done when:**
- [ ] Tag push creates GitHub release
- [ ] Changelog auto-generated
- [ ] PyPI publish triggered
- [ ] Version in pyproject.toml matches tag

---

### #220 — CLI Resilience: Pre-flight Auth

**Goal:** Implement a 'friendly-failure' mechanism for authentication errors in the CLI.

**Tasks:**
- [ ] Update `summarise.py` to catch `groq.AuthenticationError`.
- [ ] Update `cli.py` to catch the error and display a **Rich Instruction Panel**.
- [ ] Panel must include steps to run `gitpulse init` or `export GROQ_API_KEY`.

**Done when:**
- [ ] No Python stack trace on 401 errors.
- [ ] Professional Rich panel displayed with actionable resolution steps.

---

## Order of Work
```
#108 → #109 → #110 → #111
```

## Definition of Done
- [ ] README is compelling and complete
- [ ] Contributing guide enables new contributors
- [ ] Docs site live on GitHub Pages
- [ ] Release workflow creates GitHub releases
- [ ] PyPI publish automated on release
- [ ] PR merged
- [ ] v0.8.0 tag created and released
