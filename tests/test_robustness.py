"""Guards for the whole app, not just one product type.

1. The guide is internally consistent (validation.py).
2. Real Elkjøp label sets give the right values (real_pages.py).
3. Every category is reachable by its own URL/name keywords.
4. No rule ever takes a value of the wrong type from any real page.
"""
import json

import numpy as np
import pytest

from src.categories import BY_ID, CATEGORIES, detect_category
from src.categories.validation import validate_guide
from src.comparison.comparer import build_rows, value_for
from src.comparison.value_parser import fit
from src.fetching.page_parser import parse_product_page
from src.fetching.url_resolver import category_from_url, sku_from_url
from src.models import Product
from src.text import fold
from tests import real_pages as pages

ALL_PAGES = [pages.S26, pages.S25, pages.HP_LAPTOP, pages.BOSCH_MUMS6, pages.KENWOOD_KVL85, pages.ASKO_DISHWASHER,
             pages.ROBOROCK_SAROS20S, pages.DREAME_X60_PRO]


def build(page: dict) -> Product:
    """Turn a real_pages entry into a Product, through the real HTML parser."""
    json_ld = {"@type": "Product", "name": page["name"], "description": page["description"],
               "offers": {"price": page["price"]}}
    if page["rating"]:
        json_ld["aggregateRating"] = {"ratingValue": page["rating"], "reviewCount": page["reviews"]}
    rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in page["specs"].items())
    html = (f'<script type="application/ld+json">{json.dumps(json_ld)}</script>'
            f"<h1>{page['name']}</h1><h2>Spesifikasjoner</h2><table>{rows}</table>")
    product = Product(sku=sku_from_url(page["url"]), url=page["url"], category_path=category_from_url(page["url"]))
    return parse_product_page(html, product)


def values(page: dict) -> dict[str, tuple[str | None, str]]:
    """rule key -> (value, source) for one product with its own category's rules."""
    product = build(page)
    category = detect_category(product)
    used: set[str] = set()
    return {rule.key: value_for(product, rule, used) for rule in category.rules}


# ------------------------------------------------------------------- 1. guide
def test_guide_is_consistent():
    assert validate_guide() == []


# -------------------------------------------------------------- 2. real pages
def test_s26_real_labels():
    v = values(pages.S26)
    assert v["fast_charge"][0] == "25 W"                       # max, not "min. i W: 10"
    assert v["ram"] == ("12 GB", "navnet")                   # not in the table → from the name
    assert v["storage"][0] == "256 GB"
    assert v["screen_type"][0] == "OLED"                     # label is just "Display"
    assert v["screen_size"][0] == '6.3"'                      # label "Størrelse (tommer)"
    assert v["refresh"][0] == "120"
    assert v["ip"][0] == "IP68"
    assert v["battery_mah"][0] == "4300 mAh"
    assert v["battery_cycles"][0] == "2700"
    assert v["camera_count"][0] == "3"
    assert v["video"][0] == "8K UHD (4320p)"                 # not "Videoopptak: Ja"
    assert v["charger"][0] == "Nei"
    assert v["processor"] == ("Exynos 2600", "beskrivelsen")


def test_laptop_real_labels():
    product = build(pages.HP_LAPTOP)
    assert detect_category(product).id == "laptop"
    v = values(pages.HP_LAPTOP)
    assert v["ram"][0] == "16 GB"                               # not "RAM-type: DDR4"
    assert v["storage"][0] == "512 GB"
    assert v["processor"][0] == "Intel Core 5"
    assert v["screen_size"][0] == '14"'
    assert v["brightness"][0] == "250"                       # label is "Nit"
    assert v["battery_life"][0] == "7.5 timer"
    assert v["fast_charge"][0] == "100 W"
    assert v["weight"][0] == "1.4 kg"
    assert v["resolution"][0] == "Full HD (1080p)"
    assert v["hdmi"][0] == "Ja" and v["thunderbolt"][0] == "Nei"


def test_kitchen_machines_real_labels():
    bosch, kenwood = values(pages.BOSCH_MUMS6), values(pages.KENWOOD_KVL85)
    assert bosch["motor_power"][0] == "1600 W" and kenwood["motor_power"][0] == "1200 W"
    assert bosch["bowl_volume"][0] == "5.5 liter" and kenwood["bowl_volume"][0] == "7 liter"   # label says "(Itr)"
    assert bosch["dough_capacity"][0] == "3.5 kg"                                    # kg – not a volume
    assert bosch["bowls"][0] == "2" and kenwood["bowls"][0] == "2"
    assert bosch["scale"] == ("Ja", "beskrivelsen") and kenwood["scale"] == ("Ja", "beskrivelsen")
    assert bosch["auto_programs"][0] == "Ja" and kenwood["auto_programs"][0] is None   # not mentioned ≠ "Nei"
    assert bosch["timer"][0] == "Ja" and bosch["display"][0] == "Ja"
    assert kenwood["outlets"][0] == "2"


def test_dishwasher_real_labels():
    v = values(pages.ASKO_DISHWASHER)
    assert v["noise"][0] == "41 dB" and v["energy"][0] == "B" and v["place_settings"][0] == "15"
    assert v["water"][0] == "9.6 liter" and v["auto_open"][0] == "Ja" and v["cutlery"][0] == "Bestikkurv"


