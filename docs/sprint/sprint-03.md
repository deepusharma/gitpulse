# Sprint 03 — Next.js Frontend

**Sprint goal:** Build and deploy a clean, GitHub-inspired web UI for gitpulse.  
**Milestone:** v0.2 — Web UI  
**Duration:** 2026-03-21  
**Status:** ✅ Done

---

## Sprint Stories

| Issue | Story                                             | Status  | Session |
| ----- | ------------------------------------------------- | ------- | ------- |
| #36   | Scaffold Next.js app with TypeScript and Tailwind | ✅ Done | Today   |
| #37   | Build input form                                  | ✅ Done | Today   |
| #38   | Connect form to FastAPI backend                   | ✅ Done | Today   |
| #39   | Display commit breakdown and summary              | ✅ Done | Today   |
| #40   | Add loading state                                 | ✅ Done | Today   |
| #41   | Add error handling                                | ✅ Done | Today   |
| #42   | Deploy frontend to Vercel                         | ✅ Done | Today   |

---

## Design Spec

### Overall feel

- GitHub-inspired — dark/light mode, clean typography, monospace for code
- Professional but approachable
- Single page app — no routing needed for v0.2

### Page structure

```none
┌─────────────────────────────────────────┐
│  HERO SECTION                           │
│  gitpulse — Your weekly standup, done   │
│  Brief description + how it works       │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│  INPUT FORM                             │
│  GitHub username                        │
│  Repos (comma separated)               │
│  Days (default 7)                       │
│  [Generate Standup] button              │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│  RESULTS (shown after generation)       │
│  ┌─────────────┬───────────────────┐   │
│  │ Commits     │ AI Summary        │   │
│  │ breakdown   │ (markdown)        │   │
│  │ (monospace) │                   │   │
│  └─────────────┴───────────────────┘   │
└─────────────────────────────────────────┘
```

### Color palette

- Background: `#0d1117` (GitHub dark)
- Surface: `#161b22`
- Border: `#30363d`
- Text primary: `#e6edf3`
- Text secondary: `#8b949e`
- Accent: `#238636` (GitHub green)
- Error: `#da3633`

### Typography

- UI: Inter or system font
- Code/commits: JetBrains Mono or monospace

---

## Story Details

### #36 — Scaffold Next.js app

**Setup commands:**

```bash
cd web
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card badge separator
npm install react-markdown
```

**File structure:**

```none
web/
├── app/
│   ├── layout.tsx       ← root layout, fonts, metadata
│   ├── page.tsx         ← main page
│   └── globals.css      ← global styles
├── components/
│   ├── Hero.tsx         ← landing section
│   ├── SummaryForm.tsx  ← input form
│   └── Results.tsx      ← commit breakdown + summary
└── lib/
    └── api.ts           ← API client functions
```

---

### #37, #38 — Input form + API connection

**`lib/api.ts`:**

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface SummariseRequest {
  username: string;
  repos: string[];
  days: number;
}

export interface SummariseResponse {
  display: string;
  summary: string;
  repos: string[];
  days: number;
  generated_at: string;
}

export async function generateSummary(
  req: SummariseRequest,
): Promise<SummariseResponse> {
  const response = await fetch(`${API_URL}/summarise`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail?.error || "Failed to generate summary");
  }
  return response.json();
}
```

**Form fields:**

- `username` — text input, required
- `repos` — text input, comma separated, split to array before API call
- `days` — number input, default 7, min 1, max 90

---

### #39 — Results display

**Two column layout:**

- Left: commit breakdown (`display` field) — monospace font, scrollable
- Right: AI summary (`summary` field) — rendered markdown

**Use `react-markdown` for summary rendering.**

---

### #40, #41 — Loading + error states

**Loading:**

- Button shows spinner + "Generating..." while API call in progress
- Button disabled during loading
- Skeleton placeholders in results area

**Errors:**

- Use shadcn/ui `Alert` component
- Map error messages:
  - 404 → "Repo not found. Check username and repo names."
  - 429 → "GitHub API rate limit exceeded. Try again in a minute."
  - 500 → "Something went wrong. Please try again."

---

### #42 — Vercel deployment

**Steps:**

1. Push `web/` to GitHub (already in monorepo)
2. Go to `vercel.com` → New Project → Import `deepusharma/gitpulse`
3. Set **Root Directory** to `web`
4. Add environment variable:

   ```none
   NEXT_PUBLIC_API_URL=https://web-production-83e65.up.railway.app
   ```

5. Deploy
6. Test live URL

---

## Order of Work

```none
#36 → #37 → #38 → #39 → #40 → #41 → #42
```

---

## Definition of Done

Sprint is complete when:

- [✅] Next.js app running locally on localhost:3000
- [✅] Form submits and returns summary
- [✅] Loading and error states working
- [✅] App deployed on Vercel
- [✅] End to end flow working on live URL
