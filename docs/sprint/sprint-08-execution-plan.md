# Sprint 08 — Email & Scheduling Execution Plan

This sprint focuses on configuring the GitPulse API to send generated summaries via email using Resend, upgrading the web app with an optional email switch, and automating weekly summary generation using a GitHub Actions cron job. 

## User Review Required
> [!WARNING]
> Environment Verification: The `RESEND_API_KEY` was **not found** in your local environment or `.env` file during the planning phase. 
> To test email functionality locally during execution, please ensure you add it to your `.env` file before proceeding.

## Proposed Changes

---

### Backend Components

#### [MODIFY] pyproject.toml
- Add `resend` to the application dependencies.

#### [NEW] core/email.py
- Create a new module exposing a `send_summary_email(to: str, summary: str, generated_at: str)` function.
- Integrate the official `resend` Python SDK, authenticating with `os.getenv("RESEND_API_KEY")`.
- Wrap the main library call in robust error-handling so network/API errors from Resend can be caught and logged safely.

#### [MODIFY] api/api.py
- Expand `SummariseRequest` Pydantic model to include an optional field: `email: str | None = None`.
- Import `send_summary_email` from the newly created `core.email` module.
- In the POST `/summarise` route, execute the email send conditionally if the `email` argument is provided. Wait to do this until *after* successfully generating the prompt.
- Crucially, wrap the `send_summary_email` call in a `try...except` block! If Resend fails, we must log the error but still return the actual `SummariseResponse` layout to the user.

---

### Frontend Components

#### [MODIFY] web/lib/api.ts
- Update the `SummariseRequest` interface to include the optional argument `email?: string`.

#### [MODIFY] web/components/SummaryForm.tsx
- Introduce two state variables: boolean `sendEmail` (default `false`) and a string `emailAddress`.
- Initialize `emailAddress` with `session?.user?.email` if available from the GitHub OAuth session.
- Add a new UI control (e.g., a simple HTML checkbox or Switch component from shadcn if available) inside the form to opt-in for email delivery.
- When toggled _on_, conditionally render the `emailAddress` input field.
- During submission validate that an email address is provided if the toggle is set. Include the `emailAddress` inside the `generateSummary` payload if enabled.

---

### GitHub Actions

#### [NEW] .github/workflows/weekly-summary.yml
- Set up a standard GitHub Actions YAML file that runs on standard triggers:
  - `workflow_dispatch` (for manual triggered testing)
  - `schedule` containing `cron: '30 3 * * 1'` (runs every Monday at 3:30 AM UTC / 9:00 AM IST)
- Create a generic runner step (e.g., `ubuntu-latest`).
- Add a step to perform a `curl -X POST` request hitting the `$RAILWAY_API_URL/summarise` target.
- Form the JSON request payload seamlessly using secrets injected by GitHub (`$GITHUB_USERNAME`, `$SUMMARY_REPOS`, `$SUMMARY_EMAIL`).

## Open Questions
- For the GitHub Actions workflow, what format should we expect the `$SUMMARY_REPOS` secret to take? Should we assume it will be stored precisely as a JSON array string e.g., `["gitpulse", "dotfiles"]` so we can easily interpolate it to a cURL payload? Or standard CSV `repo1,repo2` that we need to format in a bash setup step first? 
- For the UI layout of the "Send email" toggle: Are you comfortable if I use a simple HTML checkbox for the toggle, or must I use a shadcn `Switch` component (which would require installing via `npx` if it doesn't already exist)?

## Verification Plan

### Automated Tests
- Run `pytest -v` to ensure the Python core and api packages function properly after adding the optional email parameters.
- Run `npm run build` in the `web/` directory to ensure TS strict typing tests haven't broken.

### Manual Verification
1. Export a valid API key locally: `export RESEND_API_KEY=re_xxxx`.
2. Boot up both the FastAPI backend and NextJS frontend.
3. Access the browser UI, toggle "Send Email", ensure it pre-fills from session, submit the request.
4. Verify: (A) UI still generates and shows the summary card (B) Backend logs the success/attempt of Resend (C) Verify actual receipt in the designated email inbox.
5. (Action Post-Merge) Utilize the GitHub UI to manually trigger `workflow_dispatch` on the Actions tab to verify the cron script is capable of succeeding against actual Production URLs.
