"""Command processors that connect menu input to trie business logic."""

from __future__ import annotations

from newspaper_restoration.extra_features import (
    FuzzySearcher,
    TrieBatchEditor,
    TriePatternResolver,
    TrieVisualizer,
)
from newspaper_restoration.file_utils import FileManager
from newspaper_restoration.text_processor import TextProcessor
from newspaper_restoration.trie import PrefixTrie
from newspaper_restoration.trie_manager import TrieManager


class TrieProcessor:
    """Handle command panels for construction, restoration, and extra features."""

    def __init__(self, trie: PrefixTrie) -> None:
        """Initialise feature managers around one shared trie."""
        self.trie = trie
        self.trie_manager = TrieManager(trie)
        self.text_processor = TextProcessor(trie)
        self.file_manager = FileManager()

        self.pattern = TriePatternResolver(trie)
        self.visual = TrieVisualizer(trie)
        self.editor = TrieBatchEditor(trie)
        self.fuzzy = FuzzySearcher(trie)

    def construct_edit_trie(self) -> None:
        """Run the command loop for editing and managing trie keywords."""
        self._print_construct_help()

        while True:
            command = input(">").strip()

            if command.startswith("+"):
                self._add_word(command[1:])
            elif command.startswith("-"):
                self._delete_word(command[1:])
            elif command.startswith("?"):
                self._search_word(command[1:])
            elif command == "#":
                print(self.trie.display_trie())
            elif command.startswith("@"):
                self._save_trie_structure(command[1:])
            elif command.startswith("~"):
                self._load_trie_structure(command[1:])
            elif command.startswith("="):
                self._save_word_list(command[1:])
            elif command == "!":
                self._print_construct_help()
            elif command == "\\":
                print("Exiting the Edit Command Prompt. Bye...")
                self._pause()
                break
            else:
                print("Invalid command. Type ! for help.")

    def predict_restore_text(self) -> None:
        """Run the command loop for predicting and restoring damaged text."""
        self._print_restore_help()

        while True:
            command = input(">").strip()

            if command.startswith("~"):
                self._load_trie_structure(command[1:])
            elif command == "#":
                print(self.trie.display_trie())
            elif command.startswith("$"):
                self._list_matching_words(command[1:])
            elif command.startswith("?"):
                self._restore_single_word(command[1:])
            elif command == "&":
                self._restore_text(all_matches=True)
            elif command == "@":
                self._restore_text(all_matches=False)
            elif command == "!":
                self._print_restore_help()
            elif command == "\\":
                print("Exiting the Restore Command Prompt. Bye...")
                self._pause()
                break
            else:
                print("Invalid command. Type ! for help.")

    def pattern_search(self) -> None:
        """Run the advanced pattern-search panel."""
        print("\nAdvanced Pattern Search - commands: ! help, \\ exit\n")
        while True:
            command = input(">").strip()
            if command.startswith("?"):
                pattern = command[1:].strip()
                results = self.pattern.search_with_advanced_pattern(pattern)
                print(",".join(f"[{word},{freq}]" for word, freq in results) if results else "")
            elif command == "!":
                print(
                    "Syntax quick-ref:\n"
                    "  ?p*t          any single-character wildcard (*)\n"
                    "  ?p+           one or more of previous token\n"
                    "  ?colou-r      optional previous token\n"
                    "  ?c[ao]t       character class\n"
                    "  ?[a-z]{3}     exactly 3 letters\n"
                    "  ?[aeiou]{2,3} 2 to 3 vowels\n"
                )
            elif command == "\\":
                print("Exiting the Pattern Search Panel. Bye...")
                self._pause()
                break
            else:
                print("Invalid command. Type ! for help.")

    def trie_editor(self) -> None:
        """Run a command panel for prefix/suffix bulk trie operations."""
        print("\nTrie Editor Panel")
        print("Use: mode=prefix/suffix | -pattern delete | @pattern,file export | #pattern preview")
        print("~file,pattern import | =old,new rename | $pattern stats | ! help | \\ exit\n")

        while True:
            command = input(">").strip()

            if command.startswith("mode="):
                self._set_editor_mode(command[5:])
            elif command.startswith("-"):
                self._editor_delete(command[1:])
            elif command.startswith("@"):
                self._editor_export(command[1:])
            elif command.startswith("#"):
                self._editor_preview(command[1:])
            elif command.startswith("~"):
                self._editor_import(command[1:])
            elif command.startswith("="):
                self._editor_rename(command[1:])
            elif command.startswith("$"):
                self._editor_stats(command[1:])
            elif command == "!":
                self._print_editor_help()
            elif command == "\\":
                print("Exiting the Trie Editor Panel. Bye...")
                self._pause()
                break
            else:
                print("Invalid command. Type ! for help.")

    def trie_visualizer(self) -> None:
        """Run a command panel for trie and word graph visualisations."""
        print(
            "\nTrie Visualization\n"
            " #   show trie | ^ similarity graph | % co-occurrence graph\n"
            " !   help      | \\ exit\n"
        )

        while True:
            command = input("> ").strip()

            if command == "#":
                self._draw_trie()
            elif command == "^":
                self._draw_similarity_graph()
            elif command == "%":
                self._draw_cooccurrence_graph()
            elif command == "!":
                self._print_visualizer_help()
            elif command == "\\":
                print("Exiting the Trie Visualization Panel. Bye...")
                self._pause()
                break
            else:
                print("Invalid command. Type ! for help.")

    def fuzzy_search_menu(self) -> None:
        """Run an approximate-search panel using edit distance."""
        print("\nFuzzy Search Panel")
        print(" ?word[,max_dist]    search approximate matches, e.g. ?car,3")
        print(" !                   help")
        print(" \\                   exit\n")

        while True:
            command = input(">").strip()
            if command.startswith("?"):
                target, max_distance = self._parse_fuzzy_command(command[1:])
                matches = self.fuzzy.search(target, max_distance)
                if matches:
                    print(
                        ", ".join(f"{word}({distance},{freq})" for word, freq, distance in matches)
                    )
                else:
                    print("(no matches)")
            elif command == "!":
                print("Commands:")
                print("  ?word[,k]   find matches within k edits (default k=2), e.g. ?car,3")
                print("  Output: match(distance, frequency)")
                print("  !           this help")
                print("  \\           exit panel\n")
            elif command == "\\":
                print("Exiting the Fuzzy Search Panel. Bye...")
                self._pause()
                break
            else:
                print("Invalid command. Type ! for help.")

    def _add_word(self, word_input: str) -> None:
        """Add a word from command input, optionally as ``word(freq)``."""
        word = word_input.strip()
        if not word:
            print("Invalid word.")
            return

        frequency = 1
        if "(" in word and word.endswith(")"):
            try:
                word_part, frequency_part = word.rsplit("(", 1)
                word = word_part.strip()
                frequency = int(frequency_part[:-1])
            except ValueError:
                frequency = 1

        try:
            self.trie.add_word(word, frequency)
        except ValueError as exc:
            print(f"Invalid frequency: {exc}")

    def _delete_word(self, word: str) -> None:
        """Delete one word and report the outcome."""
        normalized = word.strip()
        if normalized and self.trie.delete_word(normalized):
            print(f"Deleted '{normalized}'")
        else:
            print("Word not found or cannot be deleted.")

    def _search_word(self, word: str) -> None:
        """Search for one exact keyword."""
        normalized = word.strip()
        if normalized and self.trie.search_word(normalized):
            print(f'Keyword "{normalized}" is present')
        else:
            print(f'Keyword "{normalized}" is not present')

    def _save_trie_structure(self, filename: str) -> None:
        """Save the rendered trie structure to disk."""
        output_file = filename.strip() or input("Please enter new filename: ").strip()
        if not self.trie_manager.save_trie_structure(output_file):
            print("Error saving trie.")

    def _load_trie_structure(self, filename: str) -> None:
        """Load words and frequencies from disk into the trie."""
        input_file = filename.strip() or input("Please enter filename: ").strip()
        if not self.trie_manager.load_trie_from_file(input_file):
            print("Error loading trie.")

    def _save_word_list(self, filename: str) -> None:
        """Save trie words and frequencies to disk."""
        output_file = filename.strip() or input("Please enter new filename: ").strip()
        if not self.trie_manager.save_words_to_file(output_file):
            print("Error saving word list.")

    def _list_matching_words(self, pattern: str) -> None:
        """Print all words matching a wildcard pattern."""
        search_pattern = pattern.strip() or input("Pattern with * wildcards: ").strip()
        matches = self.text_processor.find_words_with_pattern(search_pattern)
        print(",".join(f"[{word},{freq}]" for word, freq in matches) if matches else "")

    def _restore_single_word(self, pattern: str) -> None:
        """Print the best restoration for one wildcard pattern."""
        search_pattern = pattern.strip() or input("Word with * wildcards: ").strip()
        suggestion = self.text_processor.get_restoration_suggestions(search_pattern)
        best = suggestion.get("best_match")
        print(f'Restored keyword "{best}"' if best else "")

    def _restore_text(self, all_matches: bool) -> None:
        """Restore an input file into an output file."""
        input_file = input("Please enter input file: ").strip()
        output_file = input("Please enter output file: ").strip()
        success = self.text_processor.restore_text_from_file(
            input_file,
            output_file,
            use_best_match=not all_matches,
        )
        if not success:
            print("Error restoring text.")

    def _set_editor_mode(self, mode_input: str) -> None:
        """Set editor mode and report invalid options."""
        mode = mode_input.strip().lower()
        try:
            self.editor.set_mode(mode)
            print(f"Mode switched to '{mode}'")
        except ValueError as exc:
            print(f"Error: {exc}")

    def _editor_delete(self, pattern_input: str) -> None:
        """Delete words from the bulk editor panel."""
        pattern = pattern_input.strip()
        count = self.editor.delete(pattern)
        print(f"Deleted {count} words matching '{pattern}' ({self.editor.mode}-based).")

    def _editor_export(self, args_input: str) -> None:
        """Export editor preview results."""
        args = args_input.split(",", 1)
        pattern = args[0].strip()
        output_file = args[1].strip() if len(args) > 1 else input("Output filename: ").strip()
        count = self.editor.export(pattern, output_file)
        print(f"Exported {count} words matching '{pattern}' to '{output_file}'.")

    def _editor_preview(self, pattern_input: str) -> None:
        """Preview editor matches."""
        pattern = pattern_input.strip()
        words = self.editor.preview(pattern)
        if not words:
            print(f"No words found matching '{pattern}'.")
            return

        print(f"Previewing {len(words)} words matching '{pattern}' ({self.editor.mode}-based):")
        for word, freq in words:
            print(f" - {word} ({freq})")

    def _editor_import(self, args_input: str) -> None:
        """Import words into the trie through the editor panel."""
        args = args_input.split(",", 1)
        input_file = args[0].strip()
        pattern = args[1].strip() if len(args) > 1 else ""
        count = self.editor.import_with_filter(input_file, pattern)
        print(f"Imported {count} words from '{input_file}' matching '{pattern}'.")

    def _editor_rename(self, args_input: str) -> None:
        """Rename words from the editor panel."""
        if "," not in args_input:
            print("Error: use =old,new")
            return

        old, new = (part.strip() for part in args_input.split(",", 1))
        try:
            count = self.editor.rename_pattern(old, new)
            print(f"Renamed {count} words from {self.editor.mode} '{old}' to '{new}'.")
        except ValueError as exc:
            print(f"Error: {exc}")

    def _editor_stats(self, pattern_input: str) -> None:
        """Print editor statistics."""
        pattern = pattern_input.strip()
        stats = self.editor.stats(pattern)
        if not stats["num_words"]:
            print(f"No statistics found for '{pattern}'.")
            return

        print(f"Statistics for {self.editor.mode} '{pattern}':")
        print(f" - Number of words : {stats['num_words']}")
        print(f" - Average frequency: {stats['avg_frequency']:.2f}")
        print(f" - Max depth       : {stats['max_depth']}")

    def _draw_trie(self) -> None:
        """Draw the current trie and report plotting failures."""
        try:
            self.visual.draw_trie()
        except Exception as exc:  # pragma: no cover - depends on plotting backend
            print(f"Failed to draw trie: {exc}")

    def _draw_similarity_graph(self) -> None:
        """Build and draw the word-similarity graph."""
        try:
            top_k = int(input("Top-K words to include [200]: ").strip() or "200")
            min_similarity = float(input("Min similarity (0..1) [0.3]: ").strip() or "0.3")
            ngram = int(input("Char n-gram size [3]: ").strip() or "3")
            top_neighbors_raw = input("Top-K neighbors per node (blank=keep all): ").strip()
            top_k_per_node = int(top_neighbors_raw) if top_neighbors_raw else None

            graph_full = self.visual.build_word_similarity_graph(
                min_similarity=min_similarity,
                ngram=ngram,
                top_k_per_node=top_k_per_node,
                use_frequency_as_weight=True,
            )

            if top_k > 0:
                words = self.visual._collect_words()
                words.sort(key=lambda item: item[1], reverse=True)
                keep = {word for word, _ in words[:top_k]}
                graph = graph_full.subgraph(keep).copy()
            else:
                graph = graph_full

            if len(graph) == 0:
                print("No nodes to draw after filtering.")
                return

            self.visual.draw_word_similarity_graph(
                graph,
                label_nodes=True,
                with_pagerank=True,
                k=None,
                seed=42,
            )
        except ValueError:
            print("Invalid value. Top-K and n-gram must be integers; similarity must be a float.")
        except Exception as exc:  # pragma: no cover - depends on plotting backend
            print(f"Failed to draw similarity graph: {exc}")

    def _draw_cooccurrence_graph(self) -> None:
        """Build and draw a co-occurrence graph from text input or a file."""
        try:
            source = (input("Source: [t]ext / [f]ile ? ").strip() or "t").lower()
            text = self._read_graph_text(source)
            if text is None:
                return

            window_size = max(2, int(input("Sliding window size (>=2) [2]: ").strip() or "2"))
            min_weight = max(1, int(input("Min edge weight (count) [1]: ").strip() or "1"))
            restrict_raw = (input("Restrict to trie vocabulary? [y/N]: ").strip() or "n").lower()
            vocabulary = None
            if restrict_raw.startswith("y"):
                vocabulary = [word for word, _ in self.visual._collect_words()]

            graph = self.visual.build_cooccurrence_graph(
                texts=[text],
                window_size=window_size,
                min_weight=min_weight,
                directed=False,
                vocabulary=vocabulary,
            )

            if len(graph) == 0:
                print("No edges to draw after thresholding.")
                return

            self.visual.draw_cooccurrence_graph(
                graph,
                label_nodes=True,
                with_pagerank=True,
                k=None,
                seed=7,
            )
        except ValueError:
            print("Invalid value. Window and min edge weight must be integers.")
        except Exception as exc:  # pragma: no cover - depends on plotting backend
            print(f"Failed to draw co-occurrence graph: {exc}")

    def _read_graph_text(self, source: str) -> str | None:
        """Read graph source text from stdin or a file."""
        if source.startswith("f"):
            path = input("Enter file path: ").strip()
            try:
                with open(path, encoding="utf-8") as file:
                    return file.read()
            except OSError as exc:
                print(f"Could not read file: {exc}")
                return None

        print("Paste/enter text. Finish with an empty line:")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def _parse_fuzzy_command(args_input: str) -> tuple[str, int]:
        """Parse ``word[,distance]`` fuzzy-search input."""
        parts = args_input.split(",", 1)
        target = parts[0].strip()
        try:
            max_distance = int(parts[1]) if len(parts) == 2 else 2
        except ValueError:
            max_distance = 2
        return target, max(0, max_distance)

    @staticmethod
    def _print_construct_help() -> None:
        """Print instructions for trie construction commands."""
        print()
        print("-" * 72)
        print("Construct/Edit Trie Commands:")
        print("    +sunshine        add a keyword")
        print("    +sunshine(12)    add a keyword with frequency")
        print("    -moonlight       delete a keyword")
        print("    ?rainbow         find a keyword")
        print("    #                display trie")
        print("    @file.txt        write trie display to file")
        print("    ~keywords.txt    load keywords from file")
        print("    =words.txt       write keywords from trie to file")
        print("    !                print instructions")
        print("    \\                exit")
        print("-" * 72)
        print()

    @staticmethod
    def _print_restore_help() -> None:
        """Print instructions for text restoration commands."""
        print()
        print("-" * 72)
        print("Predict/Restore Text Commands:")
        print("    ~keywords.txt    read keywords from file to make trie")
        print("    #                display trie")
        print("    $ra*n*ow         list all matching keywords")
        print("    ?ra*n*ow         restore one word using the best keyword match")
        print("    &                restore a text using all matching keywords")
        print("    @                restore a text using best keyword matches")
        print("    !                print instructions")
        print("    \\                exit")
        print("-" * 72)
        print()

    @staticmethod
    def _print_editor_help() -> None:
        """Print instructions for trie editor commands."""
        print(" mode=prefix/suffix   switch between prefix/suffix mode")
        print(" -pattern             delete words matching pattern")
        print(" @pattern,file        export words matching pattern to file")
        print(" #pattern             preview matching words")
        print(" ~file,pattern        import words matching pattern")
        print(" =old,new             rename words with old to new pattern")
        print(" $pattern             show statistics for matching pattern")
        print(" \\                    exit the panel\n")

    @staticmethod
    def _print_visualizer_help() -> None:
        """Print instructions for visualisation commands."""
        print(
            "Commands:\n"
            "  #   Show trie visualization\n"
            "  ^   Show word-similarity graph from trie keywords\n"
            "  %   Show co-occurrence graph from text or file\n"
            "  \\   Exit the visualizer\n"
        )

    @staticmethod
    def _pause() -> None:
        """Wait for the user before returning to the previous menu."""
        input("\nPress enter key to continue...")
