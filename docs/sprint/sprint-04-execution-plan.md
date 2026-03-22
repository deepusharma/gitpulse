# Sprint 04 Execution Plan — v0.3 UI Polish

## Goal Description
Enhance the gitpulse web UI by fixing markdown rendering, improving the layout with a split view, adding a persistent header/footer, and implementing GitHub OAuth login using NextAuth.js. This sprint focuses purely on the frontend (`web/` directory).

## Current State Review
**1. Stories (#67, #68, #66, #65):**
   - **#67**: Markdown rendering is halfway there (`react-markdown` and `prose` classes exist), but `@tailwindcss/typography` is missing so the classes have no effect.
   - **#68**: Form and results are stacked centrally. Story requires a split view: form fixed on the left (30%), results scrolling on the right (70%) on desktop.
   - **#66**: `layout.tsx` is bare. Needs `<Header>` and `<Footer>` layout wrappers.
   - **#65**: GitHub OAuth needs to wrap the app in `SessionProvider`, provide an API route for `next-auth`, and link session data to the UI (avatar in header, auto-fill username in form).

**2. Current `web/` Folder Structure:**
   - ✅ Next.js App Router structure (`app/page.tsx`, `app/layout.tsx`, `app/globals.css`)
   - ✅ Components (`Hero.tsx`, `Results.tsx`, `SummaryForm.tsx`, various `ui/` elements)
   - ✅ API lib (`lib/api.ts`)
   - ❌ Missing: `next-auth` dependency, auth API routes, Header/Footer components.

**3. Execution Order Confirmation:**
Confirmed: `#67` → `#68` → `#66` → `#65`.
Reasoning: Start with the quickest visual win (#67), then establish the core layout geometry (#68), then frame it with the header/footer (#66), and finally tackle the complex state/auth logic (#65).

**4. Dependencies to Install:**
   - `@tailwindcss/typography`
   - `next-auth`

**5. Gaps and Risks:**
   - **NextAuth.js in Next.js 14 App Router**: Requires creating the API route at `api/auth/[...nextauth]/route.ts` and ensuring `SessionProvider` is added via a client component wrapper (since `layout.tsx` is a server component by default).
   - **Session handling**: Need to seamlessly pass session data from the header down to the `SummaryForm` component to auto-fill the username.
   - **Manual OAuth Setup**: **CRITICAL RISK.** We cannot test or verify `#65` until the GitHub OAuth app is registered and environment variables are supplied.

## Manual Setup Required Before #65

To implement Story #65, you **must** manually set up a GitHub OAuth App.
1. Go to `https://github.com/settings/developers` → New OAuth App
2. Homepage URL: `http://localhost:3000` (or Vercel URL)
3. Callback URL: `http://localhost:3000/api/auth/callback/github`
4. Generate a `NEXTAUTH_SECRET` (e.g., `openssl rand -base64 32`)
5. Add these to `web/.env.local`:
   ```
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your_secret
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   ```

## Proposed Changes

### Story #67: Fix Markdown Rendering
1. Install `@tailwindcss/typography` in the `web/` directory.
2. Update Tailwind config to include the typography plugin so `prose` classes in `Results.tsx` apply the GitHub-style markdown themes natively.

### Story #68: Improve Form and Results Layout
1. Modify `app/page.tsx` to implement a CSS Grid / Flex split-screen layout (`md:flex-row`).
2. Constrain the form to 30% width (`sticky top-24` on desktop) and allow the results container (70%) to scroll independently.
3. Keep the mobile layout stacked.

### Story #66: Add Header and Footer
1. Create `components/Header.tsx` and `components/Footer.tsx`.
2. Update `app/layout.tsx` to wrap `{children}` between `<Header />` and `<Footer />`.
3. Style them using the GitHub-inspired dark theme from `sprint-04.md`.

### Story #65: GitHub OAuth (Requires manual setup first)
1. Install `next-auth`.
2. Create `app/api/auth/[...nextauth]/route.ts` with the GitHub provider.
3. Create a `components/Providers.tsx` client component exporting `<SessionProvider>` and wrap `RootLayout`.
4. Update `Header.tsx` to display GitHub Login/Logout buttons and the user's avatar.
5. Update `SummaryForm.tsx` to use `useSession()` to auto-fill the GitHub username input.

## Verification Plan

### Automated Tests
Run standard build checks and Next.js linting (`npm run build`, `npm run lint`).

### Manual Verification
1. Start the dev server (`npm run dev`).
2. Verify markdown renders with appropriate headings, typography, and lists on a generated summary.
3. Verify the layout splits neatly on large screens and stays stacked on mobile.
4. Verify the Header and Footer exist on all pages.
5. Once env vars are provided: verify the login flow authenticates with GitHub, shows the avatar in the header, and maps the username into the form.
