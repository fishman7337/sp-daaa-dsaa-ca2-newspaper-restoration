"""Graph-building and drawing helpers for trie vocabulary."""

from __future__ import annotations

import math
import re
from collections.abc import Iterable

import matplotlib.pyplot as plt
import networkx as nx

from newspaper_restoration.trie import PrefixTrie
from newspaper_restoration.trie_node import TrieNode
from newspaper_restoration.types import WordFrequency


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
