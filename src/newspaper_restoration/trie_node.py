"""Trie node model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TrieNode:
    """A single node in a prefix trie.

    Attributes:
        children: Mapping from the next character to a child node.
        is_end_of_word: Whether this node terminates a complete keyword.
        frequency: Keyword frequency when ``is_end_of_word`` is true.

    """

    children: dict[str, TrieNode] = field(default_factory=dict)
    is_end_of_word: bool = False
    frequency: int = 0

    def __str__(self) -> str:
        """Return a compact representation useful during debugging."""
        return f"Node(is_end={self.is_end_of_word}, frequency={self.frequency})"
