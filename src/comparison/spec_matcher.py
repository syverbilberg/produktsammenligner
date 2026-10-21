"""Finds the page value for a guide rule, and picks which rules to use."""
from __future__ import annotations

import re

from src.categories.compatibility import SAME, UNKNOWN, UNRELATED, check
from src.categories.guide import CATEGORIES, UNIVERSAL_RULES
from src.comparison.value_parser import fit, parse_max_number
from src.models import Category, Product, SpecRule
from src.text import with_unit


def matching_labels(product: Product, rule: SpecRule, used: set[str]) -> list[str]:
    """Labels matching the rule, in pattern order (then page order), skipping used ones."""
    lowered = [(label, label.lower()) for label in product.specs if label not in used]
    found: list[str] = []
    for pattern in rule.patterns:
        regex = re.compile(pattern)
        found += [label for label, lower in lowered if regex.search(lower) and label not in found]
    return found


def find_value(product: Product, rule: SpecRule, used: set[str]) -> str | None:
    """Return the page value for a rule, or None.

    The returned value carries the unit from the page label ("190 min").
    Labels are tried in pattern order, but a value must also suit the rule
    (see value_parser.fit): a number rule skips "Ja", an info rule prefers
    real text over "Ja". With aggregate="max" every suitable label is read
    and the highest number wins (e.g. "Påkrevd ladeeffekt (max. i W)").
    The chosen label(s) are added to `used` so no other rule takes them.
    """
    candidates = matching_labels(product, rule, used)
    scored = [(fit(rule.kind, product.specs[label], rule.aggregate), label) for label in candidates]
    if rule.aggregate == "max":
        good = [label for score, label in scored if score == 2]
        if not good:
            return None
        used.update(good)
        return max((page_value(product, label) for label in good), key=parse_max_number)
    for wanted in (2, 1):
        for score, label in scored:
            if score == wanted:
                used.add(label)
                return page_value(product, label)
    return None


def page_value(product: Product, label: str) -> str:
    """The page value with the unit from its own label: ('190', 'Brukstid (minutter)') → '190 min'.

    Elkjøp puts units in labels, and they differ between products, so the
    unit must travel with the number ('190 min' vs '3 timer').
    """
    return with_unit(product.specs[label], label)


def _all_rules() -> list[SpecRule]:
    """Every rule in the guide, de-duplicated by key."""
    seen: dict[str, SpecRule] = {}
    for category in CATEGORIES:
        for rule in category.rules:
            seen.setdefault(rule.key, rule)
    return list(seen.values())


def _with_universal(rules: list[SpecRule]) -> list[SpecRule]:
    """Append rules every category has (e.g. Lanseringsår), without duplicates."""
    keys = {r.key for r in rules}
    return rules + [r for r in UNIVERSAL_RULES if r.key not in keys]


def select_rules(categories: list[Category | None]) -> tuple[list[SpecRule], list[str]]:
    """Choose which rules to compare and return (rules, notes).

    Same category → that category's rules (+ universal rules like Lanseringsår).
    Related categories (same family) → only rules every category shares.
    Unrelated categories → nothing: a phone's battery hours and a robot
      vacuum's runtime must never be put side by side as if comparable.
    Unknown category → every rule in the guide (only matches are shown).
    """
    compatibility = check(categories)
    if compatibility.level == UNRELATED:
        return [], [compatibility.message]
    if compatibility.level == UNKNOWN:
        return _with_universal(_all_rules()), [compatibility.message]
    first = categories[0]
    if compatibility.level == SAME:
        return _with_universal(list(first.rules)), []
    shared_keys = set.intersection(*({r.key for r in c.rules} for c in categories))
    shared = [r for r in first.rules if r.key in shared_keys]
    return _with_universal(shared), [compatibility.message]
