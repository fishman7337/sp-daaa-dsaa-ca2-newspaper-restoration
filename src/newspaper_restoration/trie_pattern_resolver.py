"""Advanced pattern search over prefix tries."""

from __future__ import annotations

from newspaper_restoration.pattern_token import PatternToken
from newspaper_restoration.trie import PrefixTrie
from newspaper_restoration.trie_node import TrieNode
from newspaper_restoration.types import WordFrequency


class TriePatternResolver:
    """Search a ``PrefixTrie`` with a small regex-like pattern language."""

    INF = 10_000_000

    def __init__(self, trie: PrefixTrie) -> None:
        """Initialise the resolver with a trie to search."""
        self.trie = trie

    def search_with_advanced_pattern(self, pattern: str) -> list[WordFrequency]:
        """Search using literals, classes, wildcards, and quantifiers.

        Supported syntax:
            ``*`` matches one character, ``[abc]`` matches one character from a
            class, ``[a-z]`` supports ranges, ``+`` repeats the previous token
            one or more times, ``-`` makes it optional, and ``{n,m}`` sets a
            bounded repetition count.
        """
        tokens = self._parse_pattern(pattern.lower().strip())
        if tokens is None:
            print("Invalid pattern.")
            return []

        matches: list[WordFrequency] = []
        memo: set[tuple[int, int, int, bool]] = set()

        def dfs(node: TrieNode, token_index: int, used: int, path: str) -> None:
            if token_index == len(tokens):
                if node.is_end_of_word:
                    matches.append((path, node.frequency))
                return

            key = (id(node), token_index, used, node.is_end_of_word)
            if key in memo:
                return
            memo.add(key)

            token = tokens[token_index]

            if used >= token.minimum:
                dfs(node, token_index + 1, 0, path)

            if used < token.maximum:
                for char, child in sorted(node.children.items()):
                    if token.matcher(char):
                        dfs(child, token_index, used + 1, path + char)

        dfs(self.trie.root, 0, 0, "")
        matches.sort(key=lambda item: (-item[1], item[0]))
        return matches

    def _parse_pattern(self, pattern: str) -> list[PatternToken] | None:
        """Parse a pattern string into executable tokens."""
        tokens: list[PatternToken] = []
        index = 0

        def push_literal(char: str) -> None:
            tokens.append(PatternToken(lambda candidate, literal=char: candidate == literal))

        while index < len(pattern):
            char = pattern[index]

            if char == "\\" and index + 1 < len(pattern):
                push_literal(pattern[index + 1])
                index += 2
                continue

            if char == "*":
                tokens.append(PatternToken(lambda _candidate: True))
                index += 1
                continue

            if char == "[":
                close_index = pattern.find("]", index + 1)
                if close_index == -1:
                    print("Error: unmatched '[' in pattern.")
                    return None
                characters = self._expand_class(pattern[index + 1 : close_index])
                tokens.append(PatternToken(lambda candidate, chars=characters: candidate in chars))
                index = close_index + 1
                continue

            if char in "+-":
                if not tokens:
                    print(f"Error: quantifier '{char}' must follow a token.")
                    return None
                token = tokens[-1]
                if char == "+":
                    token.minimum = 1
                    token.maximum = self.INF
                else:
                    token.minimum = 0
                    token.maximum = 1
                index += 1
                continue

            if char == "{":
                close_index = pattern.find("}", index + 1)
                if close_index == -1 or not tokens:
                    print("Error: invalid or unmatched '{' in quantifier.")
                    return None

                try:
                    minimum, maximum = self._parse_quantifier(pattern[index + 1 : close_index])
                except ValueError:
                    print("Error: invalid quantifier.")
                    return None

                if minimum > maximum:
                    print("Error: min > max in quantifier.")
                    return None
                tokens[-1].minimum = minimum
                tokens[-1].maximum = maximum
                index = close_index + 1
                continue

            push_literal(char)
            index += 1

        return tokens or None

    def _expand_class(self, value: str) -> set[str]:
        """Expand a character class such as ``a-z`` into a set."""
        expanded: set[str] = set()
        index = 0
        while index < len(value):
            if index + 2 < len(value) and value[index + 1] == "-":
                start = ord(value[index])
                end = ord(value[index + 2])
                if start > end:
                    start, end = end, start
                for code_point in range(start, end + 1):
                    expanded.add(chr(code_point))
                index += 3
            else:
                expanded.add(value[index])
                index += 1
        return expanded

    def _parse_quantifier(self, value: str) -> tuple[int, int]:
        """Parse ``{n}``, ``{n,m}``, or ``{n-m}`` quantifiers."""
        normalized = value.replace("-", ",")
        if "," in normalized:
            start_text, end_text = (normalized.split(",", 1) + [""])[:2]
            minimum = int(start_text) if start_text else 0
            maximum = int(end_text) if end_text else self.INF
        else:
            minimum = maximum = int(normalized)
        return minimum, maximum
