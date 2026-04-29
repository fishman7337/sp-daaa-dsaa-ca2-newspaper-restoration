"""Compatibility exports for optional trie feature classes."""

from __future__ import annotations

from newspaper_restoration.fuzzy_searcher import FuzzySearcher
from newspaper_restoration.pattern_token import PatternToken
from newspaper_restoration.trie_batch_editor import TrieBatchEditor
from newspaper_restoration.trie_pattern_resolver import TriePatternResolver
from newspaper_restoration.trie_visualizer import TrieVisualizer

__all__ = [
    "FuzzySearcher",
    "PatternToken",
    "TrieBatchEditor",
    "TriePatternResolver",
    "TrieVisualizer",
]
