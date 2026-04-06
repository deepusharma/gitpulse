# CLI Reference

The GitPulse CLI (`gitpulse`) provides two primary commands.

## `gitpulse init`

Interactively sets up your `~/.gitpulse.toml` configuration file.

```bash
gitpulse init
```

## `gitpulse generate`

Generates a standup summary based on your git history.

### Basic Usage

Generate for all configured repos using default lookback (usually 7 days):
```bash
gitpulse generate
```

### Options

| Flag | Short | Description |
|---|---|---|
| `--days` | `-d` | Number of days to look back for commits. Overrides config default. |
| `--repo` | `-r` | Filter by specific repo name from your `[repos]` config. |
| `--output` | `-o` | Custom output file path. |
| `--dry-run` | | Show gathered commits only; skips the LLM call entirely. |
| `--debug` | | Enable verbose debug logging output. |

### Examples

```bash
# Look back further
gitpulse generate --days 14

# Specific repo only
gitpulse generate --repo my-app

# Custom file output
gitpulse generate --output notes/daily.md

# Preview data without spending LLM tokens
gitpulse generate --dry-run
```
