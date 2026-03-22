# PRD — gitpulse Core CLI

**Version:** 1.0  
**Status:** Complete  
**Author:** Deepak Sharma  
**Date:** 2026-03-22  
**Milestone:** v0.1 — Core CLI

---

## 1. Problem Statement

Developers often struggle to recall exactly what they worked on during daily or weekly standups. Manually reading through git logs across multiple repositories is tedious and unformatted. `gitpulse` was built to automate reading local git commit histories and generating well-structured, AI-powered standup summaries using Groq.

---

## 2. Goals

- Provide a fast, functional CLI tool to generate markdown standup summaries.
- Read commit history automatically from local Git repositories.
- Use Groq API (llama-3.3-70b-versatile) for natural language reasoning.
- Support multi-repo configurations easily via `~/.gitpulse.toml`.

---

## 3. Non-Goals / Out of Scope (v0.1)

- Web interface / GUI.
- Fetching from remote GitHub instances.
- Authentication or OAuth flows.
- Persistent databases.

---

## 4. User Stories

### Core CLI 
> As a developer, I want a CLI tool to summarize my recent git commits so I can report my updates smoothly.

| ID   | Story                                                             | Priority |
| ---- | ----------------------------------------------------------------- | -------- |
| S0.1 | Read repositories from `~/.gitpulse.toml`                         | High     |
| S0.2 | Parse local git commits using GitPython                           | High     |
| S0.3 | Map commits to Groq AI logic prompts                              | High     |
| S0.4 | Expose CLI parameters (`--days`, `--repo`, `--debug`, `--output`) | High     |
| S0.5 | Output to a cleanly formatted Markdown file                       | High     |

**Acceptance Criteria:**
- CLI runs successfully via `gitpulse` or `python -m cli.cli`
- Supports `--days` (lookback period), `--repo` (filter specific repo), `--output` (file path), and `--debug` (logging level).
- AI Output is formatted rigidly into: `WHAT I DID`, `DETAILS`, `WHATS NEXT`, `BLOCKERS`.

---

## 5. Technical Decisions

| Decision         | Choice                                         | Reason                                      |
| ---------------- | ---------------------------------------------- | ------------------------------------------- |
| Language         | Python 3.12+                                   | Excellent scripting standard, rich library support |
| Package Manager  | `uv`                                           | Extremely fast Python packaging and resolution |
| Git Parsing      | `GitPython`                                    | Mature, reliable library for reading local `.git` folders |
| LLM Generator    | Groq (`llama-3.3-70b-versatile`)               | Fast, high reasoning quality, and free tier |
| Testing          | `pytest`                                       | Standard and powerful Python test runner    |

---

## 6. Architecture & Configuration

**Configuration:** `~/.gitpulse.toml`
```toml
[repos]
gitpulse = "/path/to/gitpulse"
dotfiles = "/path/to/dotfiles"
```

**Output Format:**
Summary strictly enforces four sections:
```markdown
WHAT I DID
- Bullet points of features/fixes completed
DETAILS
- Technical details, PR numbers, or important context
WHATS NEXT
- What you plan to work on next
BLOCKERS
- Any obstacles or dependencies
```

---

## 7. Success Criteria

- Unit tests utilizing `pytest`.
- Coverage for configuration loaders, local git iterators (`test_repo_reader.py`), summary formatters (`test_summarise.py`), and environment validation (`test_utils.py`).
