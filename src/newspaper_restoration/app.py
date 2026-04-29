"""Application entry point for the newspaper restoration CLI."""

from __future__ import annotations

from newspaper_restoration.console import ConsoleUI
from newspaper_restoration.trie import PrefixTrie
from newspaper_restoration.trie_processor import TrieProcessor


class TrieApp:
    """Coordinate menu input, trie state, and feature command panels."""

    def __init__(self, ui: ConsoleUI | None = None, processor: TrieProcessor | None = None) -> None:
        """Initialise the application with injectable UI and processor objects.

        Args:
            ui: Console UI implementation. A default ``ConsoleUI`` is created
                when one is not provided.
            processor: Business-logic command processor. A default processor
                backed by a new ``PrefixTrie`` is created when one is not
                provided.
        """
        self.ui = ui or ConsoleUI()
        self.processor = processor or TrieProcessor(PrefixTrie())

    def run(self) -> None:
        """Run the main menu loop until the user chooses to exit."""
        self.ui.welcome()

        while True:
            choice = self.ui.menu()
            try:
                if choice == 1:
                    self.processor.construct_edit_trie()
                elif choice == 2:
                    self.processor.predict_restore_text()
                elif choice == 3:
                    self.processor.pattern_search()
                elif choice == 4:
                    self.processor.trie_editor()
                elif choice == 5:
                    self.processor.trie_visualizer()
                elif choice == 6:
                    self.processor.fuzzy_search_menu()
                elif choice == 7:
                    self.ui.exit()
                    return
                else:
                    print("Please enter a valid option.")
            except Exception as exc:  # pragma: no cover - defensive CLI guard
                print(f"An unexpected error occurred: {exc}")


def main() -> None:
    """Start the interactive newspaper restoration application."""
    TrieApp().run()
