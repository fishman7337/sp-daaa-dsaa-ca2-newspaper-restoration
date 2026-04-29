# Security Policy

## Supported Versions

This coursework project is maintained as a single current version:

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

## Reporting a Vulnerability

For coursework review, report security issues through the appropriate Singapore
Polytechnic class or module channel. If this project is later published, report
privately to the repository maintainer before opening a public issue.

Please include:

- A short description of the issue.
- Steps to reproduce it.
- Affected files or commands.
- Any known impact on user files or generated outputs.

## Security Checks

CI runs:

- `bandit` for Python static security analysis.
- `pip-audit` for runtime dependency vulnerability checks.

The app reads and writes user-provided local file paths. Treat input files as
untrusted text and avoid running the program on files from unknown sources
without inspecting them first.
