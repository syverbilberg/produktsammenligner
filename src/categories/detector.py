"""Works out which guide category a product belongs to."""
from __future__ import annotations

import re
from typing import Iterable

from src.categories.guide import BY_ID, CATEGORIES
from src.models import Category, Product
from src.text import fold

# Where a keyword was found and how much that counts. The URL subcategory
# (e.g. ".../oppvaskmaskin") is the most reliable signal.
_WEIGHT_SUBCATEGORY = 5
_WEIGHT_PRODUCT_TYPE = 4
_WEIGHT_NAME = 2
_WEIGHT_PATH = 1


def _matches(keyword: str, text: str) -> bool:
    """Keyword at a word start, so 'tv' does not match 'ventilator'.

    Short keywords (4 letters or less, e.g. 'mus', 'ipl', 'ovn') must also
    end at a word boundary, so 'mus' does not match 'musikk'.
    Both sides are folded (æøå → ae/o/a) first, because Elkjøp URLs write
    'kjokkenmaskin' while product names write 'kjøkkenmaskin'.
    """
    tail = r"(?![a-z])" if len(keyword) <= 4 else ""
    return re.search(rf"(?<![a-z]){re.escape(keyword)}{tail}", text) is not None


def _keywords(category: Category) -> set[str]:
    """Folded, de-duplicated keywords ('kjøkkenmaskin' and 'kjokkenmaskin' count once)."""
    return {fold(keyword) for keyword in category.keywords}


def score_categories(product: Product, allowed: Iterable[str] | None = None) -> list[tuple[int, Category]]:
    """Every category with its score, best first. Used by detect_category and tools/diagnose.

    A match counts more the longer the keyword is, so the most specific
    name wins: "vaskemaskin med tørketrommel" beats "vaskemaskin" +
    "tørketrommel", and "robotstøvsuger" beats "støvsuger".
    `allowed` limits the result to some category ids (the open tab).
    """
    path = fold(product.category_path)
    subcategory = path.rsplit("/", 1)[-1].replace("-", " ")
    product_type = fold(product.specs.get("Produkttype", ""))
    name = fold(product.name)
    allowed = set(allowed) if allowed is not None else None

    scored = []
    for category in CATEGORIES:
        if allowed is not None and category.id not in allowed:
            continue
        score = 0
        for keyword in _keywords(category):
            length = len(keyword)
            if _matches(keyword, subcategory):
                score += _WEIGHT_SUBCATEGORY * length
            if _matches(keyword, product_type):
                score += _WEIGHT_PRODUCT_TYPE * length
            if _matches(keyword, name):
                score += _WEIGHT_NAME * length
            if _matches(keyword, path):
                score += _WEIGHT_PATH * length
        scored.append((score, category))
    return sorted(scored, key=lambda pair: -pair[0])


def detect_category(product: Product, allowed: Iterable[str] | None = None,
                    use_hint: bool = True) -> Category | None:
    """Return the best-matching category (optionally only among `allowed` ids), or None.

    A product fetched inside a tab carries its category in `category_id`;
    that choice is used everywhere afterwards unless `use_hint` is False.
    """
    if use_hint and allowed is None and product.category_id in BY_ID:
        return BY_ID[product.category_id]
    scored = score_categories(product, allowed)
    if not scored:
        return None
    best_score, best = scored[0]
    return best if best_score > 0 else None
