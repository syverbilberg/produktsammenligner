"""Products of different types: same / related / unrelated."""
from src.categories import BY_ID, detect_category
from src.categories.compatibility import RELATED, SAME, UNRELATED, check
from src.comparison import compare, relevant_dimensions
from src.comparison.comparer import build_rows
from src.insights import build_insights
from src.insights.overview import build_overview
from tests import real_pages as pages
from tests.test_robustness import build


def test_levels():
    assert check([BY_ID["mobile"], BY_ID["mobile"]]).level == SAME
    assert check([BY_ID["laptop"], BY_ID["tablet"]]).level == RELATED
    assert check([BY_ID["kitchen_machine"], BY_ID["blender"]]).level == RELATED
    phone_vacuum = check([BY_ID["mobile"], BY_ID["vacuum"]])
    assert phone_vacuum.level == UNRELATED
    assert phone_vacuum.message.startswith("Produkt A er en mobiltelefon og B er en støvsuger")


def test_odd_one_out_is_the_minority():
    compat = check([BY_ID["vacuum"], BY_ID["mobile"], BY_ID["vacuum"]])
    assert compat.odd_ones == [1]


def test_unrelated_products_are_never_compared():
    """The bug from the screenshot: phone battery '51' vs robot vacuum, phone 'cheaper' and recommended."""
    products = [build(pages.S26), build(pages.DREAME_X60_PRO)]
    rows, notes, _ = build_rows(products)
    assert rows == [] and "kan ikke sammenlignes" in notes[0]
    assert relevant_dimensions(products) == ["Pris"]


def test_side_by_side_overview_uses_each_products_own_category():
    phone, robot = build_overview([build(pages.S26), build(pages.DREAME_X60_PRO)])
    assert phone.category_name == "Mobiltelefoner" and robot.category_name == "Robotstøvsugere"
    assert ("Batterikapasitet", "4300 mAh") in phone.specs
    assert ("Sugeeffekt", "42000 Pa") in robot.specs
    assert "Moppefunksjon" in robot.features and "Trådløs lading" in phone.features
    assert not any("Moppe" in f for f in phone.features)


def test_related_products_compare_shared_specs_with_note():
    laptop = build(pages.HP_LAPTOP)
    tablet = build({**pages.HP_LAPTOP, "name": "Samsung Galaxy Tab S10 nettbrett 12/256GB",
                    "url": "https://www.elkjop.no/product/mobil-nettbrett-og-smartklokker/nettbrett/samsung-tab-s10/2000001",
                    "specs": {"Produkttype": "Nettbrett", "Internminne/RAM (GB)": "12", "Intern lagring (GB)": "256",
                              "Størrelse (tommer)": "11"}})
    assert detect_category(tablet).id == "tablet"
    rows, notes, _ = build_rows([laptop, tablet])
    keys = {r.rule.key for r in rows}
    assert {"ram", "storage", "screen_size"} <= keys
    assert "beslektede" in notes[0]
    assert "generation" not in keys
    ins = build_insights([laptop, tablet])   # the tab still works for related types
    assert len(ins.choose) == 2
