# Sprint 20 — VS Code Extension

**Sprint goal:** Complete the GitPulse VS Code extension — wire up real workspace repo detection, read configuration, call the GitPulse API, and render a polished standup summary directly in the sidebar.
**Milestone:** v1.3 — Delight (completing S18.3)
**Duration:** ~4–5 hours
**Status:** Not Started

---

## Context / Pre-Sprint Audit

Sprint 18 scaffolded the extension skeleton. The following is already done:

| File | State |
|---|---|
| `vscode/package.json` | ✅ Manifest complete — sidebar container, `gitpulse.apiUrl`, `gitpulse.username` config |
| `vscode/src/extension.ts` | ✅ Activates sidebar, registers `gitpulse.refresh` command |
| `vscode/src/SidebarProvider.ts` | ✅ Webview wired up, HTML rendered, `reset.css` / `vscode.css` / `main.css` loaded |
| `vscode/media/main.css` | ✅ Basic VS Code token-aligned styling |
| `vscode/media/main.js` | ⚠️ Hardcoded `username: 'default'`, `repos: []` — not functional |
| `vscode/media/icon.svg` | ❌ Missing — will cause activation warning |
| `tsconfig.json` | ❌ Missing — compilation will fail |
| `vscode/test/` | ❌ Empty |

**What's missing for a working extension:**
1. `tsconfig.json` — required to compile TypeScript
2. `icon.svg` — required by the manifest
3. Real username + `apiUrl` read from VS Code settings via `SidebarProvider`
4. Workspace repo detection — read folder names from `vscode.workspace.workspaceFolders`
5. `SidebarProvider` → webview messaging: pass config + repos to `main.js`
6. `main.js` — use received config, show repo list, days picker, generate button, results panel
7. Polished CSS — sections, markdown-like summary rendering, status indicators
8. A `gitpulse.generateStandup` command registered in `package.json` (command palette)
9. Tests (basic extension activation smoke test)

---

## Pre-Sprint Requirements

- Sprint 18 & 19 merged to master ✅
- `node` / `npm` available (for `npm run compile`) ✅
- VS Code Extension Development Host can run locally

---

## Sprint Stories

| Story | Description | Priority |
|---|---|---|
| S20.1 | Fix compilation blockers (`tsconfig.json`, `icon.svg`) | Critical |
| S20.2 | Read `gitpulse.apiUrl` + `gitpulse.username` from VS Code settings in `SidebarProvider` | High |
| S20.3 | Detect workspace repos from `vscode.workspace.workspaceFolders` | High |
| S20.4 | Pass config + repos to the webview via `postMessage` | High |
| S20.5 | Build functional `main.js` — repo list, days picker, generate + display result | High |
| S20.6 | Polish `main.css` — section layout, summary rendering, loading/error states | Medium |
| S20.7 | Register `gitpulse.generateStandup` command in `package.json` and wire it | Medium |
| S20.8 | Add basic extension activation smoke test | Medium |

---

## Story Details

### S20.1 — Fix Compilation Blockers

**`tsconfig.json`** must be added at `vscode/tsconfig.json` with standard VS Code extension targets:
```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2020",
    "outDir": "out",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
```

**`icon.svg`** should be a simple GitPulse logo mark (pulse/waveform icon) placed at `vscode/media/icon.svg`.

---

### S20.2 — Read VS Code Settings

In `SidebarProvider.resolveWebviewView`, read config and send to webview:
```typescript
const config = vscode.workspace.getConfiguration('gitpulse');
const apiUrl = config.get<string>('apiUrl', 'http://localhost:8000');
const username = config.get<string>('username', '');
```

Send to webview via `postMessage` after view loads.

---

### S20.3 — Workspace Repo Detection

Read open workspace folders to pre-populate the repos field:
```typescript
const folders = vscode.workspace.workspaceFolders ?? [];
const repos = folders.map(f => f.name);
```

These are passed to the webview alongside config so the user sees them pre-filled.

---

### S20.4 — Webview Messaging Protocol

Define a clean bidirectional message contract:

**Extension → Webview:**
```typescript
{ type: 'init', apiUrl: string, username: string, repos: string[] }
{ type: 'refresh' }
```

