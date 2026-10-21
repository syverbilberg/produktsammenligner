"""Offline tests: run with  python -m pytest"""
import numpy as np
import pytest

from src.categories import detect_category
from src.categories import dimensions as d
from src.comparison import compare, relevant_dimensions
from src.comparison.value_parser import parse_energy_class, parse_number
from src.fetching import http_client, product_fetcher
from src.fetching.page_parser import find_product_link, parse_product_page
from src.fetching.url_resolver import InputError, candidate_urls
from src.models import Product
from tests.fixtures import ASKO_SPECS, OTHER_SPECS, product_page, search_page

ASKO_PATH = "hvitevarer/oppvaskmaskin/asko-oppvaskmaskin-dbi8557mimxxls"
ASKO_URL = f"https://www.elkjop.no/product/{ASKO_PATH}/457340"


def make(name, price, specs, sku, path="hvitevarer/oppvaskmaskin", description=""):
    product = Product(sku=sku, url="", category_path=path)
    return parse_product_page(product_page(name, price, specs, description), product)


def test_resolver_accepts_code_and_link():
    sku, urls = candidate_urls(" 457340 ")
    assert sku == "457340" and urls[0].endswith("/product/457340")
    sku, urls = candidate_urls("elkjop.no/product/a/b/c/457340")
    assert sku == "457340" and urls == ["https://elkjop.no/product/a/b/c/457340"]
    with pytest.raises(InputError):
        candidate_urls("hei")


def test_parser_reads_json_ld_and_skips_useless_specs():
    product = make("Asko oppvaskmaskin DBI8557MIMXXLS", 13757, ASKO_SPECS, "457340")
    assert product.price == 13757 and product.brand == "Asko"
    assert product.specs["Lydnivå (dB)"] == "41"
    assert "Strekkode (EAN)" not in product.specs
    assert "Høyde (ink. emballasje)" not in product.specs


def test_search_link_found_in_embedded_json():
    html = search_page("457340", ASKO_PATH)
    assert find_product_link(html, "457340") == ASKO_URL


def test_value_parsing():
    assert parse_number("5 000 mAh") == 5000
    assert parse_number("1 TB") == 1024
    assert np.isnan(parse_number("Ikke oppgitt"))
    assert parse_energy_class("A+++") < parse_energy_class("B")


def test_detects_dishwasher():
    product = make("Asko oppvaskmaskin", 13757, ASKO_SPECS, "457340")
    assert detect_category(product).id == "dishwasher"


def test_full_comparison():
    a = make("Asko oppvaskmaskin", 13757, ASKO_SPECS, "457340")
    b = make("Gram oppvaskmaskin", 8990, OTHER_SPECS, "612864")
    dims = relevant_dimensions((a, b))
    assert dims[0] == d.PRICE and d.NOISE in dims
    weights = {dim: 2 for dim in dims}
    result = compare((a, b), weights)
    winners = {row.rule.key: row.winner for row in result.rows}
    assert winners["noise"] == 0          # 41 dB beats 44 dB
    assert winners["energy"] == 0         # B beats C
    assert winners["cutlery"] == 1        # bestikkskuff beats bestikkurv
    assert winners["water"] == 0          # 9.6 L beats 10.5 L
    assert "Velg A" in result.verdict and "Velg B" in result.verdict


def test_fetch_by_code_falls_back_to_search(monkeypatch):
    pages = {
        "https://www.elkjop.no/product/457340": http_client.Page("", "", 404, "not found"),
        "https://www.elkjop.no/search?SearchTerm=457340": http_client.Page(
            "", "https://www.elkjop.no/search?SearchTerm=457340", 200, search_page("457340", ASKO_PATH)),
        ASKO_URL: http_client.Page("", ASKO_URL, 200, product_page("Asko oppvaskmaskin", 13757, ASKO_SPECS)),
    }
    monkeypatch.setattr(http_client, "get", lambda url, timeout=15: pages.get(url, http_client.Page(url, url, 404, "")))
    product = product_fetcher.fetch_product("457340")
    assert product.sku == "457340"
    assert product.category_path == "hvitevarer/oppvaskmaskin"
    assert product.price == 13757


