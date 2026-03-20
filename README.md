# gitpulse

A CLI tool that reads your git repositories and generates a weekly standup summary using AI.

![Python](https://img.shields.io/badge/python-3.12+-blue)
[![CI](https://github.com/deepusharma/gitpulse/actions/workflows/ci.yml/badge.svg)](https://github.com/deepusharma/gitpulse/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-green)
![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20llama--3.3--70b-orange)
![uv](https://img.shields.io/badge/package%20manager-uv-purple)

Point it at your repos, run one command, get a structured summary of what you did, what's next, and any blockers — ready to paste into Slack or a standup doc.

Simple utility — no dashboards, no subscriptions, just a command that tells you what you did.

---

## Why

Standups should take 2 minutes. Remembering what you did across 3 repos over the past week shouldn't take 10. gitpulse reads your commit history and does the thinking for you.

---

## Output

```MD
### dotfiles
  - aaf5721 | 2026-03-20
    chore: add git config

### gitpulse
  - ad6169e | 2026-03-20
    feat: add summariser and utils modules

WHAT I DID
* Implemented summariser module for gitpulse
* Updated dotfiles with new configurations

DETAILS
* summariser.py added with format_commits, to_prompt_str, build_prompt, summarise
* dotfiles updated with vscode settings and git config

WHATS NEXT
* Add CLI entry point and argument parsing
* Write tests

BLOCKERS
* None identified
```

---

## Stack

- Python 3.12+
- [Groq API](https://console.groq.com) — LLM inference (free tier)
- [GitPython](https://gitpython.readthedocs.io) — git repo access
- [uv](https://docs.astral.sh/uv/) — package management

---

## Install

```bash
# Clone
git clone git@github.com:deepusharma/gitpulse.git
cd gitpulse

# Set up environment
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Add your Groq API key
cp .env.example .env
# edit .env and add GROQ_API_KEY
```

---

## Configure

Create `~/.gitpulse.toml` and list your repos:

```toml
[repos]
dotfiles = "/path/to/dotfiles"
gitpulse = "/path/to/gitpulse"
myproject = "/path/to/myproject"
```

---

## Usage

```bash
# Last 7 days (default)
python src/cli.py

# Last 14 days
python src/cli.py --days 14

# With debug logging
python src/cli.py --days 7 --debug
```

Output is printed to terminal and saved to `output/summary.md`.

---

## Project structure

```None
gitpulse/
├── src/
│   ├── repo_reader.py   # reads git repos, returns flat list of commits
│   ├── summarise.py     # formats commits, builds prompt, calls Groq
│   ├── utils.py         # loads .env, validates required keys
│   └── cli.py           # entry point, argument parsing
├── tests/
│   ├── test_repo_reader.py
│   └── test_summarise.py
├── output/              # generated summaries (gitignored)
├── .env.example
└── pyproject.toml
```

---

## Run tests

```bash
pytest -v
```

---

## Roadmap

- [ ] GitHub Actions CI
- [ ] `--output` flag for custom output path
- [ ] `--repo` flag to filter specific repos
- [ ] Slack integration
- [ ] Weekly scheduled run via cron

---

## License

MIT

---

> Built with assistance from Claude (Anthropic). Tool choices, structure, and code decisions are my own.
