"""Innsikt: the "Funksjoner og bruk" tab – features, use cases, pros/cons.

Works on the same compared rows as the recommendation, but needs no
customer priorities, so it can be shown as soon as products are fetched.
"""
from __future__ import annotations

from src.comparison.comparer import build_rows
from src.comparison.spec_matcher import select_rules
from src.insights.features import feature_rows, included_items
from src.insights.names import short_names
from src.insights.pros_cons import choose_texts, pros_and_cons
from src.insights.use_cases import evaluate
from src.models import Insights, Product

_MAX_DIFFERENCES = 12


def build_insights(products: list[Product]) -> Insights:
    """Everything the "Funksjoner og bruk" tab needs, for 2–4 products."""
    products = list(products)
    names = short_names([p.name for p in products])
    rows, _, categories = build_rows(products)
    rules, _ = select_rules(categories)

    differences = [
        row for row in rows
        if row.rule.kind != "yes" and len({v for v in row.values}) > 1
    ][:_MAX_DIFFERENCES]
    features = feature_rows(products, rows, rules)
    scenarios = evaluate(categories, rows, names)
    pros, cons = pros_and_cons(products, names, rows, features)

    return Insights(
        products=products,
        short_names=names,
        differences=differences,
        features=features,
        included=[included_items(p) for p in products],
        scenarios=scenarios,
        pros=pros,
        cons=cons,
        choose=choose_texts(products, names, scenarios, rows),
    )


__all__ = ["build_insights"]
