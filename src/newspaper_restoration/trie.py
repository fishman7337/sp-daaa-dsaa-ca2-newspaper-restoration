"""Prefix trie data structure used by the restoration workflow."""

from __future__ import annotations

from newspaper_restoration.trie_node import TrieNode
from newspaper_restoration.types import WordFrequency


class PrefixTrie:
    """Store words and frequencies for exact and wildcard lookups.

    The restoration assignment uses ``*`` as a single-character wildcard, so
    ``t*e`` matches ``the`` but not ``three``.
    """

    def __init__(self) -> None:
        """Create an empty trie."""
        self.root = TrieNode()
        self.word_count = 0

    def clear(self) -> None:
        """Remove all words from the trie."""
        self.root = TrieNode()
        self.word_count = 0

    def add_word(self, word: str, frequency: int = 1) -> None:
        """Add a word to the trie, increasing its stored frequency.

        Args:
            word: Keyword to insert.
            frequency: Positive frequency value to add.

        Raises:
            ValueError: If ``frequency`` is less than one.
        """
        if frequency < 1:
            raise ValueError("frequency must be at least 1")

        normalized = self._normalize(word)
        if not normalized:
            return

        node = self.root
        for char in normalized:
            node = node.children.setdefault(char, TrieNode())

        if not node.is_end_of_word:
            self.word_count += 1
        node.is_end_of_word = True
        node.frequency += frequency

    def delete_word(self, word: str) -> bool:
        """Delete a word from the trie.

        Args:
            word: Keyword to remove.

        Returns:
            ``True`` when a word was removed; otherwise ``False``.
        """
        normalized = self._normalize(word)
        if not self.search_word(normalized):
            return False

        self._delete_helper(self.root, normalized, 0)
        return True

    def search_word(self, word: str) -> bool:
        """Check whether a complete word exists in the trie."""
        node = self._navigate_to(word)
        return bool(node and node.is_end_of_word)

    def get_word_frequency(self, word: str) -> int:
        """Return the stored frequency for ``word``, or ``0`` when absent."""
        node = self._navigate_to(word)
        if node is None or not node.is_end_of_word:
            return 0
        return node.frequency

    def get_all_words(self) -> list[WordFrequency]:
        """Return all stored words as ``(word, frequency)`` tuples."""
        words: list[WordFrequency] = []
        self._collect_words(self.root, "", words)
        return words

    def find_matching_words(self, pattern: str) -> list[WordFrequency]:
        """Find all words that match a pattern containing ``*`` wildcards.

        Args:
            pattern: Search pattern where each ``*`` represents one unknown
                character.

        Returns:
            Matches sorted by descending frequency, then alphabetically for
            deterministic output.
        """
        normalized = self._normalize(pattern)
        if not normalized:
            return []

        matches: list[WordFrequency] = []
        self._find_matches(self.root, normalized, 0, "", matches)
        matches.sort(key=lambda item: (-item[1], item[0]))
        return matches

    def get_best_match(self, pattern: str) -> str | None:
        """Return the highest-frequency match for a wildcard pattern."""
        matches = self.find_matching_words(pattern)
        return matches[0][0] if matches else None

    def display_trie(self) -> str:
        """Return a deterministic, human-readable representation of the trie."""
        if self.word_count == 0:
            return "[]"

        result = ["["]
        self._display_helper(self.root, "", result, 0)
        result.append("]")
        return "\n".join(result)

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalise user input before trie operations."""
        return value.lower().strip()

    def _delete_helper(self, node: TrieNode, word: str, index: int) -> bool:
        """Return whether the current node can be pruned after deletion."""
        if index == len(word):
            if not node.is_end_of_word:
                return False
            node.is_end_of_word = False
            node.frequency = 0
            self.word_count -= 1
            return not node.children

        char = word[index]
        child = node.children.get(char)
        if child is None:
            return False

        should_delete = self._delete_helper(child, word, index + 1)
        if should_delete:
            del node.children[char]
            return not node.is_end_of_word and not node.children
        return False

    def _collect_words(self, node: TrieNode, prefix: str, words: list[WordFrequency]) -> None:
        """Collect words below ``node`` using depth-first traversal."""
        if node.is_end_of_word:
            words.append((prefix, node.frequency))

        for char in sorted(node.children):
            self._collect_words(node.children[char], prefix + char, words)

    def _find_matches(
        self,
        node: TrieNode,
        pattern: str,
        index: int,
        word: str,
        matches: list[WordFrequency],
    ) -> None:
        """Collect all words matching ``pattern`` from ``node`` downward."""
        if index == len(pattern):
            if node.is_end_of_word:
                matches.append((word, node.frequency))
            return

        char = pattern[index]
        if char == "*":
            for child_char in sorted(node.children):
                child_node = node.children[child_char]
                self._find_matches(child_node, pattern, index + 1, word + child_char, matches)
        elif char in node.children:
            self._find_matches(node.children[char], pattern, index + 1, word + char, matches)

    def _display_helper(
        self,
        node: TrieNode,
        prefix: str,
        result: list[str],
        level: int,
    ) -> None:
        """Append display lines for all children below ``node``."""
        dots = "." * (level + 1)

        for char in sorted(node.children):
            child = node.children[char]
            current_path = prefix + char
            if child.children:
                line = f"{dots}[{current_path}"
                if child.is_end_of_word:
                    line += f"({child.frequency})*"
                result.append(line)
                self._display_helper(child, current_path, result, level + 1)
                result.append(f"{dots}]")
            elif child.is_end_of_word:
                result.append(f"{dots}>{current_path}({child.frequency})*")

    def _navigate_to(self, prefix: str) -> TrieNode | None:
        """Return the node for ``prefix`` when it exists."""
        node = self.root
        for char in self._normalize(prefix):
            node = node.children.get(char)
            if node is None:
                return None
        return node


__all__ = ["PrefixTrie", "TrieNode", "WordFrequency"]
