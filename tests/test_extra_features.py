"""Tests for advanced trie features that do not require opening plots."""

from __future__ import annotations

from newspaper_restoration.extra_features import FuzzySearcher, TrieBatchEditor, TriePatternResolver
from newspaper_restoration.trie import PrefixTrie


def make_feature_trie() -> PrefixTrie:
    """Create a trie with words useful for advanced feature tests."""
    trie = PrefixTrie()
    for word, frequency in [
        ("cat", 5),
        ("cot", 4),
        ("cut", 3),
        ("color", 2),
        ("colour", 3),
        ("running", 2),
        ("ringing", 1),
    ]:
        trie.add_word(word, frequency)
    return trie


def test_advanced_pattern_supports_character_classes() -> None:
    """Character classes should match any listed character."""
    resolver = TriePatternResolver(make_feature_trie())

    assert resolver.search_with_advanced_pattern("c[ao]t") == [("cat", 5), ("cot", 4)]


def test_advanced_pattern_supports_optional_previous_token() -> None:
    """The '-' quantifier makes the previous token optional."""
    resolver = TriePatternResolver(make_feature_trie())

    assert resolver.search_with_advanced_pattern("colou-r") == [("colour", 3), ("color", 2)]


def test_batch_editor_can_delete_by_prefix_and_rename_by_suffix() -> None:
    """Bulk editor operations should mutate only matching words."""
    trie = make_feature_trie()
    editor = TrieBatchEditor(trie)

    assert editor.delete("cu") == 1
    assert not trie.search_word("cut")

    editor.set_mode("suffix")
    assert editor.rename_pattern("ing", "ed") == 2
    assert trie.search_word("runned")
    assert trie.search_word("ringed")


def test_fuzzy_searcher_sorts_by_distance_frequency_and_word() -> None:
    """Fuzzy search results should be stable and useful for display."""
    searcher = FuzzySearcher(make_feature_trie())

    assert searcher.search("cit", max_dist=1) == [("cat", 5, 1), ("cot", 4, 1), ("cut", 3, 1)]
