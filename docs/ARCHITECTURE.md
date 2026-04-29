# Architecture

The project is a small layered CLI application.

## Layers

```text
ConsoleUI
   |
TrieApp
   |
TrieProcessor
   |
PrefixTrie + TextProcessor + TrieManager + Extra Features
   |
FileManager
```

## Key Modules

- `newspaper_restoration.trie` contains the `PrefixTrie` data structure and
  single-character wildcard lookup. It re-exports `TrieNode` from
  `newspaper_restoration.trie_node` for backwards-compatible imports.
- `newspaper_restoration.text_processor` restores damaged words and files while
  preserving punctuation and whitespace.
- `newspaper_restoration.trie_manager` loads, saves, and summarises trie data.
- `newspaper_restoration.trie_pattern_resolver`,
  `newspaper_restoration.trie_batch_editor`,
  `newspaper_restoration.trie_visualizer`, and
  `newspaper_restoration.fuzzy_searcher` contain the optional feature classes.
- `newspaper_restoration.extra_features` is a compatibility export module for
  those optional feature classes.
- `newspaper_restoration.trie_processor` owns the interactive command panels.
- `newspaper_restoration.console` contains user-facing menu rendering.

## Design Decisions

- The trie is deterministic: output is sorted by frequency and then alphabetic
  order so tests and restored files are reproducible.
- The wildcard `*` means exactly one unknown character, matching the CA2
  assignment style.
- File I/O is isolated in `FileManager` so tests can use temporary paths.
- Plot drawing stays in the visualiser, while graph construction can be tested
  without opening windows.
- Implementation files are kept to one class per file to make the CA2 codebase
  easier to navigate during review.
