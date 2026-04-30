# Sprint 22 Brief: Advanced Delivery & Integrations

## 1. Goal
Expand GitPulse's delivery mechanisms beyond just local markdown files and simple Slack webhooks. This sprint will implement Email delivery via Resend, GitHub Gist publishing, and LLM Tone/Language customization.

## 2. Context
While the web UI and CLI generate excellent summaries, users want more automated ways to share them with their teams. Currently, only basic Slack delivery is implemented in `api/routers/deliver.py`. We need to flesh out the remaining features originally planned under Epic #115. Additionally, users have requested the ability to change the output language and tone (e.g., formal, casual, pirate) of the AI summaries.

## 3. Scope & Requirements

### Epic 1: Email & Gist Delivery
- **Email (Resend):** Integrate the Resend SDK in `api/routers/deliver.py`. Expose a `POST /deliver/email` endpoint that takes an email address and summary text, sending a nicely formatted HTML email.
- **GitHub Gist:** Expose a `POST /deliver/gist` endpoint. Using the user's GitHub OAuth token (or a CLI provided token), create a secret GitHub Gist containing the markdown summary and return the URL.

### Epic 2: Tone & Language Customization
- **Backend Updates:** Modify `SummariseRequest` in `api/models.py` to accept `tone` and `language` parameters. Update the prompt builder in `gitpulse/core/summarise.py` to instruct the LLM accordingly.
- **Web UI:** Add dropdowns for Tone (Professional, Casual, Bullet-points, Pirate) and Language (English, Spanish, French, etc.) on the main generation form.
- **CLI:** Add `--tone` and `--language` flags to `gitpulse generate`.

## 4. Acceptance Criteria
- [ ] Users can enter an email address in the Web UI to receive their summary via email.
- [ ] Users can click a "Publish to Gist" button to instantly create a GitHub Gist.
- [ ] The CLI and Web UI successfully generate summaries in different languages and tones based on user selection.

## 5. Next Steps
Agent: Read this brief and immediately generate `sprint-22-plan.md` using the standard technical planning format. Wait for user approval before execution.
