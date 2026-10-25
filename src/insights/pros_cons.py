"""Fordeler og ulemper per product, plus "Velg X hvis …"."""
from __future__ import annotations

from src.comparison.summarizer import kr
from src.insights.phrasing import (has_feature, loss_phrase, lower_first, mentioned_only_by, name_of, shown,
                                   stated_only_by, win_phrase)
from src.models import FeatureRow, Product, ScenarioResult, SpecRow

_MAX_ITEMS = 5
_GOOD_RATING, _WEAK_RATING, _MIN_REVIEWS = 4.5, 4.0, 10


def _rating_text(product: Product) -> str:
    rating = f"{product.rating:.1f}".replace(".", ",")
    return f"{rating}/5 fra {product.review_count} anmeldelser"


def pros_and_cons(products: list[Product], names: list[str], rows: list[SpecRow],
                  features: list[FeatureRow]) -> tuple[list[list[str]], list[list[str]]]:
    """Up to five advantages and disadvantages per product."""
    pros: list[list[str]] = [[] for _ in products]
    cons: list[list[str]] = [[] for _ in products]

    prices = [p.price for p in products]
    if all(prices) and len(set(prices)) > 1:
        cheapest = prices.index(min(prices))
        for i, price in enumerate(prices):
            if i == cheapest:
                gap = sorted(prices)[1] - price
                pros[i].append(f"Lavest pris ({kr(gap)} billigere enn nest billigste)" if len(prices) > 2
                               else f"Lavere pris ({kr(gap)} billigere)")
            else:
                cons[i].append(f"Dyrere ({kr(price - prices[cheapest])} mer enn {names[cheapest]})")

    for row in rows:
        for holder in mentioned_only_by(row):
            pros[holder].append(f"{has_feature(row.rule, True)} (nevnt bare for {names[holder]})")
        only = stated_only_by(row) if row.rule.kind != "info" else None   # "Plassering: Integrert" is not an advantage
        if only is not None:
            missing = " og ".join(names[i] for i, v in enumerate(row.values) if v is None)
            pros[only].append(f"{name_of(row.rule)}: {shown(row.rule, row.values[only])} (ikke oppgitt for {missing})")
        if row.winner is None:
            continue
        for i in range(len(products)):
            if i == row.winner:
                pros[i].append(win_phrase(row, i, names))
            elif row.values[i] is not None:
                cons[i].append(loss_phrase(row, i, names))

    guide_labels = {row.rule.label for row in rows}
    for feature in features:
        if feature.label in guide_labels or not feature.differs:
            continue  # guide rows are already covered above; only page-only extras here
        for i, value in enumerate(feature.values):
            if value is True and any(v is False for v in feature.values):
                pros[i].append(feature.label)
            elif value is False and any(v is True for v in feature.values):
                cons[i].append(f"Mangler {feature.label[0].lower()}{feature.label[1:]}")

    for i, product in enumerate(products):
        if product.rating and (product.review_count or 0) >= _MIN_REVIEWS:
            if product.rating >= _GOOD_RATING:
                pros[i].append(f"Svært god kundevurdering hos Elkjøp ({_rating_text(product)})")
            elif product.rating < _WEAK_RATING:
                cons[i].append(f"Svakere kundevurdering ({_rating_text(product)})")

    return [_unique(p)[:_MAX_ITEMS] for p in pros], [_unique(c)[:_MAX_ITEMS] for c in cons]


def _unique(items: list[str]) -> list[str]:
    """Drop repeats, keep order ("Dampprogram" must not be listed twice)."""
    return list(dict.fromkeys(items))


def _best_win(rows: list[SpecRow], index: int) -> SpecRow | None:
    """First guide row the product wins outright, or that only it states (numbers/text)."""
    won = [row for row in rows if row.winner == index]
    only = [row for row in rows if row.winner is None and stated_only_by(row) == index]
    return (won + only)[0] if won or only else None


def choose_texts(products: list[Product], names: list[str], scenarios: list[ScenarioResult],
                 rows: list[SpecRow] | None = None) -> list[str]:
    """'Velg Bosch Series 6 hvis du baker mye brød og tunge deiger.' per product."""
    prices = [p.price for p in products]
    cheapest = prices.index(min(prices)) if all(prices) and len(set(prices)) > 1 else None
    texts = []
    for i in range(len(products)):
        reasons = [r.scenario.choose_text for r in scenarios if r.winner == i]
        if cheapest == i:
            reasons.append("vil betale minst")
        if reasons:
            joined = reasons[0] if len(reasons) == 1 else ", ".join(reasons[:-1]) + " eller " + reasons[-1]
            texts.append(f"Velg **{names[i]}** hvis du {joined}.")
        elif rows and (best := _best_win(rows, i)) is not None:
            texts.append(f"Velg **{names[i]}** hvis {lower_first(name_of(best.rule))} er viktigst "
                         f"({shown(best.rule, best.values[i])}).")
        else:
            texts.append(f"Velg **{names[i]}** hvis du foretrekker merket eller designet – "
                         "på spesifikasjonene er forskjellen liten.")
    return texts


__all__ = ["choose_texts", "has_feature", "pros_and_cons"]
