"""Facts about specific models that Elkjøp's spec table leaves out.

Used only when the spec table has no value for a rule (the table always
wins). Each entry is taken from the manufacturer's own model overview, so
nothing is guessed: a model that is not listed simply gets no value here.

Sources (Oct 2026):
- Oral-B iO: Oral-B's own iO2–iO10 comparison chart, plus Tech Advisor's
  model-by-model overview for iO4/iO7/iO8.
- Philips Sonicare: Philips' series overview as summarised by Electric Teeth
  and Brush & Floss (1100–9900 Prestige).
- Phone chips: the chip each phone model ships with in Norway.

The source shown in the table is MODEL_SOURCE.
"""
from __future__ import annotations

import re

from src.models import Product

MODEL_SOURCE = "produsentens modelloversikt"

# (regex on the lowercase product name, {rule key: value})
# Longer / more specific patterns must come before shorter ones ("io10" before "io1").
_TOOTHBRUSHES: list[tuple[str, dict[str, str]]] = [
    # Oral-B iO – from Oral-B's comparison chart (the picture the customer sent)
    (r"\bio\s?10\b", {"brush_modes": "7", "pressure_sensor": "Ja", "smart_sensor": "Ja", "timer": "Ja", "app": "Ja",
                      "display": "Ja", "ai_tracking": "Ja", "travel_case": "Ja", "charging_case": "Ja", "fast_charger": "Ja"}),
    (r"\bio\s?9\b", {"brush_modes": "7", "pressure_sensor": "Ja", "smart_sensor": "Ja", "timer": "Ja", "app": "Ja",
                     "display": "Ja", "ai_tracking": "Ja", "travel_case": "Ja", "charging_case": "Ja", "fast_charger": "Ja"}),
    (r"\bio\s?8\b", {"brush_modes": "6", "pressure_sensor": "Ja", "smart_sensor": "Ja", "timer": "Ja", "app": "Ja",
                     "display": "Ja", "travel_case": "Ja", "fast_charger": "Ja"}),
    (r"\bio\s?7\b", {"brush_modes": "5", "pressure_sensor": "Ja", "smart_sensor": "Ja", "timer": "Ja", "app": "Ja",
                     "display": "Ja", "travel_case": "Ja", "fast_charger": "Ja"}),
    (r"\bio\s?6\b", {"brush_modes": "5", "pressure_sensor": "Ja", "smart_sensor": "Ja", "timer": "Ja", "app": "Ja",
                     "display": "Ja", "travel_case": "Ja", "charging_case": "Nei", "fast_charger": "Nei"}),
    (r"\bio\s?5\b", {"brush_modes": "5", "pressure_sensor": "Ja", "smart_sensor": "Ja", "timer": "Ja", "app": "Ja",
                     "display": "Nei", "travel_case": "Ja", "charging_case": "Nei", "fast_charger": "Nei"}),
    (r"\bio\s?4\b", {"brush_modes": "4", "pressure_sensor": "Ja", "smart_sensor": "Ja", "timer": "Ja", "app": "Ja",
                     "display": "Nei", "charging_case": "Nei", "fast_charger": "Nei"}),
    (r"\bio\s?3\b", {"brush_modes": "3", "pressure_sensor": "Ja", "smart_sensor": "Ja", "timer": "Ja", "app": "Nei",
                     "display": "Nei", "charging_case": "Nei", "fast_charger": "Nei"}),
    (r"\bio\s?2\b", {"brush_modes": "3", "pressure_sensor": "Ja", "smart_sensor": "Nei", "timer": "Ja", "app": "Nei",
                     "display": "Nei", "charging_case": "Nei", "fast_charger": "Nei"}),
    # Philips Sonicare – Philips' series overview
    (r"prestige|\b9900\b", {"brush_modes": "5", "intensity": "3", "pressure_sensor": "Ja", "brush_reminder": "Ja",
                            "app": "Ja", "timer": "Ja", "travel_case": "Ja", "charging_case": "Ja"}),
    (r"diamondclean|\b9000\b", {"brush_modes": "4", "intensity": "3", "pressure_sensor": "Ja", "brush_reminder": "Ja",
                                "app": "Ja", "timer": "Ja"}),
    (r"\b6100\b", {"brush_modes": "3", "intensity": "3", "pressure_sensor": "Ja", "brush_reminder": "Ja", "app": "Nei",
                   "timer": "Ja", "travel_case": "Ja"}),
    (r"\b5300\b", {"brush_modes": "3", "pressure_sensor": "Ja", "brush_reminder": "Ja", "app": "Nei", "timer": "Ja"}),
    (r"\b5100\b", {"brush_modes": "3", "pressure_sensor": "Ja", "brush_reminder": "Ja", "app": "Nei", "timer": "Ja",
                   "travel_case": "Ja"}),
    (r"\b4100\b", {"brush_modes": "1", "intensity": "2", "pressure_sensor": "Ja", "brush_reminder": "Ja", "app": "Nei",
                   "timer": "Ja"}),
    (r"\b3100\b", {"brush_modes": "1", "pressure_sensor": "Ja", "brush_reminder": "Ja", "app": "Nei", "timer": "Ja"}),
    (r"\b2100\b", {"brush_modes": "1", "intensity": "2", "pressure_sensor": "Nei", "brush_reminder": "Nei", "app": "Nei",
                   "timer": "Ja"}),
    (r"\b1100\b", {"brush_modes": "1", "pressure_sensor": "Nei", "brush_reminder": "Nei", "app": "Nei", "timer": "Ja"}),
]

