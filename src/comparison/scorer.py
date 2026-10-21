"""Decides the winner of each spec and adds up weighted points."""
from __future__ import annotations

import numpy as np

from src.categories import dimensions as d
from src.comparison.value_parser import (parse_energy_class, parse_max_number, parse_number,
                                         parse_rank, parse_yes)
from src.models import Product, SpecRow, SpecRule

PRICE_WEIGHT_FACTOR = 2   # a big price gap counts like two spec wins
FULL_PRICE_GAP = 0.25     # 25 % cheaper (or more) earns all price points


def to_number(rule: SpecRule, value: str | None) -> float:
    """Convert a raw value to a comparable number for this rule."""
    if rule.kind == "energy":
        return parse_energy_class(value)
    if rule.kind == "yes":
        return parse_yes(value)
    if rule.kind == "rank":
        return parse_rank(value, rule.order)
    if rule.aggregate == "max":
        return parse_max_number(value)
    return parse_number(value)


def _unique_best(numbers: list[float], lower_is_better: bool) -> int | None:
    """Index of the single best number; None if fewer than two are known or the best is shared."""
    known = [(i, n) for i, n in enumerate(numbers) if not np.isnan(n)]
    if len(known) < 2:
        return None
    best = min(n for _, n in known) if lower_is_better else max(n for _, n in known)
    winners = [i for i, n in known if n == best]
    return winners[0] if len(winners) == 1 else None


def pick_winner(rule: SpecRule, values: tuple[str | None, ...]) -> int | None:
    """Index of the product that wins this spec, or None (tie / missing / info)."""
    if rule.kind == "info":
        return None
    numbers = [to_number(rule, v) for v in values]
    return _unique_best(numbers, lower_is_better=rule.kind in ("lower", "energy", "rank"))


def price_winner(products: list[Product]) -> int | None:
    """Index of the single cheapest product, or None."""
    prices = [p.price if p.price is not None else np.nan for p in products]
    return _unique_best(prices, lower_is_better=True)


def price_points(products: list[Product], weight: int) -> list[float]:
    """Price points scaled by how much cheaper each product is than the most expensive.

    A product 25 % cheaper or more gets the full weight × 2; a product only
    9 % cheaper gets about a third of that. So a small saving no longer
    outweighs a clearly better product.
    """
    prices = [p.price for p in products]
    known = [p for p in prices if p]
    if len(known) < 2 or weight == 0:
        return [0.0] * len(products)
    most_expensive = max(known)
    points = []
    for price in prices:
        if not price:
            points.append(0.0)
            continue
        saving = (most_expensive - price) / most_expensive
        points.append(weight * PRICE_WEIGHT_FACTOR * min(1.0, saving / FULL_PRICE_GAP))
    return points


def score(rows: list[SpecRow], products: list[Product], weights: dict[str, int]) -> list[float]:
    """Each spec win gives the weight of its dimension; price is scaled by the gap."""
    points = price_points(products, weights.get(d.PRICE, 0))
    for row in rows:
        if row.winner is not None:
            points[row.winner] += weights.get(row.rule.dimension, 0)
    return [round(p, 1) for p in points]
