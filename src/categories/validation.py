"""Consistency checks for the whole guide, run by the tests.

A small slip in guide.py (a typo in a regex, a rank rule without an order,
a scenario pointing at a key that doesn't exist) would otherwise only show
up as a silently missing row for one product type. These checks catch it
for every category at once.
"""
from __future__ import annotations

import re

from src.categories import dimensions as d
from src.categories.compatibility import SINGULAR
from src.categories.guide import CATEGORIES, FAMILIES, UNIVERSAL_RULES
from src.categories.scenarios import SCENARIOS
from src.comparison.fallback_extractor import EXTRACTORS, NAME, TEXT
from src.models import SpecRule

KINDS = {"higher", "lower", "energy", "yes", "rank", "info", "cpu", "gpu"}
AGGREGATES = {"first", "max"}


def _check_rule(rule: SpecRule, where: str) -> list[str]:
    problems = []
    if rule.kind not in KINDS:
        problems.append(f"{where}: ukjent kind «{rule.kind}»")
    if rule.dimension not in d.ALL:
        problems.append(f"{where}: ukjent prioritet «{rule.dimension}»")
    if rule.aggregate not in AGGREGATES:
        problems.append(f"{where}: ukjent aggregate «{rule.aggregate}»")
    if rule.kind == "rank" and not rule.order:
        problems.append(f"{where}: rank-regel uten rekkefølge (order)")
    if rule.aggregate == "max" and rule.kind not in ("higher", "lower"):
        problems.append(f"{where}: aggregate=max gir bare mening for tall")
    for pattern in rule.patterns + rule.append:
        if pattern != pattern.lower():
            problems.append(f"{where}: mønsteret «{pattern}» må være små bokstaver")
        try:
            re.compile(pattern)
        except re.error as err:
            problems.append(f"{where}: ugyldig regex «{pattern}»: {err}")
    if not rule.label or not rule.why:
        problems.append(f"{where}: mangler label eller forklaring")
    return problems


def validate_guide() -> list[str]:
    """Return a list of problems; empty means the guide is consistent."""
    problems: list[str] = []
    ids = [c.id for c in CATEGORIES]
    if len(ids) != len(set(ids)):
        problems.append("Kategori-id brukt flere ganger")

    kind_of_key: dict[str, tuple[str, str]] = {}
    for category in CATEGORIES:
        if not category.keywords:
            problems.append(f"{category.id}: mangler nøkkelord")
        keys = [r.key for r in category.rules]
        for key in {k for k in keys if keys.count(k) > 1}:
            problems.append(f"{category.id}: regelen «{key}» finnes flere ganger")
        for dim in category.always_ask:
            if dim not in d.ALL:
                problems.append(f"{category.id}: always_ask har ukjent prioritet «{dim}»")
        for rule in category.rules + UNIVERSAL_RULES:
            problems += _check_rule(rule, f"{category.id}.{rule.key}")
            # The same key must mean the same thing everywhere, or cross-category
            # comparison would mix e.g. "higher is better" with "lower is better".
            seen = kind_of_key.setdefault(rule.key, (rule.kind, category.id))
            if seen[0] != rule.kind:
                problems.append(f"{category.id}.{rule.key}: kind «{rule.kind}» ≠ «{seen[0]}» i {seen[1]}")

        known = set(keys) | {r.key for r in UNIVERSAL_RULES} | ({"generation"} if category.name_generations else set())
        scenarios = SCENARIOS.get(category.id, ())
        if not scenarios:
            problems.append(f"{category.id}: mangler bruksscenarioer (src/categories/scenarios.py)")
        for scenario in scenarios:
            for key in scenario.keys:
                if key not in known:
                    problems.append(f"{category.id}: scenarioet «{scenario.title}» bruker ukjent regel «{key}»")

    for scenario_category in SCENARIOS:
        if scenario_category not in ids:
            problems.append(f"scenarios.py: ukjent kategori «{scenario_category}»")

    for family in FAMILIES:
        for category_id in family:
            if category_id not in ids:
                problems.append(f"FAMILIES: ukjent kategori «{category_id}»")
    for category_id in ids:
        if category_id not in SINGULAR:
            problems.append(f"compatibility.SINGULAR mangler «{category_id}»")

    all_keys = {r.key for c in CATEGORIES for r in c.rules} | {r.key for r in UNIVERSAL_RULES}
    for key, extractors in EXTRACTORS.items():
        if key not in all_keys:
            problems.append(f"fallback_extractor: «{key}» finnes ikke som regel i guiden")
        for source, pattern, template in extractors:
            if source not in (NAME, TEXT):
                problems.append(f"fallback_extractor.{key}: ukjent kilde «{source}»")
            try:
                compiled = re.compile(pattern)
            except re.error as err:
                problems.append(f"fallback_extractor.{key}: ugyldig regex: {err}")
                continue
            if "v" not in compiled.groupindex:
                problems.append(f"fallback_extractor.{key}: mønsteret mangler (?P<v>…)")
            if "{v}" not in template and template != "Ja":
                problems.append(f"fallback_extractor.{key}: malen «{template}» mangler {{v}}")
    return problems
