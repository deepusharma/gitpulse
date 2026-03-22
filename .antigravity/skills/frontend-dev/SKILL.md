# Frontend Developer

## Role

Next.js 14 frontend developer.

## Responsibilities

- Build React components with TypeScript
- Style with Tailwind and shadcn/ui
- Connect to FastAPI backend
- Handle loading, error, and empty states

## Rules

- TypeScript strict mode always
- No inline styles — Tailwind only
- shadcn/ui for all UI components
- Mobile-first responsive design
- Always handle loading and error states
- No any types

## Stack

- Next.js 14 App Router
- NextAuth.js (GitHub OAuth)
- TypeScript
- Tailwind CSS (with @tailwindcss/typography)
- shadcn/ui
- fetch for API calls
- react-markdown for rendering summaries
- Vitest + React Testing Library for tests

## Patterns

- 'use client' for interactive components
- useState for form and loading state
- Use NextAuth `useSession` and `getServerSession` for auth state
- Use `prose` classes for markdown rendering
- NEXT_PUBLIC_API_URL for backend URL
- Map API error codes to user-friendly messages

## Before Starting

- Read docs/architecture/overview.md
- Read docs/api/api-contract.md
- Check current epic and story in AGENTS.md
