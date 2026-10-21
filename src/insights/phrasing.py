"""Turns compared spec rows into short Norwegian phrases.

Kept separate so all wording lives in one place and is easy to adjust.
"""
from __future__ import annotations

import re

from src.comparison.value_parser import parse_yes
from src.models import SpecRow, SpecRule
from src.text import display, strip_unit

# Names that keep their capital letter mid-sentence.
_KEEP_CASE = re.compile(r"^(wi-?fi|nfc|hdmi|thunderbolt|usb|esim|5g|4g|lte|gps|ekg|hepa|dolby|dts|airplay|"
                        r"chromecast|bluetooth|ip|vrr|led|oled|ram|ssd|dpi|nofrost|anc|spo2)", re.IGNORECASE)

# Rules where a yes/no reads better with its own wording: key → (has it, lacks it).
_YES_NO_WORDING = {
    "charger": ("Lader følger med", "Lader følger ikke med"),
}


def lower_first(text: str) -> str:
    """'Integrert vekt' → 'integrert vekt', but 'Wi-Fi' and 'NFC' stay as they are."""
    if not text or _KEEP_CASE.match(text):
        return text
    return text[0].lower() + text[1:]


def name_of(rule: SpecRule) -> str:
    """Rule label without unit: 'Motorkraft (W)' → 'Motorkraft'."""
    return strip_unit(rule.label)


def shown(rule: SpecRule, value: str | None) -> str:
    """Value as shown to the customer, with unit: '1600' → '1600 W', '5.5' → '5,5 liter'."""
    return display(value, rule.label)


def has(value: str | None) -> bool:
    """True for "Ja", "Ja, med tilbehør" and descriptive values like "Vibrerende"."""
    return value is not None and parse_yes(value) > 0


def detail(value: str | None) -> str:
    """Extra info in a yes-value: "Ja, med tilbehør" → "med tilbehør", "Vibrerende" → "Vibrerende"."""
    if not has(value):
        return ""
    text = value.strip()
    if text.lower().startswith("ja"):
        return text[2:].lstrip(" ,.–-:")
    return text


def mentioned_only_by(row: SpecRow) -> list[int]:
    """For yes/no rows: products that have it when the rest say nothing (not "Nei")."""
    if row.rule.kind != "yes":
        return []
    yes = [i for i, v in enumerate(row.values) if has(v)]
    others_silent = all(v is None for i, v in enumerate(row.values) if i not in yes)
    return yes if yes and others_silent and len(yes) < len(row.values) else []


def stated_only_by(row: SpecRow) -> int | None:
    """Index of the one product that states a number/text the others leave out.

    Only for kinds where a value is informative on its own (higher, rank,
    info). "Lower is better" values (noise, weight) are not an advantage
    just because they are stated.
    """
    if row.rule.kind not in ("higher", "rank", "info") or row.winner is not None:
        return None
    known = [i for i, v in enumerate(row.values) if v is not None]
    return known[0] if len(known) == 1 else None


def has_feature(rule: SpecRule, present: bool) -> str:
    """'Integrert vekt' / 'Mangler integrert vekt'."""
    if rule.key in _YES_NO_WORDING:
        return _YES_NO_WORDING[rule.key][0 if present else 1]
    return name_of(rule) if present else f"Mangler {lower_first(name_of(rule))}"


def win_phrase(row: SpecRow, index: int, names: list[str]) -> str:
    """Advantage for product `index`, e.g. 'Motorkraft: 1600 W (mot 1200 W)'."""
    if row.rule.kind == "yes":
        partial = [detail(v) for i, v in enumerate(row.values) if i != index and has(v) and parse_yes(v) < 1]
        return f"{name_of(row.rule)} følger med" if partial else has_feature(row.rule, True)
    others = [shown(row.rule, v) for i, v in enumerate(row.values) if i != index and v is not None]
    against = f" (mot {others[0]})" if len(others) == 1 else " (best av alle)"
    return f"{name_of(row.rule)}: {shown(row.rule, row.values[index])}{against}"


def loss_phrase(row: SpecRow, index: int, names: list[str]) -> str:
    """Disadvantage for product `index`, e.g. 'Motorkraft: 1200 W (Bosch Series 6 har 1600 W)'."""
    if row.rule.kind == "yes":
        extra = detail(row.values[index])
        return f"{name_of(row.rule)}: {extra}" if extra else has_feature(row.rule, False)
    best = row.winner
    return (f"{name_of(row.rule)}: {shown(row.rule, row.values[index])} "
            f"({names[best]} har {shown(row.rule, row.values[best])})")


def fact(row: SpecRow, names: list[str]) -> str:
    """Neutral one-liner for a scenario, e.g. 'motorkraft 1600 W mot 1200 W'."""
    label = lower_first(name_of(row.rule))
    if row.rule.kind == "yes":
        holders = [names[i] for i, v in enumerate(row.values) if has(v)]
        partial = [f"{names[i]} {detail(v)}" for i, v in enumerate(row.values) if has(v) and parse_yes(v) < 1]
        if partial:
            return f"{label}: " + "; ".join(partial)
        if mentioned_only_by(row):
            return f"bare {' og '.join(holders)} nevner {label}"
        if holders and len(holders) < len(row.values):
            return f"bare {' og '.join(holders)} har {label}"
        return f"begge har {label}" if holders else f"ingen oppgir {label}"
    known = [(i, v) for i, v in enumerate(row.values) if v is not None]
    if len(known) == 1:
        i, v = known[0]
        return f"{label} {shown(row.rule, v)} (bare oppgitt for {names[i]})"
    if len({v for _, v in known}) == 1:
        return f"{'begge' if len(known) == 2 else 'alle'} har {label} {shown(row.rule, known[0][1])}"
    return f"{label} " + " mot ".join(shown(row.rule, v) for _, v in known)
