"""Prefix and suffix batch-edit operations for prefix tries."""

from __future__ import annotations

from newspaper_restoration.file_utils import FileManager
from newspaper_restoration.trie import PrefixTrie
from newspaper_restoration.types import WordFrequency


class TrieBatchEditor:
    """Bulk-edit trie words by prefix or suffix."""

    def __init__(self, trie: PrefixTrie) -> None:
        """Initialise the editor with a trie."""
        self.trie = trie
        self._io = FileManager()
        self.mode = "prefix"

    def set_mode(self, mode: str) -> None:
        """Set matching mode to ``prefix`` or ``suffix``."""
        if mode not in {"prefix", "suffix"}:
            raise ValueError("Mode must be 'prefix' or 'suffix'.")
        self.mode = mode

    def delete(self, pattern: str) -> int:
        """Delete all words matching the current mode and pattern."""
        pattern = pattern.lower().strip()
        if not pattern:
            return 0

        to_delete = [word for word, _ in self.preview(pattern)]
        for word in to_delete:
            self.trie.delete_word(word)

        return len(to_delete)

    def export(self, pattern: str, out_file: str) -> int:
        """Export matching words to ``out_file``."""
        words = self.preview(pattern)
        self._io.save_words_to_file(words, out_file)
        return len(words)

    def preview(self, pattern: str) -> list[WordFrequency]:
        """Return all words matching ``pattern`` under the current mode."""
        normalized = pattern.lower().strip()
        return [
            (word, frequency)
            for word, frequency in self.trie.get_all_words()
            if self._matches_mode(word, normalized)
        ]

    def import_with_filter(self, in_file: str, pattern: str = "") -> int:
        """Import words from a file when they match the active mode filter."""
        normalized = pattern.lower().strip()
        count = 0

        for word, frequency in self._io.load_words_from_file(in_file):
            word_lower = word.lower()
            if not normalized or self._matches_mode(word_lower, normalized):
                self.trie.add_word(word_lower, frequency)
                count += 1

        return count

    def rename_pattern(self, old: str, new: str) -> int:
        """Rename all words matching ``old`` to use ``new`` instead."""
        old_normalized = old.lower().strip()
        new_normalized = new.lower().strip()
        if not old_normalized:
            raise ValueError("Old pattern cannot be empty.")

        words = self.preview(old_normalized)
        if not words:
            return 0

        for word, _ in words:
            self.trie.delete_word(word)

        for word, frequency in words:
            if self.mode == "prefix":
                new_word = new_normalized + word[len(old_normalized) :]
            else:
                new_word = word[: -len(old_normalized)] + new_normalized
            self.trie.add_word(new_word, frequency)

        return len(words)

    def stats(self, pattern: str) -> dict[str, float | int | str]:
        """Return count, average frequency, and maximum word length."""
        words = self.preview(pattern)
        total_frequency = sum(frequency for _, frequency in words)
        max_depth = max((len(word) for word, _ in words), default=0)
        avg_frequency = total_frequency / len(words) if words else 0.0

        return {
            "pattern": pattern,
            "mode": self.mode,
            "num_words": len(words),
            "avg_frequency": avg_frequency,
            "max_depth": max_depth,
        }

    def _matches_mode(self, word: str, pattern: str) -> bool:
        """Return whether a word matches the active prefix/suffix mode."""
        if self.mode == "prefix":
            return word.startswith(pattern)
        return word.endswith(pattern)
