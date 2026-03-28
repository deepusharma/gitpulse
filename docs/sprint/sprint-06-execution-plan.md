# Sprint 06 — Web UI Polish: Execution Plan

## 1. Context & Approach
This plan outlines the frontend implementation for Sprint 06 based on the active stories.

**Component Structure Review:**
- `page.tsx`: Manages high-level state (`data`, `isLoading`) and layout transitions.
- `SummaryForm.tsx`: Handles user input and API calls. Errors are rendered here.
- `Results.tsx`: Displays the generated `display` and `summary` markdown. Includes loading skeletons.

**Clipboard API Approach (#90):**
- Use the modern `navigator.clipboard.writeText()` API.
- Add a "Copy to Clipboard" button in the `Results.tsx` Standup Summary card header.
- Maintain a local state `isCopied` initialized to `false`, toggling to `true` on click and reverting it back after 2 seconds via `setTimeout`.
- Incorporate `lucide-react` icons (e.g., `Copy`, `Check`) for visual feedback.

## 2. Step-by-Step Execution Plan

### Step 1: Implement Empty & Error States (Story #91)
- **Error States:** `lib/api.ts` already extracts backend error messages (422, 404, 429, 500) effectively. We will ensure they render cleanly in `SummaryForm.tsx` using `Alert`. We can further improve by distinguishing between rate limits (429) and standard errors (404/500).
- **Empty States:** In `Results.tsx`, if the API returns a response but indicating no commits, we will display a friendly "No commit activity found" empty state component giving suggestions (e.g., "Try increasing the lookback period"). We'll need to parse `data.display` to determine if it actually contains commits.
- **Loading State:** Skeletons are already in place. We will ensure a smooth transition from loading to empty/error states.

### Step 2: Add Copy to Clipboard Button (Story #90)
- Extract the Standup Summary CardHeader in `Results.tsx` to accommodate a flex layout for a shadcn `Button` (variant `outline` or `ghost`, size `sm`).
- Wire the `onClick` event to `navigator.clipboard.writeText(data.summary)`.
- Use a state flag to show a "Copied" text and checkmark icon for 2 seconds.

### Step 3: Add Summary Stats (Story #92)
Since we are focusing on the frontend without altering the backend API contract, we will derive the necessary stats dynamically based on the returned `SummariseResponse` data:
- **Word Count:** Count the words by splitting `data.summary` via whitespace (`data.summary.trim().split(/\s+/).length`).
- **Generation Time:** We'll track the duration of the generation request using `performance.now()` in `SummaryForm` before and after the API call as the backend only returns a `generated_at` timestamp. We'll pass this via a new callback or state up to `page.tsx` and down to `Results.tsx`.
- **Commits Processed:** We'll count the exact number of commits by matching typical list items (like `- `) inside `data.display`.
- **Repos Included:** Derive from `data.repos.length`.
- **Display:** Show these stats elegantly at the bottom of the Standup Summary card utilizing shadcn `Badge` or small text.

## 3. Order of Execution
As required, the execution sequence will be: **#91 → #90 → #92**.

All changes will be tested to ensure the Next.js build passes cleanly.
