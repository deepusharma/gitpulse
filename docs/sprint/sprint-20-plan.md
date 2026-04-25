# Sprint 20 Execution Plan — VS Code Extension Completion

**Sprint Goal:** Complete the GitPulse VS Code extension — wire up real workspace repo detection, read configuration, call the GitPulse API, and render a polished standup summary directly in the sidebar.
**Milestone:** v1.3 — Delight
**Branch:** `feature/sprint-20-vscode`
**Status:** Approved — Ready to Execute

---

## Technical Audit & Constraints

| Risk | Mitigation |
|---|---|
| **Webview CSP** | Must include `connect-src ${apiUrl}` in the HTML meta tag to allow the webview to call the backend. |
| **Build System** | `vscode/` is a separate Node project. Requires `npm install` and `npm run compile` to generate `out/`. |
| **Sidebar Persistence** | VS Code may dispose of the webview when hidden. Use `retainContextWhenHidden: true` or handle state re-hydration. |
| **API Availability** | Extension must handle cases where the GitPulse API (localhost) is not running gracefully. |

---

## Step-by-Step Technical Plan

### S20.1 — Fix Compilation Blockers *(~15 min)*
**Files:** `vscode/tsconfig.json`, `vscode/media/icon.svg`

1. Create `vscode/tsconfig.json` with standard VS Code extension settings.
2. Create `vscode/media/icon.svg` (placeholder pulse waveform).
3. **Verification:** Run `npm run compile` in `vscode/` and ensure the `out/` directory is created without errors.

### S20.2 & S20.3 — Settings & Repo Detection *(~30 min)*
**File:** `vscode/src/SidebarProvider.ts`

1. Modify `resolveWebviewView` to:
   - Read `gitpulse.apiUrl` and `gitpulse.username` from `vscode.workspace.getConfiguration`.
   - Read folder names from `vscode.workspace.workspaceFolders`.
2. Pass these values into `_getHtmlForWebview`.
3. **Verification:** Pass these values to the HTML via a script global or `data-` attributes for initial load.

### S20.4 — Messaging Protocol *(~30 min)*
**Files:** `vscode/src/SidebarProvider.ts`, `vscode/media/main.js`

1. In `SidebarProvider`, add a `postMessage` call once the webview is resolved:
   ```typescript
   webviewView.webview.postMessage({ 
       type: 'init', 
       config: { apiUrl, username, repos } 
   });
   ```
2. In `main.js`, add a listener for the `init` message to update the local state.
3. **Verification:** `console.log` the received config in the webview console (Developer: Toggle Developer Tools).

### S20.5 — UI Logic & Fetching *(~60 min)*
**File:** `vscode/media/main.js`

1. Implement 3-state rendering:
   - **No Config:** Show "Please set your username in settings".
   - **Ready:** Show detected repos and a "Generate" button.
   - **Loading:** Show spinner.
   - **Result:** Show the formatted summary.
2. Update the `click` handler to use the `apiUrl` and `username` from state.
3. Use `display` from the API response to show the formatted summary.
4. **Verification:** Successfully generate and display a standup summary in the Sidebar.

### S20.6 — CSS Polish *(~45 min)*
**File:** `vscode/media/main.css`

1. Add styles for:
   - Repo tags/chips.
   - A modern loading spinner.
   - Markdown-lite formatting for the summary (bolding, lists).
   - Scrollbar styling to match VS Code.
2. **Verification:** UI feels "native" to VS Code and handles narrow sidebar widths elegantly.

### S20.7 — Command Palette & Wiring *(~20 min)*
**Files:** `vscode/package.json`, `vscode/src/extension.ts`

1. Register `gitpulse.generateStandup` in `package.json`.
2. Implement the command in `extension.ts` to focus the sidebar and trigger generation.
3. **Verification:** Run "GitPulse: Generate Standup" from the command palette.

### S20.8 — Smoke Tests *(~30 min)*
**File:** `vscode/src/test/suite/extension.test.ts`

1. Add a test that verifies the extension is activated.
2. Add a test that verifies commands are registered.
3. **Verification:** Run `npm test` in the `vscode/` directory.

---

## File Change Summary

| File | Change | Story |
|---|---|---|
| `vscode/tsconfig.json` | **NEW** — standard TS config | S20.1 |
| `vscode/media/icon.svg` | **NEW** — simple waveform icon | S20.1 |
| `vscode/package.json` | Add `gitpulse.generateStandup` command | S20.7 |
| `vscode/src/extension.ts` | Wire up the new generate command | S20.7 |
| `vscode/src/SidebarProvider.ts` | Read config/repos, handle CSP, and post `init` message | S20.2, S20.3, S20.4 |
| `vscode/media/main.js` | Full logic for state management and API fetching | S20.5 |
| `vscode/media/main.css` | Premium sidebar styling and markdown-lite rendering | S20.6 |
| `vscode/src/test/suite/extension.test.ts` | Basic activation and command tests | S20.8 |

---

## Definition of Done

- [ ] `npm run compile` succeeds in `vscode/`.
- [ ] Sidebar detects open workspace folders as repositories.
- [ ] Extension reads username/API URL from VS Code settings.
- [ ] "Generate Standup" successfully fetches and displays AI summary.
- [ ] Command Palette entry exists and works.
- [ ] UI is responsive and theme-aware.
- [ ] Smoke tests pass.
- [ ] All existing Python tests pass.
- [ ] PR squash-merged to master.
