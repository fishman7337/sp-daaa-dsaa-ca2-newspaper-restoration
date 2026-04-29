"""Persistence and statistics helpers for ``PrefixTrie`` instances."""

from __future__ import annotations

from typing import Any

from newspaper_restoration.file_utils import FileManager
from newspaper_restoration.trie import PrefixTrie, WordFrequency


class TrieManager:
    """Manage loading, saving, and summarising a trie."""

    def __init__(self, trie: PrefixTrie) -> None:
        """Initialise the manager with a trie instance."""
        self.trie = trie
        self.file_manager = FileManager()

    def load_trie_from_file(self, filename: str) -> bool:
        """Load ``word, frequency`` rows from a file into the trie."""
        if not self.file_manager.file_exists(filename):
            return False

        words = self.file_manager.load_words_from_file(filename)
        if not words:
            return False

        self.trie.clear()
        for word, frequency in words:
            self.trie.add_word(word, frequency)

        return True

    def save_trie_structure(self, filename: str) -> bool:
        """Save the current trie in display format."""
        return self.file_manager.save_trie_structure(self.trie, filename)

    def save_words_to_file(self, filename: str) -> bool:
        """Save all words and frequencies from the trie."""
        return self.file_manager.save_words_to_file(self.trie.get_all_words(), filename)

    def get_trie_statistics(self) -> dict[str, Any]:
        """Return basic statistics for the current trie."""
        words = self.trie.get_all_words()

        if not words:
            return {
                "word_count": 0,
                "total_frequency": 0,
                "avg_frequency": 0,
                "max_frequency": 0,
                "min_frequency": 0,
                "most_frequent_word": None,
            }

        frequencies = [frequency for _, frequency in words]

        return {
            "word_count": len(words),
            "total_frequency": sum(frequencies),
            "avg_frequency": sum(frequencies) / len(frequencies),
            "max_frequency": max(frequencies),
            "min_frequency": min(frequencies),
            "most_frequent_word": max(words, key=lambda item: item[1])[0],
        }

    def bulk_add_words(self, words: list[WordFrequency]) -> int:
        """Add several words and return the number accepted."""
        added_count = 0
        for word, frequency in words:
            if word.strip():
                self.trie.add_word(word, frequency)
                added_count += 1
        return added_count
