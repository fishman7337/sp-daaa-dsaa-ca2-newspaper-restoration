"""Tests for file utilities and trie persistence helpers."""

from __future__ import annotations

from newspaper_restoration.file_utils import FileManager
from newspaper_restoration.trie import PrefixTrie
from newspaper_restoration.trie_manager import TrieManager


def test_load_words_from_file_supports_default_frequency(tmp_path) -> None:
    """Rows without an explicit frequency are loaded with frequency one."""
    word_file = tmp_path / "words.txt"
    word_file.write_text("cat, 3\ncar\n\n", encoding="utf-8")

    assert FileManager.load_words_from_file(word_file) == [("cat", 3), ("car", 1)]


def test_trie_manager_load_resets_existing_trie(tmp_path) -> None:
    """Loading a file should replace the current trie contents."""
    trie = PrefixTrie()
    trie.add_word("old", 9)
    manager = TrieManager(trie)
    word_file = tmp_path / "words.txt"
    word_file.write_text("new, 2\n", encoding="utf-8")

    assert manager.load_trie_from_file(str(word_file))
    assert not trie.search_word("old")
    assert trie.search_word("new")
    assert trie.get_word_frequency("new") == 2


def test_save_words_to_file_round_trip(tmp_path) -> None:
    """Saved trie word lists should be loadable by the file manager."""
    trie = PrefixTrie()
    trie.add_word("cat", 3)
    trie.add_word("car", 2)
    manager = TrieManager(trie)
    output_file = tmp_path / "out" / "words.txt"

    assert manager.save_words_to_file(str(output_file))
    assert FileManager.load_words_from_file(output_file) == [("car", 2), ("cat", 3)]
