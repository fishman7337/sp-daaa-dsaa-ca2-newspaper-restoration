"""Text processing utilities for restoring OCR-damaged newspaper copy."""

from __future__ import annotations

import re
from typing import Any

from newspaper_restoration.file_utils import FileManager
from newspaper_restoration.trie import PrefixTrie, WordFrequency


class TextProcessor:
    """Restore damaged words by looking up wildcard patterns in a trie."""

    def __init__(self, trie: PrefixTrie) -> None:
        """Initialise the processor with a trie-backed vocabulary."""
        self.trie = trie

    def extract_words_from_text(self, text: str) -> list[str]:
        """Split text into whitespace-delimited words."""
        return text.split()

    def clean_word_for_matching(self, word: str) -> str:
        """Keep only alphabetic characters and wildcard markers from a word."""
        return "".join(char for char in word if char.isalpha() or char == "*")

    def restore_word_with_best_match(self, word: str) -> str:
        """Replace one damaged word with the highest-frequency trie match.

        The replacement is wrapped in angle brackets to make restored text easy
        to audit.
        """
        clean_word = self.clean_word_for_matching(word)

        if "*" not in clean_word:
            return word

        match = self.trie.get_best_match(clean_word)
        if match:
            cased_match = self._apply_case(clean_word, match)
            return word.replace(clean_word, f"<{cased_match}>")

        return word.replace(clean_word, "<>")

    def restore_word_with_all_matches(self, word: str) -> str:
        """Replace one damaged word with all possible trie matches."""
        clean_word = self.clean_word_for_matching(word)

        if "*" not in clean_word:
            return word

        matches = self.trie.find_matching_words(clean_word)
        if matches:
            match_list = "[" + ",".join(f"'{match}'" for match, _ in matches) + "]"
            return word.replace(clean_word, match_list)

        return word.replace(clean_word, "[]")

    def restore_text_from_file(
        self,
        input_filename: str,
        output_filename: str,
        use_best_match: bool = True,
    ) -> bool:
        """Restore damaged words from a file while preserving whitespace.

        Args:
            input_filename: Input text file containing words with ``*`` gaps.
            output_filename: Destination text file for restored output.
            use_best_match: Use only the highest-frequency match when true;
                otherwise list every match for each damaged word.

        Returns:
            ``True`` when the file was read and written successfully.
        """
        content = FileManager.read_text_file(input_filename)
        if content is None:
            return False

        tokens = re.split(r"(\s+)", content)
        restored_tokens = [
            token
            if not token or token.isspace()
            else self._restore_token(token, use_best_match=use_best_match)
            for token in tokens
        ]

        return FileManager.write_text_file(output_filename, "".join(restored_tokens))

    def find_words_with_pattern(self, pattern: str) -> list[WordFrequency]:
        """Find words matching a single-character wildcard pattern."""
        return self.trie.find_matching_words(pattern)

    def get_restoration_suggestions(self, word: str) -> dict[str, Any]:
        """Return restoration suggestions for a damaged word."""
        clean_word = self.clean_word_for_matching(word)

        if "*" not in clean_word:
            return {
                "original": word,
                "has_wildcards": False,
                "suggestions": [],
            }

        matches = self.trie.find_matching_words(clean_word)
        best_match = self.trie.get_best_match(clean_word)

        return {
            "original": word,
            "pattern": clean_word,
            "has_wildcards": True,
            "best_match": best_match,
            "all_matches": matches,
            "match_count": len(matches),
        }

    def _restore_token(self, token: str, use_best_match: bool) -> str:
        """Restore one token according to the selected output mode."""
        if use_best_match:
            return self.restore_word_with_best_match(token)
        return self.restore_word_with_all_matches(token)

    def _apply_case(self, pattern: str, word: str) -> str:
        """Apply the capitalisation style of ``pattern`` to ``word``."""
        if not pattern:
            return word
        if pattern.isupper():
            return word.upper()
        if pattern[0].isupper():
            return word.capitalize()
        return word
