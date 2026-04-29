# Contributing

Thank you for improving this project. Keep contributions small, tested, and
aligned with the ST1507 CA2 scope.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Standards

- Follow PEP 8 for style and PEP 257 for docstrings.
- Use Google-style docstrings for public modules, classes, and methods.
- Keep trie behavior deterministic so test results and restored output are
  reproducible.
- Add or update pytest tests for behavior changes.
- Do not commit generated folders such as `__pycache__`, `.pytest_cache`, or
  `htmlcov`.

## Quality Gate

Run the following before submitting changes:

```powershell
python -m ruff format --check .
python -m ruff check .
python -m pytest
python -m bandit -r src -c pyproject.toml
```

## Pull Request Checklist

- The change has a clear purpose.
- Tests cover the new or changed behavior.
- Documentation is updated when commands, data layout, or behavior changes.
- Security-sensitive changes, such as file handling, are explained.
- Coursework authorship and attribution remain accurate.
