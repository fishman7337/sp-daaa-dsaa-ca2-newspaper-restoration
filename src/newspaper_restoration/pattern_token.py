"""Pattern token model used by advanced trie search."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class PatternToken:
    """One parsed token in the advanced pattern language."""

    matcher: Callable[[str], bool]
    minimum: int = 1
    maximum: int = 1
