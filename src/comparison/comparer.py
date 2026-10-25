"""Orchestrates a full comparison of 2–4 products."""
from __future__ import annotations

import numpy as np

from src.categories import detect_category
from src.categories import dimensions as d
from src.categories.guide import CHARGER, GENERATION
from src.comparison import summarizer
from src.comparison import fallback_extractor
from src.comparison.model_facts import MODEL_SOURCE, fact
from src.comparison.generation import model_generations
from src.comparison.scorer import pick_winner, score
from src.comparison.value_parser import parse_max_number
from src.comparison.spec_matcher import find_value, select_rules
from src.models import Category, ComparisonResult, Product, SpecRow, SpecRule


def value_for(product: Product, rule: SpecRule, used: set[str]) -> tuple[str | None, str]:
    """Spec table first; then the product name and description (Elkjøp's own text about this exact
    product); last the manufacturer's model overview (src/comparison/model_facts.py).

    For max-type rules (e.g. charging watt) every source is read and the
    highest number wins, so "10 W" in the table never hides "45 W" in the text.
    """
    value = find_value(product, rule, used)
    if rule.aggregate == "max":
        candidates = ([(value, "")] if value is not None else []) + fallback_extractor.extract_all(product, rule.key)
        candidates = [(v, s) for v, s in candidates if not np.isnan(parse_max_number(v))]
        if not candidates:
            return None, ""
        return max(candidates, key=lambda pair: parse_max_number(pair[0]))
    if value is not None:
        return value, ""
    found = fallback_extractor.extract(product, rule.key)
    if found[0] is not None:
        return found
    known = fact(product, rule.key)            # manufacturer's model overview (toothbrushes, phone chips)
    return (known, MODEL_SOURCE) if known is not None else (None, "")


def _names_have_generations(categories: list[Category | None]) -> bool:
    """Only read generations from names where numbers mean generations (not size),
    and only within one category – "Galaxy S26" vs "Galaxy Tab S10" is not a generation step."""
    first = categories[0]
    return first is not None and first.name_generations and all(c is not None and c.id == first.id for c in categories)


def build_rows(products: list[Product]) -> tuple[list[SpecRow], list[str], list[Category | None]]:
    """Match guide rules to every product. Returns (rows, notes, categories).

    Rows where no product has a value are dropped; a value missing on some
    products is kept and shown as "Ikke oppgitt".
    """
    categories = [detect_category(p) for p in products]
    rules, notes = select_rules(categories)
    used: list[set[str]] = [set() for _ in products]
    rows = []
    generations = model_generations(products) if _names_have_generations(categories) else ()
    if any(generations):
        rows.append(SpecRow(GENERATION, generations, pick_winner(GENERATION, generations)))
    for rule in rules:
        found = [value_for(p, rule, used[i]) for i, p in enumerate(products)]
        values = tuple(value for value, _ in found)
        if all(v is None for v in values):
            continue
        sources = tuple(source for _, source in found)
        rows.append(SpecRow(rule, values, pick_winner(rule, values), sources))
    return rows, notes, categories


def relevant_dimensions(products: list[Product]) -> list[str]:
    """Priorities to ask about: price, every dimension with a comparable row,
    and the category's always_ask dimensions (e.g. camera for phones).
    Dimensions the category does not use at all are never asked."""
    rows, _, categories = build_rows(products)
    used = {row.rule.dimension for row in rows if row.rule.kind != "info"}
    shared = categories[0] if categories[0] and all(c == categories[0] for c in categories) else None
    if shared:
        used |= set(shared.always_ask)
        used &= {r.dimension for r in shared.rules} | set(shared.always_ask)
    return [d.PRICE] + [dim for dim in d.ALL if dim in used and dim != d.PRICE]


def compare(products: list[Product], weights: dict[str, int]) -> ComparisonResult:
    """Run the whole comparison with the customer's priority weights."""
    products = list(products)
    rows, notes, categories = build_rows(products)
    scores = score(rows, products, weights)
    return ComparisonResult(
        products=products,
        categories=categories,
        rows=rows,
        scores=scores,
        summaries=[summarizer.product_summary(i, rows, products, weights) for i in range(len(products))],
        verdict=summarizer.verdict(rows, products, scores, weights),
        warnings=notes + summarizer.dealbreakers(products, CHARGER),
    )
