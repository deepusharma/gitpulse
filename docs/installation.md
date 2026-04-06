# Installation

You can install GitPulse via pip (recommended) or from source.

## Via pip (recommended)

The fastest way to get started is installing via pip:

```bash
pip install gitpulse
```

## From source

If you want to contribute to GitPulse, you can install it from source:

```bash
git clone https://github.com/deepusharma/gitpulse.git
cd gitpulse
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Required | Your Groq API key — get one at [console.groq.com](https://console.groq.com) |
| `GITHUB_TOKEN` | Optional | Raises GitHub API rate limit from 60 to 5,000 req/hr |
| `NEXT_PUBLIC_API_URL` | Web only | FastAPI backend URL for the Next.js frontend |

Copy `.env.example` to `.env` and fill in the required values.
