# Code Reviewer — gitpulse

## Extends

Global reviewer skill — see ~/.antigravity/skills/reviewer/SKILL.md

## Project-specific additions

### gitpulse checklist

- [ ] Python: imports from core/ not src/
- [ ] Python: pytest -v passes before PR
- [ ] TypeScript: npm run build passes before PR
- [ ] API changes match docs/api/api-contract.md
- [ ] New features have corresponding GitHub issue
- [ ] Sprint story acceptance criteria met
- [ ] **Versioning**: Atomic sync applied to package.json, pyproject.toml, and AGENTS.md
- [ ] **QA**: Edge-case coverage present for all new logic (empty inputs, timeouts)

### Before reviewing

- Read AGENTS.md
- Check linked issue acceptance criteria
