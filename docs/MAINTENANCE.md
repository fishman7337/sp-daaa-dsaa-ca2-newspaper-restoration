# Maintenance Notes

## Release Checklist

- Update `CHANGELOG.md`.
- Run all commands in `docs/TESTING.md`.
- Confirm assignment and author metadata are still accurate.
- Confirm sample data paths in `README.md` and `docs/USAGE.md` still work.
- Remove generated caches before packaging or sharing.

## Naming

The project is named `SP DSAA Newspaper Restoration` for human-facing docs and
`sp-dsaa-newspaper-restoration` for Python packaging metadata.

## Generated Files

Do not commit:

- `__pycache__/`
- `.pytest_cache/`
- `.ruff_cache/`
- `htmlcov/`
- `.coverage`
- ad hoc output files under `outputs/`