**Webview → Extension:**
```typescript
{ type: 'onError', value: string }
{ type: 'onInfo', value: string }
```

---

### S20.5 — Functional `main.js`

The webview UI should have three states:

1. **Config state** (no username set): show a prompt to set username in VS Code settings
2. **Ready state**: show username, pre-filled repos (editable), days selector (1/7/14/30), and a "Generate Standup" button
3. **Result state**: show the generated summary with markdown-style rendering + a "Regenerate" button

Key logic:
- On `init` message, populate fields from received data
- On button click, `fetch(apiUrl + '/summarise', { method: 'POST', body: JSON.stringify({ username, repos, days }) })`
- On success, render `data.display` (the markdown formatted summary) in the result panel
- On error, show a styled error with the failure reason

---

### S20.6 — Polished CSS

Extend `main.css` with:
- Section headers for repos list, days selector, result
- Monospace code-like styling for the summary block
- Animated spinner for loading state
- Clear visual separation between config/result areas
- Responsive handling for narrow sidebar widths

---

### S20.7 — Command Palette Integration

Add to `package.json` `contributes.commands`:
```json
{
  "command": "gitpulse.generateStandup",
  "title": "GitPulse: Generate Standup"
}
```

Wire in `extension.ts` alongside the existing `gitpulse.refresh` command.

---

### S20.8 — Smoke Test

Add `vscode/test/extension.test.ts`:
- Test that extension activates without throwing
- Test that `gitpulse.refresh` command is registered
- Test that `gitpulse.generateStandup` command is registered

---

## New Files

```
vscode/
├── tsconfig.json          ← NEW (S20.1)
├── media/
│   └── icon.svg           ← NEW (S20.1)
├── src/
│   ├── extension.ts       ← UPDATE (S20.7)
│   └── SidebarProvider.ts ← UPDATE (S20.2, S20.3, S20.4)
├── media/
│   ├── main.js            ← REWRITE (S20.5)
│   └── main.css           ← UPDATE (S20.6)
└── test/
    └── extension.test.ts  ← NEW (S20.8)
```

---

## Order of Work

```
S20.1 (tsconfig + icon) → S20.2 (read settings) → S20.3 (detect repos)
→ S20.4 (messaging protocol) → S20.5 (main.js rewrite) → S20.6 (CSS polish)
→ S20.7 (command palette) → S20.8 (smoke test)
```

Verify with `npm run compile` (in `vscode/`) after S20.1. Test in Extension Development Host after S20.5.

---

## Definition of Done

- [ ] `npm run compile` succeeds with zero errors in `vscode/`
- [ ] Extension activates in VS Code Extension Development Host without errors
- [ ] Sidebar shows username + workspace repos pre-filled from VS Code settings
- [ ] "Generate Standup" button calls the GitPulse API and renders the result
- [ ] Loading and error states display correctly
- [ ] `gitpulse.generateStandup` is accessible from the Command Palette
- [ ] `icon.svg` exists and no manifest warnings on activation
- [ ] Basic smoke tests pass (`npm test` in `vscode/`)
- [ ] All Python tests still pass (`uv run pytest -v`)
- [ ] PR squash-merged to master

---

## Out of Scope

- Publishing to VS Code Marketplace (future sprint)
- Private repo support in the extension
- Offline/local git mode in the extension (uses API only for now)
- Extension settings UI (user edits `settings.json` directly)

---

## AI Planning Prompt

```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-20-brief.md
- vscode/src/SidebarProvider.ts
- vscode/src/extension.ts
- vscode/media/main.js
- vscode/media/main.css
- vscode/package.json

We are planning Sprint 20 — VS Code Extension completion.

Before writing any code:
1. Review the pre-sprint audit and all 8 stories (S20.1–S20.8).
2. Identify any additional blockers or risks not listed in the brief.
3. Propose a step-by-step technical execution plan ordered by S20.1 → S20.8.
4. For each step specify: files changed, key code snippets (no full implementations yet), and a test/verify step.
5. Flag any VS Code API constraints (e.g., webview CSP, fetch availability in webviews).
6. Save plan to `docs/sprint/sprint-20-plan.md`.

Do not write code yet. Planning only.
```
