"""The yes/no feature matrix and "what's in the box".

Two sources, so nothing the page says is lost:
1. Guide rules of kind "yes" (incl. features found in the description,
   e.g. "Integrert vekt" for kitchen machines).
2. Any other spec on the page whose value is "Ja"/"Nei" (e.g. Bosch's
   "Isknusingsfunksjon: Ja"), so the matrix also covers specs the guide
   doesn't know about yet.
"""
from __future__ import annotations

import re

from src.comparison.spec_matcher import find_value
from src.insights.phrasing import detail
from src.models import FeatureRow, Product, SpecRow, SpecRule

_INCLUDED = re.compile(r"^(?P<item>.+?) inkludert$", re.IGNORECASE)
_YES = re.compile(r"^\s*(ja|yes)\b", re.IGNORECASE)
_NO = re.compile(r"^\s*(nei|no)\b", re.IGNORECASE)
_MAX_ROWS = 20


def _as_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    if _YES.match(value):
        return True
    if _NO.match(value):
        return False
    return True  # descriptive value ("Pyrolyse") means the feature is there


def consumed_labels(product: Product, rules: list[SpecRule]) -> set[str]:
    """Page labels already used by a guide rule (so they are not listed twice)."""
    used: set[str] = set()
    for rule in rules:
        find_value(product, rule, used)
    return used


def feature_rows(products: list[Product], rows: list[SpecRow], rules: list[SpecRule]) -> list[FeatureRow]:
    """Yes/no features across all products; differing ones first."""
    features = [
        FeatureRow(row.rule.label, tuple(_as_bool(v) for v in row.values),
                   next((s for s in row.sources if s), ""), tuple(detail(v) for v in row.values))
        for row in rows if row.rule.kind == "yes"
    ]

    used = [consumed_labels(p, rules) for p in products]
    extra_labels: list[str] = []
    for product, consumed in zip(products, used):
        for label, value in product.specs.items():
            is_yes_no = _YES.match(value) or _NO.match(value)
            if is_yes_no and label not in consumed and not _INCLUDED.match(label) and label not in extra_labels:
                extra_labels.append(label)
    for label in extra_labels:
        raw = [p.specs.get(label) for p in products]
        values = tuple(_as_bool(v) for v in raw)
        if any(values):  # "Nutriblender: Nei" on its own tells the customer nothing
            features.append(FeatureRow(label, values, "", tuple(detail(v) for v in raw)))

    rank = {True: 0, False: 1}
    features.sort(key=lambda f: (rank[f.differs], 0 if all(f.values) else 1))
    return features[:_MAX_ROWS]


def included_items(product: Product) -> list[str]:
    """'Bolle inkludert: Ja' → 'Bolle'."""
    items = []
    for label, value in product.specs.items():
        match = _INCLUDED.match(label)
        if match and _YES.match(value):
            items.append(match.group("item"))
    return items
