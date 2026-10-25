"""Values for the product types added in v9, from real Elkjøp label sets."""
from src.categories import detect_category
from src.categories.groups import BY_ID as GROUPS, GROUPS as ALL_GROUPS, groups_for
from src.categories.guide import CATEGORIES
from src.comparison.comparer import build_rows
from src.text import display
from tests import real_pages_v9 as v9
from tests.test_robustness import build, values


# ------------------------------------------------------------- user requests
def test_pixel_always_gets_a_processor():
    assert values(v9.PIXEL9)["processor"][0] == "Tensor G4"                      # "Type prosessor"
    no_chip = values(v9.PIXEL9_NO_CHIP)["processor"]
    assert no_chip == ("Tensor G4", "produsentens modelloversikt")              # same phone, label missing


def test_pixel_updates_shown_in_norwegian():
    assert display(values(v9.PIXEL9)["updates"][0], "Programvareoppdateringer (år)") == "7 år"


def test_washer_shows_rpm_not_db():
    rows, _, _ = build_rows([build(v9.WASHER_DRYER_EW7), build(v9.WASHER_DRYER_EW7)])
    keys = [r.rule.key for r in rows]
    assert "spin" in keys and "noise" not in keys
    from src.categories.guide import BY_ID
    assert "noise" not in {r.key for r in BY_ID["washer"].rules}


def test_oral_b_features_from_elkjop_and_model_overview():
    io3, io9 = values(v9.ORALB_IO3), values(v9.ORALB_IO9)
    assert io3["brush_modes"][0] == "3" and io3["pressure_sensor"][0] == "Ja" and io3["travel_case"][0] == "Nei"
    assert io3["app"][0] == "Nei" and io3["display"][0] == "Nei"
    assert io9["brush_modes"] == ("7", "produsentens modelloversikt")
    assert io9["app"][0] == io9["display"][0] == io9["charging_case"][0] == io9["fast_charger"][0] == "Ja"


def test_philips_sonicare_features():
    p3100, p7100 = values(v9.SONICARE_3100), values(v9.SONICARE_7100)
    assert p3100["pressure_sensor"][0] == "Ja" and p3100["brush_reminder"][0] == "Ja"
    assert p3100["app"][0] == "Nei"            # "Navn på tilgjengelig app" alone does not mean Bluetooth
    assert p7100["brush_modes"][0] == "3" and p7100["travel_case"][0] == "Ja" and p7100["app"][0] == "Ja"


def test_toothbrush_comparison_picks_winners_on_features():
    rows, _, _ = build_rows([build(v9.ORALB_IO3), build(v9.ORALB_IO9)])
    by_key = {r.rule.key: r for r in rows}
    assert by_key["brush_modes"].winner == 1 and by_key["app"].winner == 1 and by_key["charging_case"].winner == 1
    assert by_key["pressure_sensor"].winner is None                          # both have it


# ------------------------------------------------------------- categories
def test_hob_microwave_oven_hood():
    hob = values(v9.HOB_HOX750)
    assert hob["hob_type"][0] == "Induksjon" and hob["total_power"][0] == "7350 W" and hob["boosters"][0] == "2"
    assert hob["pan_detect"][0] == "Ja"
    micro = values(v9.MICRO_LMS2173)
    assert micro["mw_power"][0] == "700 W" and micro["mw_volume"][0] == "17 liter" and micro["grill"][0] == "Nei"
    oven = values(v9.OVEN_EOP721)
    assert oven["oven_volume"][0] == "71 liter" and oven["pyrolysis"][0] == "Ja" and oven["probe"][0] == "Ja"
    hood = values(v9.HOOD_EFF60560)
    assert hood["airflow"][0].startswith("603") and hood["noise_low"][0] == "46 dB" and hood["noise_high"][0] == "57 dB"
    assert hood["grease_class"][0] == "D"


def test_american_fridge_and_washer_dryer():
    sbs = values(v9.LG_SIDE_BY_SIDE)
    assert sbs["fridge_volume"][0] == "420 liter" and sbs["freezer_volume"][0] == "221 liter"
    assert sbs["dispenser"][0] == "Kaldt vann" and sbs["door_in_door"][0] == "Ja"
    wd = values(v9.WASHER_DRYER_EW7)
    assert wd["capacity_kg"][0] == "7 kg" and wd["dry_capacity"][0] == "4 kg" and wd["spin"][0] == "1600 o/min"


def test_climate():
    air = values(v9.PURIFIER_FLOW_A3)
    assert air["cadr"][0] == "180" and air["hepa"][0] == "Ja" and air["noise_low"][0] == "26 dB"
    dry = values(v9.DEHUMIDIFIER_APT)
    assert dry["dehum_capacity"][0] == "12" and dry["min_temp"][0] == "5" and dry["drain"][0] == "Ja"
    heat = values(v9.ADAX_NEO)
    assert heat["thermostat_type"][0] == "Digital" and heat["power_w"][0] == "1000 W"


def test_computing_and_gaming():
    router = values(v9.ROUTER_HUAWEI_MESH3)
    assert router["wifi_std"][0].startswith("Wi-Fi 6") and router["nodes"][0] == "2"
    mouse = values(v9.LOGITECH_G305)
    assert mouse["dpi"][0] == "12000" and mouse["polling"][0] == "1000 Hz" and mouse["weight"][0] == "99 g"
    ssd = values(v9.SAMSUNG_T7)
    assert ssd["storage"][0] == "1000 GB" and ssd["read_speed"] == ("1050 MB/s", "beskrivelsen")
    assert values(v9.PS5_PRO)["storage"][0] == "2000 GB"


def test_personal_care_and_vacuum():
    ipl = values(v9.BRAUN_IPL_PRO5)
    assert ipl["skin_sensor"][0] == "Ja" and ipl["face"][0] == "Ja" and ipl["intensity"][0] == "3"
    shaver = values(v9.PHILIPS_SHAVER_7000)
    assert shaver["clean_station"][0] == "Ja" and shaver["wet_dry"][0] == "Ja" and shaver["battery_life"][0] == "60 min"
    hair = values(v9.DYSON_SUPERSONIC)
    assert hair["power_w"][0] == "1600 W" and hair["temps"][0] == "4" and hair["speeds"][0] == "3"
    jet = values(v9.SAMSUNG_JET)
    assert jet["runtime"][0] == "60 min"                                    # longest runtime, not the 3 min on max
    assert jet["pet"][0] == "Ja" and jet["clean_width"][0] == "250 mm"


def test_capsule_machine():
    pop = values(v9.NESPRESSO_VERTUO_POP)
    assert pop["system"][0] == "Nespresso Vertuo" and pop["water_tank"][0] == "0.56 liter" and pop["milk"][0] == "Nei"


# ------------------------------------------------------------------ groups
def test_every_category_is_in_a_tab():
    for category in CATEGORIES:
        assert groups_for(category.id), category.id


def test_tabs_only_name_known_categories():
    ids = {c.id for c in CATEGORIES}
    for group in ALL_GROUPS:
        assert set(group.categories) <= ids, group.id


def test_detection_inside_a_tab():
    jet = build(v9.SAMSUNG_JET)
    assert detect_category(jet, GROUPS["sda"].categories).id == "vacuum"
    assert detect_category(jet, GROUPS["mda"].categories) is None             # no MDA keyword fits a stick vacuum
