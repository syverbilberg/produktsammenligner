"""Writes the customer-facing text: summaries, verdict and warnings."""
from __future__ import annotations

from src.categories import dimensions as d
from src.comparison.scorer import price_winner
from src.comparison.spec_matcher import find_value
from src.models import Product, SpecRow, SpecRule
from src.text import display, strip_unit

MISSING = "Ikke oppgitt"
LETTERS = "ABCD"


def kr(amount: float) -> str:
    """Format NOK with a space as thousands separator: '13 757 kr'."""
    return f"{amount:,.0f} kr".replace(",", " ")


def _label(label: str) -> str:
    """'Motorkraft (W)' → 'motorkraft', keeping names like 'RAM' and 'Wi-Fi' as they are."""
    name = strip_unit(label)
    return name if name[:2].isupper() or "-" in name.split()[0] else name[0].lower() + name[1:]


def _dims_won(rows: list[SpecRow], index: int, weights: dict[str, int]) -> list[str]:
    """Dimensions the product wins, most important first (weight > 0 only)."""
    counts: dict[str, int] = {}
    for row in rows:
        if row.winner == index and weights.get(row.rule.dimension, 0) > 0:
            counts[row.rule.dimension] = counts.get(row.rule.dimension, 0) + 1
    return sorted(counts, key=lambda dim: (-weights.get(dim, 0), -counts[dim]))


def _join(words: list[str]) -> str:
    """'a', 'a og b', 'a, b og c' – in lowercase."""
    words = [w.lower() for w in words]
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " og " + words[-1]


def _most_important(rows: list[SpecRow], weights: dict[str, int]) -> SpecRow | None:
    """The row whose dimension weighs the most."""
    return max(rows, key=lambda r: weights.get(r.rule.dimension, 0), default=None)


def product_summary(index: int, rows: list[SpecRow], products: list[Product],
                    weights: dict[str, int]) -> str:
    """2–4 sentences: who it's for, main strength, main weakness, price."""
    product = products[index]
    sentences: list[str] = []

    dims = _dims_won(rows, index, weights)
    cheapest = price_winner(products) == index
    if dims:
        extra = " og vil betale minst" if cheapest and weights.get(d.PRICE, 0) > 0 else ""
        sentences.append(f"Passer for deg som prioriterer {_join(dims[:2])}{extra}.")
    elif cheapest:
        sentences.append("Passer for deg som vil ha det rimeligste alternativet.")

    strength = _most_important([r for r in rows if r.winner == index], weights)
    if strength:
        label = _label(strength.rule.label)
        sentences.append(f"Største styrke: {label} {display(strength.values[index], strength.rule.label)}.")

    weakness = _most_important(
        [r for r in rows if r.winner is not None and r.winner != index], weights)
    if weakness:
        best = weakness.winner
        sentences.append(
            f"Svakhet: {_label(weakness.rule.label)} {display(weakness.values[index], weakness.rule.label)} "
            f"mot {display(weakness.values[best], weakness.rule.label)} på {LETTERS[best]}."
        )

    prices = [p.price for p in products if p.price]
    if product.price and len(prices) > 1:
        lowest = min(prices)
        if product.price == lowest:
            sentences.append("Billigst av produktene.")
        else:
            sentences.append(f"Koster {kr(product.price - lowest)} mer enn det billigste.")

    return " ".join(sentences) or "For lite data til å si noe tydelig om dette produktet."


def verdict(rows: list[SpecRow], products: list[Product], scores: list[float],
            weights: dict[str, int]) -> str:
    """'Velg A hvis …' per product, plus which one fits the priorities best."""
    parts: list[str] = []
    cheapest = price_winner(products)
    for index in range(len(products)):
        reasons = _dims_won(rows, index, weights)[:2]
        reason_text = _join(reasons) if reasons else ""
        if cheapest == index:
            reason_text = f"{reason_text} og lavest pris" if reason_text else "lavest mulig pris"
        if reason_text:
            parts.append(f"Velg {LETTERS[index]} hvis du prioriterer {reason_text}.")

    top = max(scores)
    leaders = [i for i, s in enumerate(scores) if s == top]
    if len(leaders) > 1:
        names = " og ".join(LETTERS[i] for i in leaders)
        parts.append(f"Ut fra kundens prioriteringer står {names} omtrent likt – personlig smak avgjør.")
    else:
        best = leaders[0]
        line = f"Ut fra kundens prioriteringer passer **{LETTERS[best]}** best"
        if cheapest is not None and cheapest != best and products[best].price:
            diff = kr(products[best].price - products[cheapest].price)
            line += f" – den koster {diff} mer enn {LETTERS[cheapest]}, men vinner på det som er viktigst"
        parts.append(line + ".")
    return " ".join(parts)


def dealbreakers(products: list[Product], charger_rule: SpecRule | None) -> list[str]:
    """Warnings that matter even outside the guide (e.g. no charger)."""
    warnings = []
    for index, product in enumerate(products):
        value = find_value(product, charger_rule, set()) if charger_rule else None
        if value and value.strip().lower().startswith("nei"):
            warnings.append(f"Produkt {LETTERS[index]} leveres uten lader.")
        if any("utgått" in v.lower() for v in product.specs.values()):
            warnings.append(f"Produkt {LETTERS[index]} kan være en utgått modell.")
    return warnings
