# SP DSAA Newspaper Restoration

Prefix-trie based command-line application for restoring damaged historical
newspaper text where missing characters are represented by `*`.

This project was completed under Singapore Polytechnic, School of Computing,
Diploma in Applied AI & Analytics, module ST1507 Data Structure & Algorithm
(AI), CA2, AY25/26 Year 2 Semester 1. Student: Goh Kun Ming, DAAA. Lecturer:
Liu Zheng.

## Features

- Construct, edit, save, and load a prefix trie of keywords.
- Restore individual words or whole text files using best-match restoration.
- List all possible matches for damaged words.
- Advanced regex-like trie search with character classes and quantifiers.
- Prefix/suffix batch editing for keyword maintenance.
- Fuzzy search using edit distance.
- Optional NetworkX and matplotlib graph visualisations.

## Project Layout

```text
.
|-- src/newspaper_restoration/   # Application package
|-- tests/                       # Pytest suite
|-- data/
|   |-- keywords/                # Keyword frequency lists
|   |-- sample_texts/            # Damaged sample inputs
|   |-- expected_outputs/        # Historical restored outputs
|   |-- trie_dumps/              # Saved trie display examples
|   `-- legacy/                  # Preserved scratch/legacy CA2 files
|-- docs/                        # Usage, design, data, and quality docs
`-- .github/workflows/ci.yml     # Lint, test, and security CI
```

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python main.py
```

You can also run the installed console command:

```powershell
newspaper-restoration
```

## Common Commands

Run tests:

```powershell
python -m pytest
```

Run formatting and lint checks:

```powershell
python -m ruff format --check .
python -m ruff check .
```

Run security checks:

```powershell
python -m bandit -r src -c pyproject.toml
python -m pip_audit -r requirements.txt
```

## Data Format

Keyword files use one keyword per line. Frequencies are optional:

```text
the, 120
again, 14
newspaper
```

The wildcard `*` represents exactly one missing character. For example, `t*e`
matches `the`; `t**e` matches a four-letter word such as `time` when present in
the trie.

## Documentation

- [Usage Guide](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data Guide](docs/DATA.md)
- [Testing and Quality](docs/TESTING.md)
- [Assignment Context](docs/ASSIGNMENT_CONTEXT.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## License

This repository is coursework material. See [LICENSE](LICENSE) before reuse.
