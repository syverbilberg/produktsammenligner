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
             pages.ROBOROCK_SAROS20S, pages.DREAME_X60_PRO, pages.PCS_PRIME400, pages.LEGION_TOWER5,
             pages.LG_B5_TV, pages.ASKO_W3096, pages.SONY_XM6, pages.LG_DRYER, pages.MELITTA_SOLO]


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
    assert v["processor"][0] == "Intel Core 5 120U"           # type + "Nummer"
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
                "Oppvaskmaskin": "dishwasher", "Robotstøvsuger": "vacuum", "Stasjonær gaming-PC": "desktop",
                "TV": "tv", "Vaskemaskin": "washer", "Hodetelefoner": "headphones", "Tørketrommel": "dryer",
                "Kaffemaskin": "coffee"}[page["specs"]["Produkttype"]]
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


def test_gaming_desktops_show_gpu_and_cpu():
    """The bug from the user: GPU not shown, no winner for the CPU."""
    pcs, legion = values(pages.PCS_PRIME400), values(pages.LEGION_TOWER5)
    assert pcs["gpu"][0] == "GeForce RTX 5070" and legion["gpu"][0] == "GeForce RTX 5070"
    assert pcs["processor"][0] == "Intel Core i7 14700F"                # "Prosessortype" + "Nummer"
    assert legion["processor"][0] == "AMD Ryzen 7 7700X"
    assert pcs["vram"][0] == "12" and pcs["psu"][0] == "750 W"
    assert pcs["ram_max"][0] == "192 GB"


def test_cpu_and_gpu_get_winners_only_when_the_gap_is_clear():
    from src.comparison.scorer import pick_winner
    from src.categories.guide import GPU, PROCESSOR
    assert pick_winner(GPU, ("GeForce RTX 5070", "GeForce RTX 5060 Ti")) == 0
    assert pick_winner(GPU, ("GeForce RTX 5070", "GeForce RTX 5070")) is None
    assert pick_winner(GPU, ("Radeon RX 9070 XT", "GeForce RTX 5070")) == 0
    assert pick_winner(PROCESSOR, ("Intel Core i5 14400F", "Intel Core i7 14700F")) == 1
    assert pick_winner(PROCESSOR, ("Intel Core i7 14700F", "AMD Ryzen 7 7700X")) == 0      # 20 vs 8 cores
    assert pick_winner(PROCESSOR, ("Intel Core i7 14700F", "Intel Core i7 14700K")) is None  # close: no made-up winner
    assert pick_winner(PROCESSOR, ("AMD Ryzen 7 9800X3D", "AMD Ryzen 5 7600")) == 0
    assert pick_winner(PROCESSOR, ("Snapdragon 8 Elite for Galaxy", "Exynos 2200")) == 0


def test_desktop_comparison_lists_gpu_first():
    products = [build(pages.PCS_PRIME400), build(pages.LEGION_TOWER5)]
    rows, _, _ = build_rows(products)
    assert rows[0].rule.key == "gpu"
    keys = [r.rule.key for r in rows]
    assert {"gpu", "vram", "processor", "ram", "storage", "psu"} <= set(keys)


def test_tv_real_labels():
    v = values(pages.LG_B5_TV)
    assert v["panel"][0] == "OLED" and v["refresh"][0] == "120 Hz"        # "Bildepanelfrekvens (Hz)"
    assert v["panel_score"][0] == "8" and v["contrast_score"][0] == "10"
    assert v["hdr_formats"][0] == "Dolby Vision"
    assert v["dolby_vision"][0] == "Ja"
    assert v["hdmi_count"][0] == "3" and v["hdmi_standard"][0] == "HDMI 2.1"
    assert v["vrr"][0] == "Ja" and v["allm"][0] == "Ja" and v["platform"][0] == "webOS"
    assert v["atmos"] == ("Ja", "beskrivelsen") and v["sound_w"][0] == "20 W"


def test_washer_real_labels():
    v = values(pages.ASKO_W3096)
    assert v["capacity_kg"][0] == "9 kg" and v["spin"][0] in ("1600 o/min", "1600")
    assert v["noise"][0] == "70 dB"                                          # "Luftbåren akustisk lydutslipp …"
    assert v["water"][0] == "35 liter/syklus"
    assert v["auto_dose"] == ("Ja", "beskrivelsen") and v["steam"] == ("Ja", "beskrivelsen")


def test_headphones_real_labels():
    v = values(pages.SONY_XM6)
    assert v["anc"][0] == "Ja"                                               # "Aktiv støykansellering"
    assert v["battery_anc"][0] == "30 timer" and v["battery_life"][0] == "40 timer"
    assert v["multipoint"] == ("Ja", "beskrivelsen")
    assert v["weight"][0] == "254 g" and v["hires"][0] == "Hi-Res Audio"


def test_dryer_heat_pump_is_not_ranked_as_condenser():
    v = values(pages.LG_DRYER)
    assert v["heat_pump"][0] == "Ja" and v["tech"][0] == "Kondens"
    assert v["capacity_kg"][0] == "9 kg" and v["noise"][0] == "62 dB"
    assert v["moisture"][0] == "Sensor" and v["energy_year"][0] == "194"


def test_coffee_machine_real_labels():
    v = values(pages.MELITTA_SOLO)
    assert v["type"][0] == "Automatisk" and v["grinder"][0] == "Ja" and v["grind_levels"][0] == "5"
    assert v["milk"][0] == "Ja" and v["frother"][0] == "Ja" and v["pressure"][0] == "15 Bar"
    assert v["water_tank"][0] == "1.2 liter"                                 # "(I)" is Elkjøp's typo for liter
    assert v["rinse"][0] == "Ja" and v["descale_alert"][0] == "Ja"


@pytest.mark.parametrize("category", CATEGORIES, ids=lambda c: c.id)
def test_every_category_has_a_comparable_key_spec(category):
    """Every category must have at least three rules that can pick a winner,
    so a comparison never ends up as only "Info" rows."""
    comparable = [r for r in category.rules if r.kind != "info"]
    assert len(comparable) >= 3, category.id
