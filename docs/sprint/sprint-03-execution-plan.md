# Sprint 03 - Next.js Frontend Execution Plan

## Goal Description
Build and deploy a clean, GitHub-inspired single-page web UI for gitpulse as per the v0.2 milestone. The web app will allow users to input their GitHub username, a list of repositories, and a lookback period to generate an AI-powered standup summary via the FastAPI backend.

## Proposed Changes

### Scaffold Next.js App (#36)
- **Directory**: `web` (will be created)
- **Tech**: Next.js 14 App Router, TypeScript, Tailwind CSS, shadcn/ui.
- **Commands**: 
  - `npx -y create-next-app@latest . --typescript --tailwind --app --no-src-dir` inside the `web` directory.
  - Setup shadcn `npx -y shadcn-ui@latest init -y` with default style (New York), neutral color, CSS variables = yes.
  - Add shadcn components: `npx -y shadcn-ui@latest add button input card badge separator alert skeleton`.
  - `npm install react-markdown`
- **Structure**: Create `components/Hero.tsx`, `components/SummaryForm.tsx`, `components/Results.tsx`, `lib/api.ts`.
- **Environment**: Define `.env.local` inside `web/` with `NEXT_PUBLIC_API_URL=http://localhost:8000` for local dev.

### API Connection & Input Form (#37, #38)
- **`lib/api.ts`**:
  - Implement `SummariseRequest` and `SummariseResponse` interfaces.
  - Implement async `generateSummary` function using `fetch` with error translation (mapping API 404, 429, 500 responses into user-friendly `Error` objects).
- **`components/SummaryForm.tsx`**:
  - Implement inputs: `username` (text), `repos` (comma-separated text -> split to array), `days` (number).
  - Add sanitization: `repos.split(',').map(repo => repo.trim())`
  - Submit handler calls `api.ts`.
  - Pass the returned data up to `page.tsx` state.

### Results Display (#39)
- **`components/Results.tsx`**:
  - Split into a responsive two-column grid (`grid-cols-1 md:grid-cols-2`).
  - **Left column**: Raw commit breakdown using `<pre>` and monospace font for `display`. Wrap in `max-h-[600px] overflow-y-auto` to prevent infinite scroll on large results.
  - **Right column**: AI-generated summary rendered with `react-markdown` for the `summary` string.

### Loading & Error States (#40, #41)
- Add loading boolean state in `page.tsx`/`SummaryForm.tsx`. Button shows a spinner while loading and becomes disabled.
- Add an error state string. If set, render it inside a shadcn `Alert` component (variant `destructive`) immediately below the form or inside it.
- Render Skeleton placeholders in `Results.tsx` when data is loading.

### Vercel Deployment (#42)
- Push `web` folder to GitHub repo.
- User imports project to Vercel, setting Root Directory to `web` and env var `NEXT_PUBLIC_API_URL=https://gitpulse-api.railway.app` (or whatever the deployed URL is).

## Verification Plan

### Automated Tests
- Running the `next dev` server to ensure local build succeeds.
- No Vitest setup is strictly required by the sprint doc for v0.2, but components will be type-checked strictly.

### Manual Verification
- Start local Dev server (`npm run dev`) and test standard workflow against local FastAPI backend (or prod backend).
- Ensure input forms capture and split repos strings correctly.
- Verify Markdown renders nicely and the Results container stays within `max-h-[600px]`.
- Test Error states by forcing 404 (invalid repo), etc.
- Verify Vercel deployment with correct environment variables and root directory.
