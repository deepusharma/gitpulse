# Sprint 01 — Codebase Restructure

**Sprint goal:** Restructure the codebase into core/cli/api/web and set up agent infrastructure.  
**Milestone:** v0.2 — Web UI  
**Duration:** Week of 2026-03-21  
**Status:** Complete ✅

---

## Sprint Stories

| Issue | Story                            | Status  | Night |
| ----- | -------------------------------- | ------- | ----- |
| #23   | Create AGENTS.md and skill files | ✅ Done | -     |
| #19   | Move shared logic to core/       | ✅ Done | Mon   |
| #20   | Move CLI code to cli/            | ✅ Done | Mon   |
| #21   | Update imports and tests         | ✅ Done | Tue   |
| #22   | Update CI for new structure      | ✅ Done | Tue   |

---

## Story Detailss

### #19 — Move shared logic to core/

**Goal:** Move `repo_reader.py`, `summarise.py`, `utils.py` from `src/` to `core/`.

**Steps:**

1. Create `core/` folder with `__init__.py`
2. `git mv src/repo_reader.py core/repo_reader.py`
3. `git mv src/summarise.py core/summarise.py`
4. `git mv src/utils.py core/utils.py`
5. Create `core/tests/` folder
6. `git mv tests/test_repo_reader.py core/tests/test_repo_reader.py`
7. `git mv tests/test_summarise.py core/tests/test_summarise.py`
8. `git mv tests/test_utils.py core/tests/test_utils.py`
9. Create `core/docs/` folder with empty `core-guide.md`

**Done when:**

- [✅] `core/` exists with `__init__.py`
- [✅] All three modules in `core/`
- [✅] All three test files in `core/tests/`
- [✅] No files left in `src/`

**Do NOT change any logic — move only.**

---

### #20 — Move CLI code to cli/

**Goal:** Move `cli.py` from `src/` to `cli/` and add `main()` function.

**Steps:**

1. Create `cli/` folder with `__init__.py`
2. `git mv src/cli.py cli/cli.py`
3. Create `cli/tests/` folder with empty `test_cli.py`
4. Create `cli/docs/` folder with empty `cli-guide.md`
5. Wrap `if __name__ == "__main__"` block in a `main()` function
6. Add entry point to `pyproject.toml`:

```toml
   [project.scripts]
   gitpulse = "cli.cli:main"
```

**Done when:**

- [✅] `cli/` exists with `__init__.py`
- [✅] `cli.py` is in `cli/`
- [✅] `main()` function exists in `cli.py`
- [✅] `pyproject.toml` has entry point
- [✅] No `cli.py` left in `src/`

---

### #21 — Update imports and tests

**Goal:** Update all imports to use `core.` and verify all tests pass.

**Steps:**

1. Update `cli/cli.py` imports:

   ```python
      from core.repo_reader import get_commits
      from core.summarise import format_commits, to_prompt_str, to_display_str, build_prompt, summarise
      from core.utils import load_env
   ```

2. Update `pyproject.toml` to add `core` and `cli` to Python path
3. Run `pytest -v` — all 16 tests must pass
4. Fix any import errors

**Done when:**

- [✅] All imports reference `core.` not `src.`
- [✅] `pytest -v` shows 16 passing
- [✅] No import errors

---

### #22 — Update CI for new structure

**Goal:** Update GitHub Actions to find tests in new location.

**Steps:**

1. Open `.github/workflows/ci.yml`
2. Verify pytest discovers `core/tests/` automatically
3. Add `pythonpath` config to `pyproject.toml` if needed:

   ```toml
      [tool.pytest.ini_options]
      pythonpath = ["."]
      testpaths = ["core/tests", "cli/tests"]
   ```

4. Push and verify CI passes on PR

**Done when:**

- [✅] CI passes on PR
- [✅] All tests discovered and passing in CI

---

## Order of Work

```none
#19 → #20 → #21 → #22
```

Must be done in order — each story depends on the previous.

---

## Agent Instructions

When working on this sprint:

1. Read `AGENTS.md` first
2. Read `docs/architecture/overview.md` — section 6 (folder structure)
3. Work on stories in order — #19 first
4. Use `git mv` not `mv` — preserves file history
5. Do NOT change any logic during restructure — move only
6. Run `pytest -v` after each story to verify nothing broke
7. One PR per story pair (#19+#20 together, #21+#22 together)

---

## Definition of Done

Sprint is complete when:

- [✅] All 4 stories closed
- [✅] `src/` folder is empty and deleted
- [✅] `pytest -v` shows 16 passing from new locations
- [✅] CI passes
- [✅] CLI still runs: `python -m cli.cli --days 7`
