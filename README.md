# gitpulse (v0.6.0)

A multi-client tool that reads git commit history and generates AI-powered standup summaries.

![Python](https://img.shields.io/badge/python-3.12+-blue)
[![CI](https://github.com/deepusharma/gitpulse/actions/workflows/ci.yml/badge.svg)](https://github.com/deepusharma/gitpulse/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-green)
![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20llama--3.3--70b-orange)
![uv](https://img.shields.io/badge/package%20manager-uv-purple)

GitPulse automates the retrieval of git commit history—from local folders or remote GitHub repos—and leverages LLMs to generate well-structured, professional standup updates.

## ✨ New in v0.6.0
- **Searchable Repository Selection**: Pick repos from a dynamic list instead of manual typing.
- **Server-side Caching**: Lightning-fast summary generation via in-memory caching.
- **History Filters**: Search your past summaries by keyword and date-range.
- **Data Export**: Download your summaries as `.md` files.

---

## 🚀 Live Demo

| Component | URL                                           |
| --------- | --------------------------------------------- |
| **Web UI**| <https://gitpulse-kappa.vercel.app>           |
| **API**   | <https://web-production-83e65.up.railway.app> |

---

## 🛠️ Installation (Local CLI)

```bash
# Clone
git clone git@github.com:deepusharma/gitpulse.git
cd gitpulse

# Set up environment
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Add your credentials
cp .env.example .env
# edit .env and add GROQ_API_KEY
```

---

## ⚙️ Configure CLI

Create `~/.gitpulse.toml` to store your local repository paths:

```toml
[repos]
gitpulse = "/Users/you/projects/gitpulse"
my-app = "/Users/you/projects/my-app"
```

---

## 📖 Usage

### CLI (Local Repos)
```bash
# Generate for last 7 days (default)
gitpulse

# For specific repo and duration
gitpulse --repo gitpulse --days 14 --output report.md
```

### Web UI (Remote Repos)
1. Log in with **GitHub OAuth**.
2. Search and select your repositories.
3. Hit **Generate Summary**.
4. Download the result or view it in your **History**.

---

## 📂 Project Structure

```none
gitpulse/
├── core/     # Shared library: repo reading & AI summarization
├── cli/      # Typer-based CLI tool
├── api/      # FastAPI backend
├── web/      # Next.js 14 frontend (App Router)
├── docs/     # PRDs, Architecture, and Release Notes
├── db/       # Database migrations and seeders
└── tests/    # Comprehensive test suites
```

---

## ✅ Run Tests

```bash
uv run pytest -v
```

---

## 🚧 Troubleshooting

### `GROQ_API_KEY` Missing
- **Error**: `ValueError: Missing required environment variable: GROQ_API_KEY`
- **Solution**: Ensure your `.env` file is in the root directory and contains a valid key from [console.groq.com](https://console.groq.com).

### GitHub API Rate Limits
- **Error**: `403 Forbidden` or `429 Too Many Requests`
- **Solution**: Add a `GITHUB_TOKEN` to your `.env` file to increase your rate limit from 60 to 5000 requests per hour.

### Config Not Found
- **Error**: `FileNotFoundError: ~/.gitpulse.toml not found`
- **Solution**: Run `gitpulse init` (planned) or manually create the file as described in the **Configure** section.

---

## 🗺️ Roadmap

- [x] GitHub OAuth Integration
- [x] Analytics Dashboard (v0.5)
- [x] Server-side Caching (v0.6)
- [ ] Email & Slack Delivery (v0.7)
- [ ] PyPI Distribution (v0.8)
- [ ] VS Code Extension (v1.0)

---

## 📄 License

MIT

---
> Built by the GitPulse Team.
