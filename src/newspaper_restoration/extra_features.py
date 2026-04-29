"""Optional search, editing, and visualisation features for prefix tries."""

from __future__ import annotations

import math
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass

import matplotlib.pyplot as plt
import networkx as nx

from newspaper_restoration.file_utils import FileManager
from newspaper_restoration.trie import PrefixTrie, TrieNode, WordFrequency


@dataclass
class PatternToken:
    """One parsed token in the advanced pattern language."""

    matcher: Callable[[str], bool]
    minimum: int = 1
    maximum: int = 1


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


class TrieVisualizer:
    """Build and draw trie, similarity, and co-occurrence graphs."""

    def __init__(self, trie: PrefixTrie) -> None:
        """Initialise the visualiser with a trie."""
        self.trie = trie
        self.graph = nx.DiGraph()
        self.positions: dict[str, tuple[float, float]] = {}
        self.labels: dict[str, str] = {}
        self.node_map: dict[str, TrieNode] = {}
        self._next_x = 0

    def draw_trie(self) -> None:
        """Render the trie as a top-down graph."""
        self._reset_layout()
        self._build_graph(self.trie.root)

        word_nodes = [prefix for prefix, node in self.node_map.items() if node.is_end_of_word]
        non_word_nodes = [prefix for prefix in self.node_map if prefix not in word_nodes]

        xs, ys = zip(*self.positions.values(), strict=True)
        width = max(xs) - min(xs)
        depth = max(abs(y) for y in ys)
        figure_width = max(14.0, width * 2.0)
        figure_height = max(8.0, depth * 1.5)

        plt.figure(figsize=(figure_width, figure_height))
        nx.draw_networkx_nodes(
            self.graph,
            pos=self.positions,
            nodelist=non_word_nodes,
            node_size=1000,
            node_color="lightgray",
        )
        nx.draw_networkx_nodes(
            self.graph,
            pos=self.positions,
            nodelist=word_nodes,
            node_size=1000,
            node_color="skyblue",
        )
        nx.draw_networkx_edges(self.graph, pos=self.positions, arrows=False)
        nx.draw_networkx_labels(self.graph, pos=self.positions, labels=self.labels, font_size=9)

        plt.title("Prefix Trie", fontsize=14)
        plt.axis("off")
        plt.tight_layout()
        plt.show()

    def build_word_similarity_graph(
        self,
        min_similarity: float = 0.3,
        ngram: int = 3,
        top_k_per_node: int | None = None,
        use_frequency_as_weight: bool = False,
    ) -> nx.Graph:
        """Build an undirected graph of similar trie words."""
        words = self._collect_words()
        vocabulary = [word for word, _ in words]
        frequencies = dict(words)
        graph = nx.Graph()

        for word in vocabulary:
            size = math.log1p(frequencies[word]) if use_frequency_as_weight else 1.0
            graph.add_node(word, frequency=frequencies[word], size=size)

        grams = {word: self._char_ngrams(word, n=ngram) for word in vocabulary}

        for index, first_word in enumerate(vocabulary):
            scored: list[tuple[str, float]] = []
            for second_word in vocabulary[index + 1 :]:
                first_grams = grams[first_word]
                second_grams = grams[second_word]
                if not first_grams and not second_grams:
                    continue
                intersection_size = len(first_grams & second_grams)
                if intersection_size == 0:
                    continue
                similarity = intersection_size / len(first_grams | second_grams)
                if similarity >= min_similarity:
                    scored.append((second_word, similarity))

            if top_k_per_node is not None:
                scored.sort(key=lambda item: item[1], reverse=True)
                scored = scored[:top_k_per_node]

            for second_word, similarity in scored:
                graph.add_edge(first_word, second_word, weight=similarity)

        return graph

    def draw_word_similarity_graph(
        self,
        graph: nx.Graph,
        label_nodes: bool = True,
        with_pagerank: bool = True,
        k: float | None = None,
        seed: int = 42,
    ) -> None:
        """Draw a word-similarity graph using a spring layout."""
        pos = nx.spring_layout(graph, k=k, seed=seed)

        if with_pagerank and len(graph) > 0:
            pagerank = nx.pagerank(graph, weight="weight")
            sizes = [300 + 3000 * pagerank[node] for node in graph.nodes()]
        else:
            sizes = [
                300 + 300 * float(graph.nodes[node].get("size", 1.0)) for node in graph.nodes()
            ]

        weights = [graph[u][v].get("weight", 1.0) for u, v in graph.edges()]

        plt.figure(figsize=(12, 8))
        nx.draw_networkx_edges(graph, pos, width=[2.0 * weight for weight in weights], alpha=0.25)
        nx.draw_networkx_nodes(graph, pos, node_size=sizes, node_color="lightsteelblue")
        if label_nodes:
            nx.draw_networkx_labels(graph, pos, font_size=9)
        plt.title("Word Similarity Graph (char n-gram Jaccard)", fontsize=13)
        plt.axis("off")
        plt.tight_layout()
        plt.show()

    def build_cooccurrence_graph(
        self,
        texts: Iterable[str],
        window_size: int = 2,
        min_weight: int = 1,
        directed: bool = False,
        vocabulary: Iterable[str] | None = None,
    ) -> nx.Graph:
        """Build a weighted word co-occurrence graph from text documents."""
        allowed_vocabulary = set(vocabulary) if vocabulary is not None else None
        graph: nx.Graph = nx.DiGraph() if directed else nx.Graph()
        counts: dict[tuple[str, str], int] = {}
        safe_window_size = max(1, window_size)

        for text in texts:
            tokens = self._tokenize(text)
            if allowed_vocabulary is not None:
                tokens = [token for token in tokens if token in allowed_vocabulary]

            for index, first_token in enumerate(tokens):
                graph.add_node(first_token)
                end = min(len(tokens), index + 1 + safe_window_size)
                for second_token in tokens[index + 1 : end]:
                    if directed:
                        key = (first_token, second_token)
                    else:
                        key = (
                            (first_token, second_token)
                            if first_token <= second_token
                            else (second_token, first_token)
                        )
                    counts[key] = counts.get(key, 0) + 1

        for (first_token, second_token), count in counts.items():
            if count >= min_weight:
                graph.add_edge(first_token, second_token, weight=count)

        return graph

    def draw_cooccurrence_graph(
        self,
        graph: nx.Graph,
        label_nodes: bool = True,
        with_pagerank: bool = True,
        k: float | None = None,
        seed: int = 7,
    ) -> None:
        """Draw a word co-occurrence graph."""
        pos = nx.spring_layout(graph, k=k, seed=seed)
        if with_pagerank and len(graph) > 0:
            pagerank = nx.pagerank(graph, weight="weight")
            sizes = [300 + 3000 * pagerank[node] for node in graph.nodes()]
        else:
            sizes = [400] * len(graph)

        weights = [graph[u][v].get("weight", 1.0) for u, v in graph.edges()]

        plt.figure(figsize=(12, 8))
        nx.draw_networkx_edges(
            graph,
            pos,
            width=[1.0 + 0.8 * weight for weight in weights],
            alpha=0.3,
        )
        nx.draw_networkx_nodes(graph, pos, node_size=sizes, node_color="palegreen")
        if label_nodes:
            nx.draw_networkx_labels(graph, pos, font_size=9)
        plt.title("Word Co-occurrence Graph", fontsize=13)
        plt.axis("off")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def export_graphml(graph: nx.Graph, path: str) -> None:
        """Export a graph to GraphML for tools such as Gephi or Cytoscape."""
        nx.write_graphml(graph, path)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Tokenise text into lowercase alphanumeric words."""
        return [token for token in re.split(r"[^A-Za-z0-9]+", text.lower()) if token]

    @staticmethod
    def _char_ngrams(word: str, n: int = 3) -> set[str]:
        """Create character n-grams for a word."""
        if n <= 0:
            return set()

        normalized = f"^{word.lower()}$"
        return {normalized[index : index + n] for index in range(max(0, len(normalized) - n + 1))}

    @classmethod
    def _jaccard(cls, first: str, second: str, n: int = 3) -> float:
        """Compute Jaccard similarity of character n-grams."""
        first_grams = cls._char_ngrams(first, n)
        second_grams = cls._char_ngrams(second, n)
        if not first_grams and not second_grams:
            return 0.0
        union_size = len(first_grams | second_grams)
        return len(first_grams & second_grams) / union_size if union_size else 0.0

    def _collect_words(self) -> list[WordFrequency]:
        """Return all words in the trie sorted alphabetically."""
        words = self.trie.get_all_words()
        words.sort(key=lambda item: item[0])
        return words

    def _reset_layout(self) -> None:
        """Reset graph state before building a fresh visualisation."""
        self.graph = nx.DiGraph()
        self.positions = {}
        self.labels = {}
        self.node_map = {}
        self._next_x = 0

    def _build_graph(self, node: TrieNode, prefix: str = "", depth: int = 0) -> None:
        """Recursively build graph edges, labels, and positions."""
        self.node_map[prefix] = node

        if node.children:
            child_xs = []
            for char, child in sorted(node.children.items()):
                child_prefix = prefix + char
                self.graph.add_edge(prefix, child_prefix)
                self._build_graph(child, child_prefix, depth + 1)
                child_xs.append(self.positions[child_prefix][0])
            x_position = sum(child_xs) / len(child_xs)
        else:
            x_position = self._next_x
            self._next_x += 1

        y_position = -depth
        self.positions[prefix] = (x_position, y_position)
        label = prefix or "ROOT"
        if node.is_end_of_word:
            label += f" ({node.frequency})"
        self.labels[prefix] = label


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
