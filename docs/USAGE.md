# Usage Guide

## Start the App

```powershell
python main.py
```

or, after installation:

```powershell
newspaper-restoration
```

## Construct or Edit Trie

Choose menu option `1`.

| Command | Meaning |
| ------- | ------- |
| `+word` | Add a keyword with frequency 1. |
| `+word(5)` | Add a keyword with frequency 5. |
| `-word` | Delete a keyword. |
| `?word` | Search for an exact keyword. |
| `#` | Display the trie. |
| `@file.txt` | Save the trie display to a file. |
| `~data/keywords/sample_keywords.txt` | Load keywords from a file. |
| `=file.txt` | Save the keyword list to a file. |
| `!` | Show help. |
| `\` | Exit the panel. |

## Restore Text

Choose menu option `2`.

| Command | Meaning |
| ------- | ------- |
| `$ra*n*ow` | List all matching keywords. |
| `?ra*n*ow` | Print the best matching keyword. |
| `&` | Restore a file using all matches. |
| `@` | Restore a file using best matches. |

When restoring a file, the program asks for input and output paths. Example
input:

```text
T*e yearly contest happened a*ain.
```

Example best-match output:

```text
<The> yearly contest happened <again>.
```

## Extra Features

Menu option `3` opens advanced pattern search. Menu option `4` opens prefix and
suffix batch editing. Menu option `5` opens visualisation. Menu option `6` opens
fuzzy search.

For headless environments, set `MPLBACKEND=Agg` before using graph functions in
tests or scripts.