# Phone chips. Pixel pages sometimes lack "Type prosessor"; every phone of the
# same kind should still get a processor row.
_PHONE_CHIPS: list[tuple[str, str]] = [
    (r"pixel 10 pro", "Tensor G5"), (r"pixel 10\b", "Tensor G5"),
    (r"pixel 9 ?pro", "Tensor G4"), (r"pixel 9a\b", "Tensor G4"), (r"pixel 9\b", "Tensor G4"),
    (r"pixel 8 ?pro", "Tensor G3"), (r"pixel 8a\b", "Tensor G3"), (r"pixel 8\b", "Tensor G3"),
    (r"pixel 7 ?pro", "Tensor G2"), (r"pixel 7a\b", "Tensor G2"), (r"pixel 7\b", "Tensor G2"),
    (r"iphone 17 pro", "A19 Pro"), (r"iphone air", "A19 Pro"), (r"iphone 17\b", "A19"),
    (r"iphone 16e", "A18"), (r"iphone 16 pro", "A18 Pro"), (r"iphone 16\b", "A18"),
    (r"iphone 15 pro", "A17 Pro"), (r"iphone 15\b", "A16 Bionic"),
    (r"iphone 14 pro", "A16 Bionic"), (r"iphone 14\b", "A15 Bionic"), (r"iphone 13\b", "A15 Bionic"),
    (r"galaxy s26 ultra", "Snapdragon 8 Elite Gen 5 for Galaxy"), (r"galaxy s26\b", "Exynos 2600"),
    (r"galaxy s25 fe", "Exynos 2400"), (r"galaxy s25\b", "Snapdragon 8 Elite for Galaxy"),
    (r"galaxy s24 ultra", "Snapdragon 8 Gen 3 for Galaxy"), (r"galaxy s24 fe", "Exynos 2400e"),
    (r"galaxy s24\b", "Exynos 2400"),
]


def _name(product: Product) -> str:
    return re.sub(r"\s+", " ", (product.name or "").lower())


def fact(product: Product, key: str) -> str | None:
    """The manufacturer's value for this product and rule key, or None."""
    name = _name(product)
    if key == "processor":
        for pattern, chip in _PHONE_CHIPS:
            if re.search(pattern, name):
                return chip
        return None
    if "tannbørste" in name or "tannborste" in name or "sonicare" in name or "oral-b" in name:
        for pattern, facts in _TOOTHBRUSHES:
            if re.search(pattern, name):
                return facts.get(key)
    return None