# ------------------------------------------------------- 3. category routing
@pytest.mark.parametrize("category", CATEGORIES, ids=lambda c: c.id)
def test_every_category_is_reachable_from_its_url(category):
    keyword = fold(category.keywords[0]).replace(" ", "-")
    product = Product(sku="1", name=f"Merke {category.keywords[0]} X100",
                      category_path=f"overkategori/{keyword}")
    assert detect_category(product).id == category.id


@pytest.mark.parametrize("page", ALL_PAGES, ids=lambda p: p["name"][:30])
def test_real_pages_get_the_right_category(page):
    expected = {"Mobiltelefon": "mobile", "Bærbar PC": "laptop", "Kjøkkenmaskin": "kitchen_machine",
                "Oppvaskmaskin": "dishwasher", "Robotstøvsuger": "vacuum"}[page["specs"]["Produkttype"]]
    assert detect_category(build(page)).id == expected


# --------------------------------------------- 4. no wrong-typed values ever
@pytest.mark.parametrize("page", ALL_PAGES, ids=lambda p: p["name"][:30])
@pytest.mark.parametrize("category", CATEGORIES, ids=lambda c: c.id)
def test_no_rule_takes_a_wrong_typed_value(page, category):
    """Run EVERY category's rules on EVERY real page (as happens for unknown
    categories) and check each found value suits its rule."""
    product = build(page)
    used: set[str] = set()
    for rule in category.rules:
        value, _ = value_for(product, rule, used)
        if value is None:
            continue
        assert fit(rule.kind, value, rule.aggregate) > 0, f"{category.id}.{rule.key} took «{value}»"
        if rule.kind in ("higher", "lower"):
            assert not np.isnan(float(__import__("src.comparison.value_parser", fromlist=["x"]).parse_max_number(value)))


def test_s25_vs_s26_recommends_the_newer_phone_with_neutral_weights():
    from src.categories import dimensions as d
    from src.comparison import compare, relevant_dimensions
    products = [build(pages.S25), build(pages.S26)]
    weights = {dim: d.LEVELS[d.DEFAULT_LEVEL] for dim in relevant_dimensions(products)}
    result = compare(products, weights)
    assert result.scores[1] > result.scores[0]
    rows = {row.rule.key: row for row in result.rows}
    assert rows["generation"].winner == 1


def test_laptop_names_are_not_read_as_generations():
    a = build(pages.HP_LAPTOP)
    b = build({**pages.HP_LAPTOP, "name": 'HP Laptop 15-fd0830no Core5-120U/16/512 15" bærbar PC'})
    rows, _, _ = build_rows([a, b])
    assert "generation" not in {row.rule.key for row in rows}


def test_robot_vacuums_real_labels():
    rock, dreame = values(pages.ROBOROCK_SAROS20S), values(pages.DREAME_X60_PRO)
    assert rock["battery_life"][0] == "190 min"                     # not "190 timer"
    assert dreame["battery_life"][0] is None
    assert rock["suction"][0] == "36000 Pa" and dreame["suction"][0] == "42000 Pa"
    assert rock["mop_type"][0] == "Vibrerende"
    assert rock["mop"] == ("Ja", "beskrivelsen")                     # "VibraRise … mopping"
    assert dreame["mop"] == ("Ja", "beskrivelsen")                   # "Thermal Deep Mop"
    assert rock["water_tank"][0] == "4000 ml" and dreame["water_tank"][0] == "4200 ml"
    assert rock["auto_empty"][0] == "Ja, med tilbehør" and dreame["auto_empty"][0] == "Ja"
    assert rock["noise"][0] == "64 dB"


def test_robot_vacuum_comparison_and_tab():
    from src.insights import build_insights
    products = [build(pages.ROBOROCK_SAROS20S), build(pages.DREAME_X60_PRO)]
    rows = {row.rule.key: row for row in build_rows(products)[0]}
    assert rows["auto_empty"].winner == 1                            # included vs. "med tilbehør"
    assert rows["water_tank"].winner == 1                            # 4,2 l vs 4,0 l (ml compared as liter)
    assert rows["dust"].winner is None                               # robot bin vs dock bag – not comparable
    ins = build_insights(products)
    floor = next(r for r in ins.scenarios if r.scenario.title == "Gulvvask")
    assert not any("ingen oppgir" in fact for fact in floor.reasons)
    assert any("vanntank" in fact for fact in floor.reasons)
    features = {f.label: (f.values, f.details) for f in ins.features}
    assert features["Moppefunksjon"][0] == (True, True)
    assert features["Tømmestasjon"] == ((True, True), ("med tilbehør", ""))
    assert any(c.startswith("Tømmestasjon: med tilbehør") for c in ins.cons[0])


def test_units_are_converted_before_comparing():
    from src.comparison.scorer import pick_winner
    from src.categories.guide import BATTERY_LIFE
    assert pick_winner(BATTERY_LIFE, ("190 min", "3 timer")) == 0    # 190 min > 180 min
    assert pick_winner(BATTERY_LIFE, ("150 min", "3 timer")) == 1
