# Quick Start

Get your first standup summary in under 5 minutes.

## 1. Install

```bash
pip install gitpulse
```

## 2. Set your API key

You'll need a free Groq API key to power the AI summarization.

```bash
export GROQ_API_KEY=gsk_...          # get one free at console.groq.com
```

## 3. Configure

Run the interactive setup wizard to define your default repositories and lookback window.

```bash
gitpulse init
```

## 4. Generate

Generate your first standup! GitPulse will read your local git logs and output a formatted standup update.

```bash
gitpulse generate
```

You'll get a standup summary in your terminal and saved to your default output path (e.g. `output/summary.md`).
