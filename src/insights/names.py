"""Short, readable product names: 'Bosch Series 6 kjøkkenmaskin MUMS6ZS18 (sort)' → 'Bosch Series 6'."""
from __future__ import annotations

import re

from src.categories.guide import CATEGORIES
from src.text import fold

# Words that start the "what it is" part of an Elkjøp name.
_TYPE_WORDS = {fold(k) for c in CATEGORIES for k in c.keywords} | {
    "smarttelefon", "barbar", "pc", "kjokkenmaskin", "tv", "smart", "oppvaskmaskin", "vaskemaskin",
}
_MAX_WORDS = 5


_STOP = re.compile(r"^(4k|8k|uhd|smart|5g|\d+(gb|tb)|\d+/\d+.*)$", re.IGNORECASE)
_SIZE = re.compile(r'^\d{1,3}(?:[.,]\d)?("|”|\'\')$')


def short_name(name: str) -> str:
    """Cut the name before the product-type word, colour and specs.

    Elkjøp writes the type in lowercase ("kjøkkenmaskin", "smarttelefon",
    "bærbar PC") while brand and series are capitalised ("Laptop", "iPhone"),
    so only lowercase type words end the name.
    """
    name = re.sub(r"\s*\([^)]*\)\s*$", "", name or "").strip()      # "(sort)"
    words = name.split()
    kept: list[str] = []
    for i, word in enumerate(words):
        folded = fold(word).strip(",")
        if i > 0 and word.islower() and (folded in _TYPE_WORDS or folded.startswith(("smarttelefon", "kjokken"))):
            break
        if i > 0 and ("/" in word or _STOP.match(word)):
            break
        if _SIZE.match(word):
            continue                                                  # '65"' – size, not name
        kept.append(word)
    if len(kept) == 1:
        code = next((w for w in words[1:] if any(ch.isdigit() for ch in w) and "/" not in w), None)
        if code:
            kept.append(code)                                         # "Asko" + model code
    return " ".join(kept[:_MAX_WORDS]) or name


def short_names(names: list[str]) -> list[str]:
    """Short names, falling back to full names when two would look identical."""
    shorts = [short_name(n) for n in names]
    return shorts if len(set(shorts)) == len(shorts) else names
