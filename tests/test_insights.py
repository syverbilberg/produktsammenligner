"""Tests for the "Funksjoner og bruk" tab."""
import pytest

from src.categories import CATEGORIES
from src.insights import build_insights
from src.insights.names import short_name
from src.models import Product
from tests import real_pages as pages
from tests.test_robustness import build


def test_kitchen_machines_match_the_expected_use_cases():
    ins = build_insights([build(pages.BOSCH_MUMS6), build(pages.KENWOOD_KVL85)])
    assert ins.short_names == ["Bosch Series 6", "Kenwood Titanium Chef Baker XL"]
    winners = {r.scenario.title.split(",")[0]: r.winner for r in ins.scenarios}
    assert winners["Brød"] == 0              # 1600 W (counts double) vs bigger bowl
    assert winners["Kaker"] == 0             # automatic programs/timer/display only mentioned for Bosch
    assert winners["Store bakeprosjekter og flere oppskrifter etter hverandre"] == 1   # 7 l bowl
    assert ins.included[0] == ["Bolle", "Hjulpisker", "Eltekrok"]
    features = {f.label: f.values for f in ins.features}
    assert features["Integrert vekt"] == (True, True)
    assert features["Automatiske programmer"] == (True, None)       # not mentioned ≠ missing
    assert any("Motorkraft: 1600 W" in p for p in ins.pros[0])
    assert any("Bollevolum: 7 liter" in p for p in ins.pros[1])
    assert "Bosch Series 6" in ins.choose[0] and "brød" in ins.choose[0]


def test_phones_pros_and_choose():
    ins = build_insights([build(pages.S25), build(pages.S26)])
    assert any(p.startswith("Modellgenerasjon: S26") for p in ins.pros[1])
    assert any(p.startswith("Lavere pris") for p in ins.pros[0])
    assert any("Lader følger ikke med" in c for c in ins.cons[0]) is False   # both lack it → no difference
    assert "S26" in ins.choose[1]


@pytest.mark.parametrize("count", [2, 3, 4])
@pytest.mark.parametrize("category", CATEGORIES, ids=lambda c: c.id)
def test_tab_builds_for_every_category_and_count(category, count):
    """Synthetic products per category with a few generic specs must never crash."""
    products = []
    for i in range(count):
        specs = {"Produkttype": category.keywords[0], "Energiklasse": "ABC"[i % 3],
                 "Vekt (kg)": str(5 + i), "Wi-Fi": "Ja" if i % 2 else "Nei", "Lanseringsår": str(2022 + i)}
        products.append(Product(sku=str(1000 + i), name=f"Merke{i} {category.keywords[0]} M{i}00",
                                price=1000.0 + 500 * i, category_path=f"x/{category.keywords[0]}", specs=specs))
    ins = build_insights(products)
    assert len(ins.pros) == len(ins.cons) == len(ins.choose) == count
    assert all(text.startswith("Velg **") for text in ins.choose)


def test_short_names():
    assert short_name("Samsung Galaxy S26 5G smarttelefon 12/256GB (sort)") == "Samsung Galaxy S26"
    assert short_name('HP Laptop 14-ep1830no Core5-120U/16/512 14" bærbar PC') == "HP Laptop 14-ep1830no"
    assert short_name("Asko oppvaskmaskin DBI8557MIMXXLS") == "Asko DBI8557MIMXXLS"
    assert short_name('LG 65" C5 OLED 4K Smart TV (2025)') == "LG C5 OLED"
