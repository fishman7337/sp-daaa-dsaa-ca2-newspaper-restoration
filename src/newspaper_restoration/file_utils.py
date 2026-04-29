"""File utilities for keyword lists, trie dumps, and text restoration."""

from __future__ import annotations

from pathlib import Path

from newspaper_restoration.displayable_trie import DisplayableTrie
from newspaper_restoration.types import WordFrequency


class FileManager:
    """Handle all disk I/O for the restoration system."""

    @staticmethod
    def save_trie_structure_str(structure: str, filename: str | Path) -> bool:
        """Write an already formatted trie dump to a file."""
        return FileManager.write_text_file(filename, structure)

    @staticmethod
    def save_trie_structure(trie: DisplayableTrie, filename: str | Path) -> bool:
        """Write the current trie structure to a file.

        Args:
            trie: Object exposing a ``display_trie`` method.
            filename: Output file path.

        Returns:
            ``True`` when the file is written successfully.
        """
        return FileManager.write_text_file(filename, trie.display_trie())

    @staticmethod
    def load_words_from_file(filename: str | Path) -> list[WordFrequency]:
        """Load ``word, frequency`` rows from a UTF-8 text file.

        Blank lines are ignored. Lines without a comma are treated as words
        with frequency ``1``.
        """
        path = Path(filename)
        words: list[WordFrequency] = []

        try:
            with path.open("r", encoding="utf-8") as file:
                for line_number, raw_line in enumerate(file, start=1):
                    parsed = FileManager._parse_word_line(raw_line)
                    if parsed is None:
                        continue
                    word, frequency = parsed
                    if frequency < 1:
                        print(f"Skipping line {line_number}: frequency must be at least 1")
                        continue
                    words.append((word, frequency))
        except OSError as exc:
            print(f"Error loading from file: {exc}")

        return words

    @staticmethod
    def save_words_to_file(words: list[WordFrequency], filename: str | Path) -> bool:
        """Save words and frequencies as ``word, frequency`` rows."""
        content = "".join(f"{word}, {frequency}\n" for word, frequency in words)
        return FileManager.write_text_file(filename, content)

    @staticmethod
    def read_text_file(filename: str | Path) -> str | None:
        """Read UTF-8 text from a file.

        Returns:
            File contents, or ``None`` when reading fails.
        """
        path = Path(filename)
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Error reading file: {exc}")
            return None

    @staticmethod
    def write_text_file(filename: str | Path, content: str) -> bool:
        """Write UTF-8 text to a file, creating parent directories as needed."""
        path = Path(filename)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return True
        except OSError as exc:
            print(f"Error writing file: {exc}")
            return False

    @staticmethod
    def file_exists(filename: str | Path) -> bool:
        """Return whether ``filename`` exists on disk."""
        return Path(filename).exists()

    @staticmethod
    def _parse_word_line(raw_line: str) -> WordFrequency | None:
        """Parse one keyword-list row."""
        line = raw_line.strip()
        if not line:
            return None

        if "," not in line:
            return line, 1

        word_part, frequency_part = line.split(",", 1)
        word = word_part.strip()
        if not word:
            return None

        frequency_text = frequency_part.strip()
        frequency = int(frequency_text) if frequency_text else 1
        return word, frequency
