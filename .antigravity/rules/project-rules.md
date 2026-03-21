# Project Rules — gitpulse

These rules apply to all agent interactions in this project.
Read and follow these before writing any code.

---

## 1. Code Quality & Clarity

- Write code for clarity and maintainability first — avoid clever or complex logic
- Break complex functions into smaller, well-named functions
- Only optimise for performance when there is a measurable bottleneck
- One function, one responsibility
- Guard clauses over nested ifs — fail fast, return early
- No magic numbers or strings — use named constants or config
- Maximum function length: ~30 lines. If longer, consider splitting.

**Good:**

```python
def is_valid_days(days: int) -> bool:
    return MIN_DAYS <= days <= MAX_DAYS
```

**Bad:**

```python
def process(d):
    if d > 0:
        if d < 91:
            return True
```

---

## 2. Logging & Exception Handling

### Python

- Always use `logging` module — never `print`
- `%s` format style: `logger.debug("msg: %s", var)`
- Log at appropriate levels:
  - `DEBUG` — detailed flow, variable values
  - `INFO` — key lifecycle events
  - `WARNING` — recoverable issues
  - `ERROR` — failures that need attention
- Always log before raising an exception
- Catch specific exceptions — never bare `except:`
- Include context in error messages

```python
# Good
try:
    response = httpx.get(url)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    logger.error("GitHub API error for %s: %s", url, e)
    raise

# Bad
try:
    response = httpx.get(url)
except:
    pass
```

### TypeScript

- Use `console.error` only — never `console.log` in production code
- Always handle Promise rejections
- Use try/catch for all async operations

---

## 3. Configuration — No Hardcoding

- All config goes in environment variables or config files
- Never hardcode: URLs, API keys, usernames, file paths, ports, model names
- Use `.env` for secrets, `pyproject.toml` or `config.py` for app config
- Document all config in `.env.example`

```python
# Good
model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Bad
model = "llama-3.3-70b-versatile"
```

---

## 4. Naming & Folder Structure

### Python naming

- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names — avoid abbreviations: `commits` not `cmts`

### TypeScript naming

- `camelCase` for functions and variables
- `PascalCase` for components and interfaces
- `UPPER_CASE` for constants
- Prefix interfaces with no `I`: `SummaryResponse` not `ISummaryResponse`

### Folder structure

```none
core/       ← shared Python library
cli/        ← CLI client
api/        ← FastAPI backend
web/        ← Next.js frontend
docs/       ← project documentation
tests/      ← mirrors src structure
```

Never put business logic in `cli.py` or `api.py` — always in `core/`.

---

## 5. Testing & Coverage

- Tests required for ALL new functions — no exceptions
- Cover happy path, failure cases, and edge cases
- Edge cases to always consider:
  - Empty inputs (empty list, empty string, None)
  - Boundary values (days=0, days=90, days=91)
  - API failures (404, 429, 500)
  - Network timeouts
  - Missing environment variables
- Mock ALL external calls — Groq, GitHub API, file system where possible
- One test file per module
- Group tests with section comments
- Descriptive names: `test_function_condition_expected`
- Aim for >80% coverage

---

## 6. UI Standards

- Use **shadcn/ui** for all UI components
- Style with **Tailwind CSS** only — no inline styles
- Design inspiration: GitHub.com — clean, minimal, developer-focused
- Color palette: neutral grays with a single accent color
- Typography: monospace for code/commits, sans-serif for UI
- Always show:
  - Loading state during API calls
  - Error state for failures
  - Empty state when no data
- Mobile-first responsive design
- Accessible — use semantic HTML, ARIA labels where needed

---

## 7. Documentation

### Python #SKIP MD024

- Google docstrings on ALL functions and classes
- Module-level docstring at top of every file explaining its purpose
- Inline comments for non-obvious logic only
- Keep docstrings up to date with code changes

```python
"""
Module for reading git commits from local repos or GitHub API.
Supports two sources: local (GitPython) and github (GitHub REST API).
"""

def get_commits(source: str = "local", **kwargs) -> list:
    """
    Get commits from a git repository.

    Args:
        source: Data source — 'local' or 'github'
        **kwargs: Source-specific arguments

    Returns:
        Flat list of commit dicts with keys:
        repo, message, author, date, hash

    Raises:
        ValueError: If source is not 'local' or 'github'
    """
```

### TypeScript #SKIP MD024

- JSDoc comments on all exported functions and components
- Props interfaces documented with descriptions

---

## 8. Linting & Formatting

### Python #SKIP MD024

- **Ruff** for linting and formatting — already configured in pyproject.toml
- Run before every commit: `ruff check . && ruff format .`
- No `print` statements — Ruff rule T20 enforces this
- Type checking with **Pyrefly**

### TypeScript #SKIP MD024

- **ESLint** with Next.js config
- **Prettier** for formatting
- Both run automatically on save in VS Code

---

## 9. License

- License: **MIT**
- Add MIT license header to all new source files:

```python
# MIT License
# Copyright (c) 2026 Deepak Sharma
# See LICENSE file in the project root for full license text.
```

```typescript
// MIT License
// Copyright (c) 2026 Deepak Sharma
// See LICENSE file in the project root for full license text.
```

- `LICENSE` file must exist at project root

---

## 10. Git Workflow

- Never commit directly to master — branch protection enforced
- Branch naming: `feature/description`, `fix/description`, `test/description`
- Conventional commits:
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation
  - `refactor:` code change, no feature/fix
  - `test:` adding tests
  - `chore:` build, config, tooling
- Every PR must reference an issue: `Closes #XX`
- Squash merge only
- Run `pytest -v` and linting before every PR

---

## 11. Good Patterns

### Python - Good Patterns

- **Adapter pattern** — repo_reader supports multiple sources via `source` param
- **Guard clauses** — validate inputs at top of function, return/raise early
- **Dependency injection** — pass dependencies as parameters, don't hardcode
- **Config over code** — use env vars and config files
- **Explicit over implicit** — clear function names, explicit return types

### TypeScript / React - Good Patterns

- **Component composition** — small, reusable components over large monoliths
- **Custom hooks** — extract stateful logic into `useX` hooks
- **Error boundaries** — catch and display errors gracefully
- **Loading/error/success states** — always handle all three

---

## 12. Anti-Patterns to Avoid

### Python - Anti Patterns

- ❌ Bare `except:` — always catch specific exceptions
- ❌ `print()` — use logging
- ❌ Hardcoded values — use config
- ❌ Deep nesting — use guard clauses
- ❌ Long functions — split into smaller ones
- ❌ Importing from `src/` — always use `core/`
- ❌ Mutable default arguments: `def f(x=[])` — use `None` instead
- ❌ Catching and silently ignoring exceptions

### TypeScript - Anti Patterns

- ❌ `any` type — use proper types
- ❌ Inline styles — use Tailwind
- ❌ Direct DOM manipulation — use React state
- ❌ Unhandled promises — always await or catch
- ❌ Prop drilling more than 2 levels — use context or state management
- ❌ `console.log` in production — use proper error handling

### General

- ❌ Copy-paste code — extract into shared functions
- ❌ TODO comments left in PRs — resolve before merging
- ❌ Untested code — tests required for all new functions
- ❌ Secrets in code — use environment variables
