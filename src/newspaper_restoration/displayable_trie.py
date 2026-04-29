"""Protocol for trie-like objects that can render themselves."""

from __future__ import annotations

from typing import Protocol


class DisplayableTrie(Protocol):
    """Protocol for objects that can provide a displayable trie dump."""

    def display_trie(self) -> str:
        """Return a displayable trie dump."""
