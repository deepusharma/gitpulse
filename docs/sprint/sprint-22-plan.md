# Sprint 22 Plan: Advanced Delivery & Integrations

## Overview
This plan details the technical implementation for expanding GitPulse's delivery options (Email via Resend, GitHub Gists) and adding LLM output customization (Tone & Language).

## Phase 1: Tone & Language Customization

### Step 1.1: Core Library Updates
**File:** `gitpulse/core/summarise.py`
- Modify `build_prompt(formatted_activity: str, tone: str = "professional", language: str = "English") -> str`.
- Inject specific instructions into the system prompt directing the LLM to adopt the requested tone and output in the specified language.
- Update `summarise` to pass these parameters down.

### Step 1.2: CLI Integration
**File:** `gitpulse/cli/cli.py`
- Add `--tone` (default: `professional`) and `--language` (default: `English`) options to the `generate` Typer command.
- Update the TOML config schema (`~/.gitpulse.toml`) to accept default tone and language preferences under the `[defaults]` section.

### Step 1.3: API & Web UI Updates
**Files:** `api/models.py`, `api/routers/summarise.py`, `web/src/app/page.tsx`
- Update `SummariseRequest` Pydantic model to include optional `tone` and `language` fields.
- Update the frontend form to include select dropdowns for Tone and Language, passing them in the POST request to `/summarise`.

## Phase 2: Advanced Delivery Options

### Step 2.1: Email Delivery Integration
**Files:** `api/models.py`, `api/routers/deliver.py`
- Create an `EmailDeliverRequest` model (to, summary).
- Add `resend` to `pyproject.toml` dependencies.
- Implement `POST /deliver/email` endpoint using the Resend Python SDK. Requires `RESEND_API_KEY`.
- Format the markdown summary into simple HTML before sending.

### Step 2.2: GitHub Gist Integration
**Files:** `api/models.py`, `api/routers/deliver.py`
- Create a `GistDeliverRequest` model (token, summary, is_public).
- Implement `POST /deliver/gist` endpoint utilizing `httpx` to call the GitHub API (`POST /gists`).
- Parse the response and return the generated `html_url`.

## Phase 3: Web UI Integration for Delivery

### Step 3.1: Frontend Delivery Modal
**File:** `web/src/components/delivery-modal.tsx` (New Component)
- Create a reusable modal/dialog that opens upon clicking "Share".
- Implement tabs for "Slack", "Email", and "GitHub Gist".
- **Email Tab:** Input for email address -> triggers `/deliver/email`.
- **Gist Tab:** Toggle for Private/Public -> triggers `/deliver/gist` using the current NextAuth GitHub session token.

### Step 3.2: Success Feedback
- Use `toast` notifications to inform the user of successful delivery or errors.

## Phase 4: Validation & Docs
- **Testing:** Write `pytest` mocks for Resend and GitHub Gist endpoints.
- **Documentation:** Add `.env` requirements (`RESEND_API_KEY`) to `README.md` and document the new `/deliver` endpoints in `api-contract.md`.
