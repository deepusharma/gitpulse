# Configuration

GitPulse is configured via a TOML file located at `~/.gitpulse.toml`.

`gitpulse init` creates this file interactively. You can also edit it manually.

## Example Config

```toml
# ~/.gitpulse.toml
github_username = "deepusharma"

[defaults]
days   = 7
output = "output/summary.md"

[repos]
gitpulse = "/Users/you/projects/gitpulse"
my-app   = "/Users/you/projects/my-app"
```

## Reference

| Key | Section | Type | Default | Description |
|---|---|---|---|---|
| `github_username` | root | string | — | Your GitHub username |
| `days` | `[defaults]` | int | `7` | Default lookback window in days |
| `output` | `[defaults]` | string | `"output/summary.md"` | Output file path |
| `<name>` | `[repos]` | string | — | Absolute path to a local git repository |
