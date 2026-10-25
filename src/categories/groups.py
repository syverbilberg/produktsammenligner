"""The tabs at the top of the app, following Elkjøp's own product tree.

Each group lists the categories (ids from guide.py) that belong to it.
A category may sit in several groups (a gaming laptop is both Computing and
Gaming). validation.py checks that every category is in at least one group.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Group:
    """One tab.

    Attributes:
        id: Short key used in session state.
        name: Tab label.
        hint: Example products shown under the tabs.
        categories: Category ids that belong to this tab.
    """

    id: str
    name: str
    hint: str
    categories: tuple[str, ...]


GROUPS: tuple[Group, ...] = (
    Group("mda", "MDA", "Kjøleskap, komfyr, platetopp, mikro, kjøkkenvifte, oppvask, vask og tørk",
          ("fridge", "american_fridge", "wine_fridge", "oven", "hob", "microwave", "hood", "dishwasher",
           "washer", "washer_dryer", "dryer")),
    Group("sda", "SDA", "Støvsugere, kaffe, kjøkkenapparater, personlig pleie, inneklima og elsykler",
          ("vacuum", "robot_vacuum", "coffee", "capsule", "filter_coffee", "grinder", "kitchen_machine", "blender",
           "stick_mixer", "airfryer", "sandwich", "soda", "kitchen", "toothbrush", "shaver", "hair", "ipl", "scale",
           "air_purifier", "dehumidifier", "fan", "heater", "air_conditioner", "emobility")),
    Group("computing", "Data", "Bærbare og stasjonære PC-er, nettbrett, skjermer, skrivere, lagring, nettverk og kamera",
          ("laptop", "desktop", "tablet", "monitor", "printer", "storage", "mouse", "keyboard", "router", "pc_speaker",
           "camera")),
    Group("gaming", "Gaming", "Konsoller, gaming-PC og -laptop, kontrollere, ratt, headset og strømmeutstyr",
          ("console", "laptop", "desktop", "controller", "racing", "streaming_gear", "component", "headphones",
           "mouse", "keyboard", "monitor")),
    Group("mobile", "Mobil", "Mobiltelefoner, smartklokker og nettbrett", ("mobile", "watch", "tablet")),
    Group("tv_audio", "TV og lyd", "TV, lydplanker, høyttalere, hodetelefoner og projektorer",
          ("tv", "soundbar", "speaker", "headphones", "projector")),
)

BY_ID = {group.id: group for group in GROUPS}


def groups_for(category_id: str) -> list[Group]:
    """Every tab a category belongs to."""
    return [g for g in GROUPS if category_id in g.categories]


@dataclass
class Placement:
    """Where a fetched product belongs relative to the open tab.

    Attributes:
        category: The category to use, or None (unknown product, or wrong tab).
        wrong_tab: Set when the product clearly belongs to another tab.
        actual: The product's own category when it is in the wrong tab.
    """

    category: "object | None"
    wrong_tab: Group | None = None
    actual: "object | None" = None


def place(product, group: Group) -> Placement:
    """Find the product's category inside `group`.

    The product's best category over ALL categories decides: if it is in the
    open tab, use it; if it belongs to another tab, report that tab (so a
    robot vacuum searched under MDA is not squeezed into "kjøleskap").
    A product no category recognises is let through as unknown.
    """
    from src.categories.detector import detect_category   # local: detector imports guide, guide is light
    best = detect_category(product, use_hint=False)
    if best is None:
        return Placement(detect_category(product, group.categories, use_hint=False))
    if best.id in group.categories:
        return Placement(best)
    return Placement(None, groups_for(best.id)[0], best)
