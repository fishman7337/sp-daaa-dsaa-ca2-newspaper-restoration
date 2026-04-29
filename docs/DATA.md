# Data Guide

The original loose text files have been preserved and grouped by purpose.

## Folders

- `data/keywords`: keyword frequency lists used to build tries.
- `data/sample_texts`: damaged sample input texts.
- `data/expected_outputs`: restored outputs from previous runs or expected
  examples.
- `data/trie_dumps`: saved trie display files.
- `data/legacy`: miscellaneous legacy and scratch files preserved from the
  original CA2 folder.

## Keyword Format

Each row is either:

```text
word
```

or:

```text
word, frequency
```

Rows without a frequency default to `1`. Frequencies must be positive integers.

## Damaged Text Format

Damaged characters are represented with `*`. Each `*` is one missing character.
Whitespace and punctuation are preserved during restoration.
