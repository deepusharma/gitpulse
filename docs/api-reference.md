# API Reference

The GitPulse API exposes the core summarization functionality over HTTP.

## Base URL

| Environment | URL                                                   |
| ----------- | ----------------------------------------------------- |
| Local       | `http://localhost:8000`                               |
| Production  | `https://web-production-83e65.up.railway.app`         |

---

## `POST /summarise`

Generate a standup summary from a GitHub user's public repos.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "deepusharma",
  "repos": ["gitpulse"],
  "days": 7
}
```

| Field      | Type     | Required | Default | Description                        |
| ---------- | -------- | -------- | ------- | ---------------------------------- |
| `username` | string   | Yes      | —       | GitHub username                    |
| `repos`    | string[] | Yes      | —       | List of repo names (not full URLs) |
| `days`     | integer  | No       | 7       | Number of days to look back        |

**Response — 200 OK:**
```json
{
  "display": "### gitpulse\n  - a1b2c3d | 2026-03-21\n    feat: add summariser\n",
  "summary": "# WHAT I DID\n* Implemented summariser module\n\n# DETAILS\n* ...\n\n# WHATS NEXT\n* ...\n\n# BLOCKERS\n* None identified",
  "repos": ["gitpulse"],
  "days": 7,
  "generated_at": "2026-03-21T10:00:00Z"
}
```

---

## `GET /health`

Health check endpoint.

**Response — 200 OK:**
```json
{
  "status": "ok",
  "version": "0.7.0"
}
```

---

## `GET /history`

Retrieve past generated summaries (with optional filters).

| Query Param | Type | Description |
|---|---|---|
| `limit` | integer | Max records to return |
| `skip` | integer | Pagination offset |

---

## `GET /analytics`

Retrieve statistical commit data for the analytics dashboard.
