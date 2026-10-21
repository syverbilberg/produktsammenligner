"""Works out which guide category a product belongs to."""
from __future__ import annotations

import re

from src.categories.guide import CATEGORIES
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

    Both sides are folded (æøå → ae/o/a) first, because Elkjøp URLs write
    'kjokkenmaskin' while product names write 'kjøkkenmaskin'.
    """
    return re.search(rf"(?<![a-z]){re.escape(keyword)}", text) is not None


def _keywords(category: Category) -> set[str]:
    """Folded, de-duplicated keywords ('kjøkkenmaskin' and 'kjokkenmaskin' count once)."""
    return {fold(keyword) for keyword in category.keywords}


def score_categories(product: Product) -> list[tuple[int, Category]]:
    """Every category with its score, best first. Used by detect_category and tools/diagnose."""
    path = fold(product.category_path)
    subcategory = path.rsplit("/", 1)[-1].replace("-", " ")
    product_type = fold(product.specs.get("Produkttype", ""))
    name = fold(product.name)

    scored = []
    for category in CATEGORIES:
        score = 0
        for keyword in _keywords(category):
            if _matches(keyword, subcategory):
                score += _WEIGHT_SUBCATEGORY
            if _matches(keyword, product_type):
                score += _WEIGHT_PRODUCT_TYPE
            if _matches(keyword, name):
                score += _WEIGHT_NAME
            if _matches(keyword, path):
                score += _WEIGHT_PATH
        scored.append((score, category))
    return sorted(scored, key=lambda pair: -pair[0])


def detect_category(product: Product) -> Category | None:
    """Return the best-matching category, or None if nothing matches."""
    best_score, best = score_categories(product)[0]
    return best if best_score > 0 else None
