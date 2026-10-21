"""Scores each product per use case ("Brød og tunge deiger", "Foto og video" …).

A product wins a use case by winning most of the specs that decide it.
The first key of a scenario is the most important and counts double.

Missing data is never turned into a guess:
- a number stated for only one product is shown, but doesn't count;
- a feature mentioned ("Ja") for one product and simply not mentioned
  for the other counts half, and is worded "bare X nevner …".
"""
from __future__ import annotations

from src.categories.scenarios import SCENARIOS
from src.insights.phrasing import fact, mentioned_only_by
from src.models import Category, ScenarioResult, SpecRow


def evaluate(categories: list[Category | None], rows: list[SpecRow], names: list[str]) -> list[ScenarioResult]:
    """Result per scenario for the shared category (none if categories differ)."""
    first = categories[0]
    if first is None or any(c is None or c.id != first.id for c in categories):
        return []
    by_key = {row.rule.key: row for row in rows}
    results = []
    for scenario in SCENARIOS.get(first.id, ()):
        relevant = [by_key[key] for key in scenario.keys if key in by_key]
        if not relevant:
            continue  # nothing on the pages about this use case
        wins = [0.0] * len(names)
        for row in relevant:
            weight = 2.0 if row.rule.key == scenario.keys[0] else 1.0
            if row.winner is not None:
                wins[row.winner] += weight
            else:
                for holder in mentioned_only_by(row):
                    wins[holder] += weight / 2
        top = max(wins)
        leaders = [i for i, w in enumerate(wins) if w == top]
        winner = leaders[0] if top > 0 and len(leaders) == 1 else None
        # Facts: deciding rows first, then the rest, at most four.
        ordered = ([r for r in relevant if r.winner is not None]
                   + [r for r in relevant if r.winner is None and mentioned_only_by(r)]
                   + [r for r in relevant if r.winner is None and not mentioned_only_by(r)])
        results.append(ScenarioResult(scenario, winner, [fact(r, names) for r in ordered[:4]]))
    return results
