"""Finds which product is the newer model from the product names.

Elkjøp pages rarely state a release year, but names usually carry the
generation: "Galaxy S25" vs "Galaxy S26", "iPhone 16" vs "iPhone 17",
"Pixel 9" vs "Pixel 10". When the names are identical up to one token of
the form <letters><number> with the same letters, that number is the
generation.
"""
from __future__ import annotations

import re

from src.models import Product

_MODEL_TOKEN = re.compile(r"([a-z]*)(\d{1,3})")


def _tokens(name: str) -> list[str]:
    """Lowercase words without punctuation."""
    return re.findall(r"[a-z0-9æøå]+", name.lower())


def model_generations(products: list[Product]) -> tuple[str | None, ...]:
    """Display value per product (e.g. 'S25'), or all None if not comparable."""
    token_lists = [_tokens(p.name) for p in products]
    shortest = min(len(t) for t in token_lists)
    for i in range(shortest):
        column = [tokens[i] for tokens in token_lists]
        if len(set(column)) == 1:
            continue  # same word in every name (brand, series) – keep looking
        matches = [_MODEL_TOKEN.fullmatch(token) for token in column]
        if all(matches) and len({m.group(1) for m in matches}) == 1:
            return tuple(token.upper() for token in column)
        break  # first difference is not a generation number
    return tuple(None for _ in products)
