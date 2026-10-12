# Copilot instructions

- Preserve the existing architecture unless a task explicitly requires
  changing it.
- Inspect existing code before creating new files.
- Do not duplicate existing functionality.
- Keep agents, tools, models, and workflows separated.
- Browser automation belongs in tools, not directly inside agents.
- Use type hints and descriptive docstrings.
- Add or update tests for behavioral changes.
- Never commit credentials, browser state files, tokens, or secrets.
- Update relevant documentation when architecture or behavior changes.
- Use TODO comments instead of pretending unfinished functionality works.
