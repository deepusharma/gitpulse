# API Contract — gitpulse

**Version:** 0.1  
**Status:** Draft  
**Author:** Deepak Sharma  
**Date:** 2026-03-21  
**Milestone:** v0.2 — Web UI

---

## Base URL

| Environment | URL                                                   |
| ----------- | ----------------------------------------------------- |
| Local       | `http://localhost:8000`                               |
| Production  | `https://gitpulse-api.railway.app` (TBD after deploy) |

---

## Authentication

v0.2 — no authentication required. Public repos only.

---

## Endpoints

### `GET /health`

Health check endpoint.

**Request:** No body required.

**Response — 200 OK:**

```json
{
  "status": "ok",
  "version": "0.2.0"
}
```

---

### `POST /summarise`

Generate a standup summary from a GitHub user's public repos.

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "username": "deepusharma",
  "repos": ["gitpulse", "dotfiles"],
  "days": 7
}
```

**Request Fields:**

| Field      | Type     | Required | Default | Description                        |
| ---------- | -------- | -------- | ------- | ---------------------------------- |
| `username` | string   | Yes      | —       | GitHub username                    |
| `repos`    | string[] | Yes      | —       | List of repo names (not full URLs) |
| `days`     | integer  | No       | 7       | Number of days to look back        |

**Validation Rules:**

- `username` — non-empty string
- `repos` — non-empty list, each item a non-empty string
- `days` — integer between 1 and 90

---

**Response — 200 OK:**

```json
{
  "display": "### gitpulse\n  - a1b2c3d | 2026-03-21\n    feat: add summariser\n",
  "summary": "# WHAT I DID\n* Implemented summariser module\n\n# DETAILS\n* ...\n\n# WHATS NEXT\n* ...\n\n# BLOCKERS\n* None identified",
  "repos": ["gitpulse", "dotfiles"],
  "days": 7,
  "generated_at": "2026-03-21T10:00:00Z"
}
```

**Response Fields:**

| Field          | Type     | Description                              |
| -------------- | -------- | ---------------------------------------- |
| `display`      | string   | Formatted commit breakdown per repo      |
| `summary`      | string   | AI-generated standup summary in markdown |
| `repos`        | string[] | Repos that were queried                  |
| `days`         | integer  | Lookback period used                     |
| `generated_at` | string   | ISO 8601 timestamp of generation         |

---

**Response — 422 Unprocessable Entity:**

Returned when request body fails validation.

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

**Response — 404 Not Found:**

Returned when a repo does not exist or is private.

```json
{
  "error": "Repo 'deepusharma/nonexistent' not found or is private",
  "code": 404
}
```

---

**Response — 429 Too Many Requests:**

Returned when GitHub API rate limit is exceeded.

```json
{
  "error": "GitHub API rate limit exceeded. Try again in 60 minutes.",
  "code": 429
}
```

---

**Response — 500 Internal Server Error:**

Returned when Groq API fails or unexpected error occurs.

```json
{
  "error": "Failed to generate summary. Please try again.",
  "code": 500
}
```

---

## Error Handling Summary

| Status Code | Cause                     | User Message                  |
| ----------- | ------------------------- | ----------------------------- |
| 422         | Invalid request body      | Field-level validation errors |
| 404         | Repo not found or private | Repo not found or is private  |
| 429         | GitHub rate limit         | Try again in 60 minutes       |
| 500         | Groq API failure          | Failed to generate summary    |

---

## Example — curl

```bash
# Health check
curl http://localhost:8000/health

# Generate summary
curl -X POST http://localhost:8000/summarise \
  -H "Content-Type: application/json" \
  -d '{
    "username": "deepusharma",
    "repos": ["gitpulse", "dotfiles"],
    "days": 7
  }'
```

---

## Example — JavaScript fetch

```javascript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/summarise`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "deepusharma",
    repos: ["gitpulse", "dotfiles"],
    days: 7,
  }),
});

const data = await response.json();
console.log(data.summary);
```

---

## Notes

- `display` field uses `\n` for newlines — render as preformatted text or split on newlines
- `summary` field is markdown — use a markdown renderer in the UI
- `repos` in request are short names only — not full URLs (`gitpulse` not `github.com/deepusharma/gitpulse`)
- GitHub API rate limit is 60 requests/hour unauthenticated. Adding `GITHUB_TOKEN` raises this to 5000/hour.
