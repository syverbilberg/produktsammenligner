"""Turns spec text like '1 TB', 'A+++' or 'Ja' into comparable numbers.

Every function returns np.nan when the value can't be read, so missing data
never turns into a guess.
"""
from __future__ import annotations

import re

import numpy as np

_NUMBER = re.compile(r"\d{1,3}(?:[  ]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?")
_ENERGY_CLASSES = ("A+++", "A++", "A+", "A", "B", "C", "D", "E", "F", "G")
_NO_WORDS = ("nei", "no", "ingen", "ikke", "uten")


# Units converted to one base before comparing, so "190 min" and "3 timer"
# or "4000 ml" and "4,2 liter" compare correctly. Base: minutes, liter, kg, GB.
_UNIT_SCALE = {
    "min": 1, "minutter": 1, "minutt": 1, "t": 60, "h": 60, "time": 60, "timer": 60,
    "ml": 0.001, "cl": 0.01, "dl": 0.1, "l": 1, "liter": 1,
    "g": 0.001, "kg": 1, "tb": 1024, "gb": 1,
}
_UNIT_AFTER = re.compile(r"\s*-?\s*([a-zæøå]+)", re.IGNORECASE)


def _to_float(text: str) -> float:
    return float(re.sub(r"[ \u00a0]", "", text).replace(",", "."))


def _scaled(value: str, match: re.Match) -> float:
    """The matched number converted with the unit written right after it."""
    number = _to_float(match.group())
    unit = _UNIT_AFTER.match(value, match.end())
    return number * _UNIT_SCALE.get(unit.group(1).lower(), 1) if unit else number


def parse_number(value: str | None) -> float:
    """First number in the text, in base units (minutes, liter, kg, GB)."""
    if not value:
        return np.nan
    match = _NUMBER.search(value)
    return _scaled(value, match) if match else np.nan


def parse_energy_class(value: str | None) -> float:
    """EU energy class as a rank where lower is better (A+++ = 0)."""
    if not value:
        return np.nan
    cleaned = value.strip().upper().replace(" ", "")
    for rank, energy_class in enumerate(_ENERGY_CLASSES):
        if cleaned.startswith(energy_class):
            return float(rank)
    return np.nan


_PARTIAL = re.compile(r"(tilbehør|ekstrautstyr|krever|valgfri|i tillegg|kjøpes separat|ekstra kostnad)")


def parse_yes(value: str | None) -> float:
    """1.0 = has it, 0.5 = only with extra purchase ("Ja, med tilbehør"), 0.0 = doesn't."""
    if not value:
        return np.nan
    lower = value.strip().lower()
    if lower.startswith(_NO_WORDS):
        return 0.0
    if _PARTIAL.search(lower):
        return 0.5
    return 1.0  # "Ja", or a descriptive value ("Pyrolyse", "Vibrerende") means it has it


def parse_rank(value: str | None, order: tuple[str, ...]) -> float:
    """Position of the best `order` word in the value (lower = better).

    More technologies break ties: "Kamera, Laser" (0.9) beats "Laser" (1.0).
    """
    if not value:
        return np.nan
    lower = value.lower()
    found = [rank for rank, word in enumerate(order) if word in lower]
    if not found:
        return np.nan
    return float(min(found)) - 0.1 * (len(found) - 1)


def parse_max_number(value: str | None) -> float:
    """Largest number in the text, in base units, e.g. '10 W / 25 W' -> 25.0."""
    if not value:
        return np.nan
    numbers = [_scaled(value, m) for m in _NUMBER.finditer(value)]
    return max(numbers) if numbers else np.nan


_YES_NO = re.compile(r"^\s*(ja|nei|yes|no)\b", re.IGNORECASE)


def fit(kind: str, value: str | None, aggregate: str = "first") -> int:
    """How well a page value suits a rule kind: 2 = good, 1 = usable, 0 = wrong.

    Stops a rule from grabbing the wrong label, e.g. a number rule landing
    on "Hurtiglading: Ja" or an info rule landing on "Videoopptak: Ja".
    """
    if not value or not value.strip():
        return 0
    if kind in ("higher", "lower"):
        number = parse_max_number(value) if aggregate == "max" else parse_number(value)
        return 0 if np.isnan(number) else 2
    if kind == "energy":
        return 0 if np.isnan(parse_energy_class(value)) else 2
    if kind == "yes":
        return 2 if _YES_NO.match(value) else 1
    if kind == "info":
        return 1 if _YES_NO.match(value) else 2
    return 2  # rank: any text; unknown words simply give no winner
