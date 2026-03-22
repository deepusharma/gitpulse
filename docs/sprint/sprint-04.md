# Sprint 04 — UI Polish

**Sprint goal:** Polish the gitpulse web UI with GitHub OAuth login, header/footer, proper markdown rendering and improved layout.  
**Milestone:** v0.3 — UI Polish  
**Duration:** Week of 2026-03-22  
**Status:** In Progress

---

## Sprint Stories

| Issue | Story                               | Status         | Night   |
| ----- | ----------------------------------- | -------------- | ------- |
| #67   | Fix markdown rendering              | 🔵 This Sprint | Mon     |
| #68   | Improve form and results layout     | 🔵 This Sprint | Mon     |
| #66   | Add header and footer               | 🔵 This Sprint | Tue     |
| #65   | GitHub OAuth login with NextAuth.js | 🔵 This Sprint | Wed-Thu |

---

## Story Details

### #67 — Fix markdown rendering

**Goal:** AI summary renders as proper markdown not plain text.

**Fix:**

- Install `@tailwindcss/typography`
- Add `typography` plugin to `tailwind.config.ts`
- Apply `prose prose-invert` classes to summary container

**Done when:**

- [ ] Headings render with size hierarchy
- [ ] Bullet points render as bullets
- [ ] Bold text renders correctly
- [ ] Dark theme compatible

---

### #68 — Improve form and results layout

**Goal:** Split view — form fixed left, results scrollable right on desktop.

**Layout:**

```
Desktop:
┌─────────────────┬──────────────────────────┐
│  Form (30%)     │  Results (70%)           │
│  stays fixed    │  scrollable              │
│                 │  ┌──────────┬─────────┐  │
│                 │  │ Commits  │ Summary │  │
│                 │  └──────────┴─────────┘  │
└─────────────────┴──────────────────────────┘

Mobile:
┌────────────────────┐
│ Form               │
├────────────────────┤
│ Results            │
└────────────────────┘
```

**Done when:**

- [ ] Desktop: form fixed left, results right
- [ ] Mobile: stacked layout
- [ ] Smooth transition when results appear
- [ ] Results panel scrollable independently

---

### #66 — Add header and footer

**Goal:** Professional header and footer matching GitHub dark theme.

**Header:**

- gitpulse logo/wordmark left
- GitHub repo link right
- User avatar + name after login (placeholder for now)

**Footer:**

- Copyright 2026 Deepak Sharma
- GitHub repo link
- Version number from package.json
- MIT License link

**Done when:**

- [ ] Header visible on all pages
- [ ] Footer visible on all pages
- [ ] Responsive on mobile
- [ ] Dark theme consistent

---

### #65 — GitHub OAuth login with NextAuth.js

**Goal:** Users can log in with GitHub. Username auto-fills in form.

**Setup required (manual — before agent starts):**

1. Go to `github.com/settings/developers`
2. New OAuth App:
   - Homepage URL: your Vercel URL
   - Callback URL: `https://your-vercel-url/api/auth/callback/github`
3. Copy Client ID and Client Secret

**Environment variables needed:**

```
# web/.env.local
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate with: openssl rand -base64 32
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
```

**Implementation:**

- Install `next-auth`
- Create `app/api/auth/[...nextauth]/route.ts`
- Wrap app in `SessionProvider`
- Add login/logout button to header
- Auto-fill username field from session

**Done when:**

- [ ] Login with GitHub button works
- [ ] After login username auto-fills in form
- [ ] User avatar and name in header
- [ ] Logout button works
- [ ] Session persists on refresh
- [ ] Works on Vercel with production OAuth app

---

## Order of Work

```
#67 → #68 → #66 → #65
```

Start with quick wins (#67, #68) before the more complex auth work (#65).

---

## Technical Notes

### Color palette (GitHub-inspired dark)

```
Background:  #0d1117
Surface:     #161b22
Border:      #30363d
Text:        #e6edf3
Text muted:  #8b949e
Accent:      #238636
Error:       #da3633
```

### Dependencies to install

```bash
cd web
npm install @tailwindcss/typography next-auth
```

### Vercel environment variables needed for #65

```
NEXTAUTH_URL=https://your-vercel-url.vercel.app
NEXTAUTH_SECRET=your_secret
GITHUB_CLIENT_ID=your_id
GITHUB_CLIENT_SECRET=your_secret
```

---

## Definition of Done

Sprint is complete when:

- [ ] Markdown renders properly
- [ ] Split view layout working on desktop
- [ ] Header and footer on all pages
- [ ] GitHub OAuth login working locally
- [ ] GitHub OAuth login working on Vercel
- [ ] All changes deployed and live
