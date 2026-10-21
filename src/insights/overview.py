"""Side-by-side overview for products that can't be compared (phone vs robot vacuum).

Each product is described on its own terms – its own category's key specs
and features – with no winners, scores or "velg X". Useful when a customer
is choosing between two purchases with the same budget.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.categories import detect_category
from src.categories.guide import UNIVERSAL_RULES
from src.comparison.comparer import value_for
from src.insights.features import included_items
from src.insights.names import short_names
from src.insights.phrasing import has, name_of, shown

_MAX_SPECS = 8
_MAX_FEATURES = 8


@dataclass
class ProductOverview:
    """One product described on its own.

    Attributes:
        product: The product.
        short_name: Short display name.
        category_name: Detected category, e.g. "Mobiltelefoner".
        specs: (label, value) for the category's key specs found on the page.
        features: Features the product has ("Trådløs lading", "Moppefunksjon" …).
        included: What comes in the box.
    """

    product: object
    short_name: str
    category_name: str
    specs: list[tuple[str, str]] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    included: list[str] = field(default_factory=list)


def build_overview(products: list) -> list[ProductOverview]:
    """Overview per product, using only its own category's guide."""
    names = short_names([p.name for p in products])
    overviews = []
    for product, name in zip(products, names):
        category = detect_category(product)
        overview = ProductOverview(product, name, category.name if category else "Ukjent produkttype",
                                   included=included_items(product))
        rules = list(category.rules) + list(UNIVERSAL_RULES) if category else []
        used: set[str] = set()
        for rule in rules:
            value, _ = value_for(product, rule, used)
            if value is None:
                continue
            if rule.kind == "yes":
                if has(value) and len(overview.features) < _MAX_FEATURES:
                    overview.features.append(name_of(rule))
            elif len(overview.specs) < _MAX_SPECS:
                overview.specs.append((name_of(rule), shown(rule, value)))
        overviews.append(overview)
    return overviews
