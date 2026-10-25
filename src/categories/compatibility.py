"""Can these products be compared? Same category, related, or unrelated.

  same      – compared on the category's full guide
  related   – same family (laptop ↔ tablet): compared on shared specs, with a note
  unrelated – phone ↔ robot vacuum: no comparison; the app asks the customer
              to swap a product or see a side-by-side overview without winners
  unknown   – a category could not be detected: compared on any known spec, with a note
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.categories.guide import FAMILIES
from src.models import Category

SAME, RELATED, UNRELATED, UNKNOWN = "same", "related", "unrelated", "unknown"


@dataclass
class Compatibility:
    """Result of comparing the products' categories.

    Attributes:
        level: SAME, RELATED, UNRELATED or UNKNOWN.
        categories: Detected category per product (None when unknown).
        odd_ones: Indices of products that don't fit with the rest (UNRELATED only).
        message: Short Norwegian explanation for the customer ("" for SAME).
    """

    level: str
    categories: list[Category | None]
    odd_ones: list[int]
    message: str


def related(a: Category, b: Category) -> bool:
    """True when two categories are the same or share a family."""
    return a.id == b.id or any(a.id in family and b.id in family for family in FAMILIES)


# Singular with article, used in sentences. validation.py checks every category has one.
SINGULAR: dict[str, str] = {
    "mobile": "en mobiltelefon", "tablet": "et nettbrett", "watch": "en smartklokke",
    "headphones": "hodetelefoner", "laptop": "en bærbar PC", "desktop": "en stasjonær PC",
    "monitor": "en PC-skjerm", "printer": "en skriver", "tv": "en TV", "soundbar": "en lydplanke",
    "camera": "et kamera", "fridge": "et kjøleskap/fryser",
    "oven": "en stekeovn/komfyr", "washer": "en vaskemaskin", "dryer": "en tørketrommel",
    "dishwasher": "en oppvaskmaskin", "vacuum": "en støvsuger", "coffee": "en kaffemaskin",
    "kitchen_machine": "en kjøkkenmaskin", "airfryer": "en airfryer", "blender": "en blender",
    "kitchen": "et kjøkkenapparat", "emobility": "et elkjøretøy",
    "speaker": "en høyttaler", "projector": "en projektor", "storage": "en lagringsenhet", "mouse": "en mus",
    "keyboard": "et tastatur", "router": "en ruter", "pc_speaker": "PC-høyttalere", "console": "en spillkonsoll",
    "controller": "en spillkontroller", "racing": "et ratt/joystick", "streaming_gear": "strømmeutstyr",
    "component": "en PC-komponent", "american_fridge": "et amerikanerskap", "wine_fridge": "et vinskap",
    "hob": "en platetopp", "microwave": "en mikrobølgeovn", "hood": "en kjøkkenvifte",
    "washer_dryer": "en kombinert vaskemaskin/tørketrommel", "stick_mixer": "en stavmikser", "sandwich": "en sandwichgrill/vaffeljern",
    "soda": "en kullsyremaskin", "capsule": "en kapselmaskin", "filter_coffee": "en kaffetrakter", "grinder": "en kaffekvern",
    "toothbrush": "en elektrisk tannbørste", "shaver": "en barbermaskin/trimmer", "hair": "en hårføner/styler",
    "ipl": "en IPL/epilator", "scale": "en badevekt", "robot_vacuum": "en robotstøvsuger", "air_purifier": "en luftrenser",
    "dehumidifier": "en avfukter", "fan": "en vifte", "heater": "en panelovn/varmeovn", "air_conditioner": "en aircondition",
}


def _type_name(category: Category) -> str:
    """'mobile' → 'en mobiltelefon'."""
    return SINGULAR.get(category.id, category.name.lower())


def _bare(category: Category) -> str:
    """'en mobiltelefon' → 'mobiltelefon'."""
    return _type_name(category).split(" ", 1)[-1] if _type_name(category).startswith(("en ", "et ")) else _type_name(category)


def check(categories: list[Category | None]) -> Compatibility:
    """Classify a set of detected categories."""
    if any(c is None for c in categories):
        return Compatibility(UNKNOWN, categories, [],
                             "Fant ikke produkttypen sikkert – sammenligner alle kjente spesifikasjoner.")
    if len({c.id for c in categories}) == 1:
        return Compatibility(SAME, categories, [], "")
    if all(related(a, b) for a in categories for b in categories):
        names = " og ".join(sorted({_bare(c) for c in categories}))
        return Compatibility(RELATED, categories, [],
                             f"Ulike, men beslektede produkttyper ({names}). Bare det de har felles sammenlignes.")

    # Unrelated: the most common category is the reference; the rest are "odd".
    reference_id = Counter(c.id for c in categories).most_common(1)[0][0]
    reference = next(c for c in categories if c.id == reference_id)
    odd = [i for i, c in enumerate(categories) if not related(c, reference)]
    letters = "ABCD"
    parts = [f"{letters[i]} er {_type_name(c)}" for i, c in enumerate(categories)]
    message = f"Produkt {_join(parts)}, kan ikke sammenlignes."
    return Compatibility(UNRELATED, categories, odd, message)


def _join(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " og " + parts[-1]
