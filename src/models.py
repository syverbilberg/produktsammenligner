"""Shared data classes used by every part of the app."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Product:
    """A product fetched from an Elkjøp product page.

    Attributes:
        sku: Elkjøp varekode, e.g. "457340".
        name: Product name as shown on the page.
        url: Final product page URL.
        price: Price in NOK, or None if it could not be read.
        brand: Brand name, if available.
        image: URL of the main product image, if available.
        rating: Average customer rating (0–5), if available.
        review_count: Number of customer reviews behind the rating.
        category_path: Category part of the URL, e.g. "hvitevarer/oppvaskmaskin".
        specs: Spec label -> value, exactly as written on the page.
        description: Product description text (used when a spec is missing
            from the spec table but mentioned in the text).
        category_id: Category chosen when the product was fetched inside a tab
            (e.g. "vacuum" in the SDA tab). Empty = detect from the page.
    """

    sku: str
    name: str = ""
    url: str = ""
    price: float | None = None
    brand: str = ""
    image: str = ""
    rating: float | None = None
    review_count: int | None = None
    category_path: str = ""
    specs: dict[str, str] = field(default_factory=dict)
    description: str = ""
    category_id: str = ""


@dataclass(frozen=True)
class SpecRule:
    """One spec from the category guide and how to compare it.

    Attributes:
        key: Internal id, shared across categories (e.g. "ram") so that
            products from different categories can be compared on overlap.
        label: Norwegian display name shown to the customer.
        patterns: Regexes (lowercase) matched against Elkjøp spec labels;
            the first spec label that matches any pattern is used.
        kind: How to pick a winner:
            "higher" – larger number wins
            "lower"  – smaller number wins
            "energy" – better EU energy class wins
            "yes"    – having the feature ("Ja") wins
            "rank"   – value containing an earlier word in `order` wins
            "cpu"    – processor, ranked by comparison/hardware.py
            "gpu"    – graphics card, ranked by comparison/hardware.py
            "info"   – shown for information only, no winner
        dimension: Which customer priority this spec belongs to.
        why: One line explaining why the spec matters.
        order: Ranking words for kind="rank", best first.
        aggregate: "first" uses the first matching label; "max" looks at
            every matching label and keeps the highest number (e.g. the
            maximum charging effect when a page lists several).
        append: Patterns for labels whose value is added after the main
            value, e.g. "Prosessortype: Intel Core i7" + "Nummer: 14700F"
            → "Intel Core i7 14700F".
    """

    key: str
    label: str
    patterns: tuple[str, ...]
    kind: str
    dimension: str
    why: str
    order: tuple[str, ...] = ()
    aggregate: str = "first"
    append: tuple[str, ...] = ()


@dataclass(frozen=True)
class Category:
    """A product category from the guide.

    Attributes:
        id: Internal id, e.g. "dishwasher".
        name: Norwegian display name, e.g. "Oppvaskmaskiner".
        keywords: Words found in Elkjøp URLs/names/product types for this category.
        rules: The specs that matter for this category.
        always_ask: Priorities always asked for this category, even when
            the pages lack comparable specs for them (e.g. camera for phones).
        name_generations: True when numbers in product names are model
            generations (Galaxy S25 → S26). False where they usually mean
            size (laptops, TVs: "HP Laptop 14", 'LG 65"').
    """

    id: str
    name: str
    keywords: tuple[str, ...]
    rules: tuple[SpecRule, ...] = ()
    always_ask: tuple[str, ...] = ()
    name_generations: bool = False


@dataclass
class SpecRow:
    """One compared spec: a value per product and the winner.

    Attributes:
        rule: The guide rule this row comes from.
        values: Raw value per product, in input order (None when missing).
        winner: Index of the best product, or None for a tie / not comparable.
        sources: Where each value came from: "" (spec table), "navnet"
            (product name) or "beskrivelsen" (description text).
    """

    rule: SpecRule
    values: tuple[str | None, ...]
    winner: int | None
    sources: tuple[str, ...] = ()


@dataclass
class ComparisonResult:
    """Everything the result view needs to show.

    Attributes:
        products: The compared products (2–4), in input order.
        categories: Detected category per product (None when unknown).
        rows: Compared specs, in guide order.
        scores: Weighted points per product.
        summaries: Short customer summary per product.
        verdict: "Velg A hvis … Velg B hvis …" text.
        warnings: Dealbreakers and notes (e.g. different categories).
    """

    products: list[Product]
    categories: list[Category | None]
    rows: list[SpecRow]
    scores: list[float]
    summaries: list[str]
    verdict: str
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Scenario:
    """A typical use case for a category, e.g. "Brød og tunge deiger".

    Attributes:
        title: Heading shown in the "Funksjoner og bruk" tab.
        choose_text: Fits after "Velg X hvis du …", e.g. "baker mye brød".
        keys: Rule keys that decide this use case, most important first.
        icon: Icon name from src/ui/components.ICONS.
    """

    title: str
    choose_text: str
    keys: tuple[str, ...]
    icon: str = "star"


@dataclass
class ScenarioResult:
    """How the products do in one use case.

    Attributes:
        scenario: The use case.
        winner: Index of the best product, or None if equal / unclear.
        reasons: Short facts behind the result, e.g. "Motorkraft: 1600 W mot 1200 W".
    """

    scenario: Scenario
    winner: int | None
    reasons: list[str]


@dataclass
class FeatureRow:
    """One yes/no feature across the products.

    Attributes:
        label: Feature name, e.g. "Integrert vekt".
        values: True / False / None (not stated) per product.
        source: "" when from the spec table, otherwise "beskrivelsen"/"navnet".
        details: Extra text per product, e.g. "med tilbehør" or "Vibrerende".
    """

    label: str
    values: tuple[bool | None, ...]
    source: str = ""
    details: tuple[str, ...] = ()

    @property
    def differs(self) -> bool:
        """True when the known values (or their details) are not all the same."""
        known = [(v, d) for v, d in zip(self.values, self.details or ("",) * len(self.values)) if v is not None]
        return len(set(known)) > 1


@dataclass
class Insights:
    """Everything the "Funksjoner og bruk" tab shows.

    Attributes:
        products: The products, in input order.
        short_names: Short display name per product, e.g. "Bosch Series 6".
        differences: Spec rows where the products differ (no yes/no rows).
        features: Yes/no features, differing ones first.
        included: What comes in the box, per product.
        scenarios: Result per use case for the detected category.
        pros: Advantages per product.
        cons: Disadvantages per product.
        choose: "Velg X hvis …" sentence per product.
    """

    products: list[Product]
    short_names: list[str]
    differences: list[SpecRow]
    features: list[FeatureRow]
    included: list[list[str]]
    scenarios: list[ScenarioResult]
    pros: list[list[str]]
    cons: list[list[str]]
    choose: list[str]