def test_three_products():
    a = make("Asko oppvaskmaskin", 13757, ASKO_SPECS, "1")
    b = make("Gram oppvaskmaskin", 8990, OTHER_SPECS, "2")
    c = make("Bosch oppvaskmaskin", 10990, {**OTHER_SPECS, "Lydnivå (dB)": "39", "Energiklasse": "A"}, "3")
    result = compare([a, b, c], {dim: 2 for dim in relevant_dimensions([a, b, c])})
    winners = {row.rule.key: row.winner for row in result.rows}
    assert winners["noise"] == 2 and winners["energy"] == 2
    assert len(result.summaries) == 3 and len(result.scores) == 3
    assert "Velg C" in result.verdict


def test_mobile_priorities_have_camera_not_connectivity():
    specs = {"Produkttype": "Mobiltelefon", "RAM (GB)": "8", "5G": "Ja", "NFC": "Ja"}
    path = "mobil-nettbrett-og-smartklokker/mobiltelefon"
    a = make("Samsung Galaxy S25", 9990, specs, "1", path)
    b = make("Google Pixel 9", 8990, {**specs, "RAM (GB)": "12"}, "2", path)
    dims = relevant_dimensions([a, b])
    assert d.CAMERA in dims and d.CONNECTIVITY not in dims


def test_neutral_level_exists():
    assert list(d.LEVELS) == ["Ikke viktig", "Litt viktig", "Nøytral", "Viktig", "Svært viktig"]
    assert d.DEFAULT_LEVEL == "Nøytral"


PHONE_PATH = "mobil-nettbrett-og-smartklokker/mobiltelefon"
S25 = {"Produkttype": "Mobiltelefon", "Prosessor": "Snapdragon 8 Elite for Galaxy", "RAM (GB)": "12",
       "Lagringskapasitet (GB)": "256", "Batterikapasitet (mAh)": "4000",
       "Ladeeffekt (W)": "10", "Maks ladeeffekt (W)": "25", "Trådløs ladeeffekt (W)": "15", "Trådløs lading": "Ja"}
S26 = {**S25, "Prosessor": "Exynos 2600", "Batterikapasitet (mAh)": "4300"}


def test_newer_phone_wins_with_neutral_price():
    a = make("Samsung Galaxy S25 5G smarttelefon 12/256GB (Blueblack)", 12290, S25, "938012", PHONE_PATH)
    b = make("Samsung Galaxy S26 5G smarttelefon 12/256GB (sort)", 13490, S26, "1039743", PHONE_PATH)
    weights = {dim: 2 for dim in relevant_dimensions([a, b])}
    weights.update({d.PERFORMANCE: 3, d.BATTERY: 3})
    result = compare([a, b], weights)
    rows = {row.rule.key: row for row in result.rows}
    assert rows["generation"].values == ("S25", "S26") and rows["generation"].winner == 1
    assert rows["fast_charge"].values == ("25 W", "25 W")      # max wired watt, not 10 W or wireless
    assert result.scores[1] > result.scores[0]
    assert "passer **B** best" in result.verdict


def test_generation_needs_matching_names():
    a = make("Apple iPhone 16 128GB", 9990, S25, "1", PHONE_PATH)
    b = make("Apple iPhone 17 Pro 256GB", 14990, S25, "2", PHONE_PATH)
    c = make("Asko oppvaskmaskin", 1, ASKO_SPECS, "3")
    d_ = make("Gram oppvaskmaskin", 1, OTHER_SPECS, "4")
    from src.comparison.generation import model_generations
    assert model_generations([a, b]) == ("16", "17")
    assert model_generations([c, d_]) == (None, None)


