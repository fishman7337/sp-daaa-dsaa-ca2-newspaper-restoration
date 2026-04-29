# Testing and Quality

## Local Quality Commands

```powershell
python -m ruff format --check .
python -m ruff check .
python -m pytest
python -m bandit -r src -c pyproject.toml
python -m pip_audit -r requirements.txt
```

## Test Coverage

The pytest suite covers:

- Prefix trie insertion, deletion, exact search, wildcard search, frequency
  handling, and display for empty tries.
- Best-match and all-match restoration.
- File restoration with whitespace preservation.
- Keyword file parsing and trie manager load/save behavior.
- Advanced pattern search, batch editing, and fuzzy search.

## CI

GitHub Actions runs lint, formatting, tests with coverage, Bandit, and runtime
dependency auditing. The matrix currently targets Python 3.11 and 3.12.
