"""Newspaper restoration tools built around prefix tries."""

from newspaper_restoration.text_processor import TextProcessor
from newspaper_restoration.trie import PrefixTrie, TrieNode
from newspaper_restoration.trie_manager import TrieManager

__all__ = ["PrefixTrie", "TextProcessor", "TrieManager", "TrieNode"]
__version__ = "0.1.0"
