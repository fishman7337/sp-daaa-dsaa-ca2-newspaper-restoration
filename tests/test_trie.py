"""Tests for the prefix trie data structure."""

from __future__ import annotations

import pytest

from newspaper_restoration.trie import PrefixTrie


def make_sample_trie() -> PrefixTrie:
    """Create a trie with a small deterministic vocabulary."""
    trie = PrefixTrie()
    for word, frequency in [
        ("cat", 3),
        ("car", 2),
        ("card", 1),
        ("care", 1),
        ("dog", 2),
        ("do", 3),
        ("dot", 1),
        ("dove", 1),
        ("rain", 5),
        ("rainbow", 2),
    ]:
        trie.add_word(word, frequency)
    return trie


def test_add_search_and_frequency_are_case_insensitive() -> None:
    """Words are normalised before insertion and lookup."""
    trie = PrefixTrie()

    trie.add_word("Cat", 2)
    trie.add_word(" cat ", 3)

    assert trie.search_word("CAT")
    assert trie.get_word_frequency("cat") == 5
    assert trie.word_count == 1


def test_add_rejects_non_positive_frequency() -> None:
    """Invalid frequencies should not silently corrupt trie statistics."""
    trie = PrefixTrie()

    with pytest.raises(ValueError, match="frequency"):
        trie.add_word("cat", 0)


def test_delete_preserves_shared_prefix_nodes() -> None:
    """Deleting one word must not delete other words sharing its prefix."""
    trie = make_sample_trie()

    assert trie.delete_word("car") is True

    assert not trie.search_word("car")
    assert trie.search_word("card")
    assert trie.search_word("care")
    assert trie.word_count == 9


def test_wildcard_matches_exactly_one_character_and_sorts_deterministically() -> None:
    """The assignment wildcard syntax uses one asterisk per unknown character."""
    trie = make_sample_trie()
    trie.add_word("can", 2)

    assert trie.find_matching_words("ca*") == [("cat", 3), ("can", 2), ("car", 2)]
    assert trie.find_matching_words("ca**") == [("card", 1), ("care", 1)]


def test_best_match_uses_frequency_then_alphabetical_tiebreak() -> None:
    """Best match is stable even when several words share the same frequency."""
    trie = PrefixTrie()
    trie.add_word("bag", 1)
    trie.add_word("bad", 1)

    assert trie.get_best_match("ba*") == "bad"


def test_display_empty_trie() -> None:
    """An empty trie should have a compact display representation."""
    assert PrefixTrie().display_trie() == "[]"
