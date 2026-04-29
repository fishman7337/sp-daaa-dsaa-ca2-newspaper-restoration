"""Tests for text restoration behavior."""

from __future__ import annotations

from newspaper_restoration.text_processor import TextProcessor
from newspaper_restoration.trie import PrefixTrie


def make_text_processor() -> TextProcessor:
    """Create a processor with restoration-friendly sample words."""
    trie = PrefixTrie()
    for word, frequency in [
        ("the", 5),
        ("this", 3),
        ("thus", 1),
        ("again", 2),
        ("her", 2),
        ("all", 2),
    ]:
        trie.add_word(word, frequency)
    return TextProcessor(trie)


def test_restore_word_with_best_match_preserves_punctuation_and_case() -> None:
    """Best-match output keeps punctuation and mirrors source capitalisation."""
    processor = make_text_processor()

    assert processor.restore_word_with_best_match("T*e") == "<The>"
    assert processor.restore_word_with_best_match("th*s.") == "<this>."


def test_restore_word_with_all_matches_is_deterministic() -> None:
    """All-match output lists candidates in trie ranking order."""
    processor = make_text_processor()

    assert processor.restore_word_with_all_matches("th*s") == "['this','thus']"


def test_restore_text_from_file_preserves_whitespace(tmp_path) -> None:
    """File restoration should keep original spacing and newlines."""
    processor = make_text_processor()
    input_file = tmp_path / "defect.txt"
    output_file = tmp_path / "restored.txt"
    input_file.write_text("T*e  hero\ncame a*ain.", encoding="utf-8")

    assert processor.restore_text_from_file(str(input_file), str(output_file))
    assert output_file.read_text(encoding="utf-8") == "<The>  hero\ncame <again>."


def test_get_restoration_suggestions_for_clean_word() -> None:
    """Undamaged words should not produce wildcard suggestions."""
    processor = make_text_processor()

    assert processor.get_restoration_suggestions("hello") == {
        "original": "hello",
        "has_wildcards": False,
        "suggestions": [],
    }