def test_no_brand_specific_explanations_for_phones():
    from src.categories.guide import BY_ID
    assert not any("iphone" in r.why.lower() for r in BY_ID["mobile"].rules)


def _rows(products):
    from src.comparison.comparer import build_rows
    rows, _, _ = build_rows(products)
    return {row.rule.key: row for row in rows}


def test_ram_and_storage_from_name_when_table_lacks_them():
    no_ram = {k: v for k, v in S26.items() if k not in ("RAM (GB)", "Lagringskapasitet (GB)")}
    a = make("Samsung Galaxy S25 5G smarttelefon 12/256GB (Blueblack)", 12290, S25, "1", PHONE_PATH)
    b = make("Samsung Galaxy S26 5G smarttelefon 12/256GB (sort)", 13490, no_ram, "2", PHONE_PATH)
    rows = _rows([a, b])
    assert rows["ram"].values == ("12 GB", "12 GB") and rows["ram"].sources == ("", "navnet")
    assert rows["storage"].values[1] == "256 GB" and rows["storage"].sources[1] == "navnet"


def test_values_from_description_text():
    text = ("Telefonen har en rask Exynos 2600-brikke og 12 GB RAM for smidig multitasking. "
            "Det er plass til alt på de 256 GB lagringsplass, og batteriet på 4 300 mAh varer hele dagen.")
    a = make("Samsung Galaxy S26 smarttelefon", 13490, {"Produkttype": "Mobiltelefon"}, "1", PHONE_PATH, text)
    b = make("Samsung Galaxy S25 smarttelefon", 12290, S25, "2", PHONE_PATH)
    rows = _rows([a, b])
    assert rows["ram"].values[0] == "12 GB" and rows["ram"].sources[0] == "beskrivelsen"
    assert rows["storage"].values[0] == "256 GB"
    assert rows["battery_mah"].values[0] == "4 300 mAh" and rows["battery_mah"].winner == 0
    assert rows["processor"].values[0].lower() == "exynos 2600"


def test_spec_table_wins_over_name():
    a = make("Samsung Galaxy S25 smarttelefon 8/128GB", 1, {**S25, "RAM (GB)": "12"}, "1", PHONE_PATH)
    b = make("Samsung Galaxy S26 smarttelefon 12/256GB", 1, S26, "2", PHONE_PATH)
    assert _rows([a, b])["ram"].values == ("12 GB", "12 GB")


def test_tv_values_from_name():
    path = "tv-lyd-og-smarte-hjem/tv/oled-tv"
    a = make('Samsung 65" QN90F Neo QLED 4K Smart TV (2025)', 19990, {"Produkttype": "TV"}, "1", path)
    b = make('LG 65" C5 OLED 4K Smart TV (2025)', 21990, {"Produkttype": "TV"}, "2", path)
    rows = _rows([a, b])
    assert rows["screen_size"].values == ('65"', '65"')
    assert rows["panel"].values == ("Neo QLED", "OLED") and rows["panel"].winner == 1
    assert rows["resolution"].values == ("4K", "4K")


def test_washer_values_from_name_and_text():
    path = "hvitevarer/vaskemaskin"
    a = make("Bosch vaskemaskin WGG24409SN 9 kg", 8990, {"Produkttype": "Vaskemaskin"}, "1", path,
             "Sentrifugerer med opptil 1400 o/min og har energiklasse A.")
    b = make("Electrolux vaskemaskin EW6F4842 8 kg", 7990, {"Produkttype": "Vaskemaskin"}, "2", path,
             "Maskinen sentrifugerer med 1200 o/min. Energiklasse B.")
    rows = _rows([a, b])
    assert rows["capacity_kg"].values == ("9 kg", "8 kg") and rows["capacity_kg"].winner == 0
    assert rows["spin"].values == ("1400 o/min", "1200 o/min") and rows["spin"].winner == 0
    assert rows["energy"].values == ("A", "B") and rows["energy"].winner == 0
