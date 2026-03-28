# Sprint 05 — CLI Polish & Config Defaults

**Sprint goal:** Add --dry-run flag, config file defaults, and better error messages to the CLI.
**Milestone:** v0.4 — Config & Scheduling
**Duration:** Day 1 (Weekday — ~1 hour)
**Status:** Not Started

---

## Antigravity Prompts

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/prd/prd-v04.md (if exists, else use docs/prd/prd-v03.md)
- docs/sprint/sprint-05.md
- docs/architecture/overview.md
- core/repo_reader.py
- cli/cli.py

We are planning Sprint 05 — CLI Polish & Config Defaults.

Before writing any code:
1. Review stories #86, #87, #88, #89
2. Review current cli/cli.py and core/repo_reader.py structure
3. Confirm implementation approach for config defaults
4. Identify any risks or dependencies
5. Propose step-by-step execution plan
6. Save plan to docs/sprint/sprint-05-execution-plan.md

Do not write any code yet. Planning only.
Use @backend-dev skill.
```

### Execution Prompt (Fast Mode)
```
Read these files before starting:
- AGENTS.md
- docs/sprint/sprint-05.md
- docs/sprint/sprint-05-execution-plan.md

Execute stories #87, #86, #88, #89 in that order.
Branch: feature/sprint-05-cli-polish

Use @backend-dev skill.
Run pytest -v before committing — all tests must pass.
Commit: "feat: dry-run flag, config defaults, better errors (S#86-S#89)"
Push and create PR.
Closes #86
Closes #87
Closes #88
Closes #89
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| #86 | S5.1: add --dry-run flag to CLI | 🔵 This Sprint | High |
| #87 | S5.2: add [defaults] section to .gitpulse.toml | 🔵 This Sprint | High |
| #88 | S5.3: improve CLI error messages | 🔵 This Sprint | Medium |
| #89 | S5.4: write tests for config defaults and dry-run | 🔵 This Sprint | High |

---

## Story Details

### #86 — --dry-run flag

**Goal:** Show commit breakdown without calling Groq API.

**Implementation:**
- Add `--dry-run` flag to argparse in `cli/cli.py`
- If `--dry-run` set — skip `build_prompt`, `summarise` calls
- Print `display_str` only
- Log "dry-run mode — skipping LLM call"

**Done when:**
- [ ] `python -m cli.cli --dry-run` shows commits only
- [ ] No Groq API call made
- [ ] No output file written

---

### #87 — Config file defaults

**Goal:** Read defaults from `~/.gitpulse.toml` for CLI flags.

**New .gitpulse.toml structure:**
```toml
[repos]
gitpulse = "/path/to/gitpulse"

[defaults]
days = 7
output = "output/summary.md"
repo = "gitpulse"
```

**Priority:** CLI flag > config default > argparse default

**Done when:**
- [ ] [defaults] section read from config
- [ ] CLI flags override config defaults
- [ ] .gitpulse.toml.example updated

---

### #88 — Better error messages

**Scenarios to handle:**
- Repo not found → "Repo 'X' not found in ~/.gitpulse.toml. Add it under [repos]."
- GROQ_API_KEY missing → "GROQ_API_KEY not set. Add it to .env or export it."
- No commits found → "No commits found for the last N days. Try --days 30."
- Config file missing → "~/.gitpulse.toml not found. Run gitpulse init to set up."

**Done when:**
- [ ] Each error has clear message with suggested fix

---

### #89 — Tests

**Done when:**
- [ ] Test --dry-run skips LLM call
- [ ] Test config defaults loaded correctly
- [ ] Test CLI flag overrides config default
- [ ] All existing tests still pass

---

## Order of Work
```
#87 → #86 → #88 → #89
```

## Definition of Done
- [ ] --dry-run works end to end
- [ ] Config defaults load from ~/.gitpulse.toml
- [ ] Error messages are clear and actionable
- [ ] All tests pass
- [ ] PR merged
