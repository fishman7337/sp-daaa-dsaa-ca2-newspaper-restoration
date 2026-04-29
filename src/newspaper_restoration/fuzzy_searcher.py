"""Fuzzy trie lookup using edit distance."""

from __future__ import annotations

from newspaper_restoration.trie import PrefixTrie
from newspaper_restoration.trie_node import TrieNode


class FuzzySearcher:
    """Approximate trie lookup using Levenshtein edit distance."""

    def __init__(self, trie: PrefixTrie) -> None:
        """Initialise the searcher with a trie."""
        self.trie = trie

    def search(self, word: str, max_dist: int = 2) -> list[tuple[str, int, int]]:
        """Return ``(word, frequency, distance)`` matches within ``max_dist``."""
        target = word.lower().strip()
        target_length = len(target)
        results: list[tuple[str, int, int]] = []
        previous_row = list(range(target_length + 1))

        def recurse(node: TrieNode, prefix: str, prior_row: list[int]) -> None:
            for char, child in sorted(node.children.items()):
                current_row = [prior_row[0] + 1]
                for index in range(1, target_length + 1):
                    cost = 0 if target[index - 1] == char else 1
                    current_row.append(
                        min(
                            current_row[index - 1] + 1,
                            prior_row[index] + 1,
                            prior_row[index - 1] + cost,
                        )
                    )

                distance = current_row[-1]
                candidate = prefix + char
                if distance <= max_dist and child.is_end_of_word:
                    results.append((candidate, child.frequency, distance))

                if min(current_row) <= max_dist:
                    recurse(child, candidate, current_row)

        recurse(self.trie.root, "", previous_row)
        results.sort(key=lambda item: (item[2], -item[1], item[0]))
        return results
