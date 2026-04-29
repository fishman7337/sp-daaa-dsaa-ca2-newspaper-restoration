"""Console presentation helpers for the interactive application."""

from __future__ import annotations


class ConsoleUI:
    """Render the welcome screen and main menu for the CLI."""

    @staticmethod
    def welcome() -> None:
        """Print the application welcome banner."""
        print("\n")
        print("*" * 65)
        print("* {:<62}*".format("ST1507 DSAA: Newspaper Restoration with Tries"))
        print("*" + "-" * 63 + "*")
        print("*{:<63}*".format(""))
        print("*    {:<58}*".format("- Done by: Goh Kun Ming, DAAA Student"))
        print("*    {:<58}*".format("- Singapore Polytechnic, School of Computing"))
        print("*    {:<58}*".format("- ST1507 Data Structures & Algorithm (AI), CA2"))
        print("*{:<63}*".format(""))
        print("*" * 65)
        print("")

    @staticmethod
    def menu() -> int:
        """Prompt for the next main menu option.

        Returns:
            The selected menu number, or ``0`` when the input is not a valid
            integer.
        """
        print("\nPlease select your choice ('1','2','3','4','5','6','7'):")
        print("    1. Construct/Edit Trie")
        print("    2. Predict/Restore Text")
        print("    " + "-" * 52)
        print("    3. Advanced Pattern Search")
        print("    4. Trie Editor")
        print("    " + "-" * 52)
        print("    5. Trie Visualizer")
        print("    6. Fuzzy Searcher")
        print("    " + "-" * 52)
        print("    7. Exit")

        try:
            return int(input("Enter choice: "))
        except ValueError:
            return 0

    @staticmethod
    def exit() -> None:
        """Print a goodbye message before the app returns to the shell."""
        print("\nBye, thanks for using ST1507 DSAA: Newspaper Restoration with Tries")


GUI = ConsoleUI
