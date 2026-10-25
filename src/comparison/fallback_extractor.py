"""Finds spec values in the product name and description when the spec
table does not have them.

Order of trust: spec table (handled in spec_matcher) → product name →
description. Elkjøp names follow fixed patterns ("12/256GB", '65"', "9 kg",
"OLED"), so the name is checked before the free text.

Each extractor is (source, regex, display template). The regex must have a
named group "v" holding the value; the template turns it into what the
table shows, e.g. "{v} GB". Add a line here when a spec keeps showing up as
"Ikke oppgitt" even though the page mentions it.
"""
from __future__ import annotations

import re

from src.models import Product

NAME = "navnet"
TEXT = "beskrivelsen"

_NUM = r"\d{1,3}(?:[  ]?\d{3})*(?:[.,]\d+)?"   # 12 · 4 300 · 5000 · 6,7

# key -> list of (source, pattern, template)
EXTRACTORS: dict[str, list[tuple[str, str, str]]] = {
    # ---------------------------------------------------- phones, tablets, PCs
    "ram": [
        (NAME, r"\b(?P<v>\d{1,2})\s*/\s*\d{2,4}\s*(?:gb|tb)\b", "{v} GB"),
        (NAME, r"\b(?P<v>\d{1,2})\s*gb\s*ram\b", "{v} GB"),
        (NAME, r"/(?P<v>\d{1,2})\s*(?:gb)?\s*/\s*\d{3,4}\s*(?:gb)?\b", "{v} GB"),   # laptops: "Core5-120U/16/512"
        (TEXT, r"\b(?P<v>\d{1,2})\s*gb\s*(?:med\s+)?(?:ram|arbeidsminne|lpddr\w*)", "{v} GB"),
        (TEXT, r"\b(?:ram|arbeidsminne)\s*(?:på|:)?\s*(?P<v>\d{1,2})\s*gb", "{v} GB"),
    ],
    "storage": [
        (NAME, r"\b\d{1,2}\s*/\s*(?P<v>\d{2,4}\s*(?:gb|tb))\b", "{v}"),
        (NAME, r"/\d{1,2}\s*(?:gb)?\s*/\s*(?P<v>\d{3,4})\s*(?:gb)?\b", "{v} GB"),   # laptops: "…/16/512"
        (NAME, r"\b(?P<v>(?:64|128|256|512|1024)\s*gb|[12]\s*tb)\b", "{v}"),
        (TEXT, r"\b(?P<v>\d{2,4}\s*(?:gb|tb))\s*(?:intern\w*\s*)?(?:lagring\w*|ssd)", "{v}"),
        (TEXT, r"lagring\w*\s*(?:på|:)?\s*(?P<v>\d{2,4}\s*(?:gb|tb))", "{v}"),
    ],
    "gpu": [
        (NAME, r"/(?:rtx\s?)?(?P<v>[2-5]0[5-9]0(?:\s?ti)?)\b", "RTX {v}"),
        (TEXT, r"(?P<v>(?:geforce\s)?rtx\s?[2-5]0[5-9]0(?:\s?ti)?(?:\s?super)?|radeon\s?rx\s?\d{4}\s?(?:xtx|xt)?|arc\s?[ab]\d{3})", "{v}"),
    ],
    "vram": [
        (TEXT, r"(?P<v>\d{1,2})\s*gb\s*(?:gddr\d\w*|vram|grafikkminne)", "{v} GB"),
    ],
    "processor": [
        (NAME, r"\b(?P<v>(?:i[3579]|r[3579]|u[579]|core\s?[357]|ultra\s?[579])-[\w]{2,8})(?=/)", "{v}"),
        (TEXT, r"(?P<v>snapdragon\s+(?:x\s+)?(?:\d\s*(?:gen\s*\d|elite|\+)?[\w ]{0,15}?)(?=[-\s,.|]|$)"
               r"|exynos\s+\d{3,4}|dimensity\s+\d{3,4}|tensor\s+g\d|a\d{2}\s+(?:pro|bionic)"
               r"|apple\s+m\d(?:\s+(?:pro|max|ultra))?|intel\s+core\s+(?:ultra\s+)?[\w-]{2,12}"
               r"|amd\s+ryzen\s+(?:ai\s+)?\d[\w ]{0,12}?(?=[-\s,.|]|$))", "{v}"),
    ],
    "battery_mah": [
        (TEXT, rf"(?P<v>{_NUM})\s*mah", "{v} mAh"),
    ],
    "fast_charge": [
        (TEXT, r"(?:hurtiglad\w*|lading)[^.|]{0,40}?(?P<v>\d{2,3})\s*w\b", "{v} W"),
        (TEXT, r"(?P<v>\d{2,3})\s*w\s*(?:super\s*)?(?:hurtig)?lad", "{v} W"),
    ],
    "refresh": [
        (TEXT, r"(?P<v>\d{2,3})\s*hz", "{v} Hz"),
    ],
    "screen_size": [
        (NAME, r"(?P<v>\d{2,3}(?:[.,]\d)?)\s*(?:\"|”|''|tommer|tom\b)", '{v}"'),
        (TEXT, r"(?P<v>\d{1,3}(?:[.,]\d)?)\s*-?\s*(?:\"|”|tommer)", '{v}"'),   # "6,3-tommers"
    ],
    "resolution": [
        (NAME, r"\b(?P<v>8k|4k|uhd|qhd|wqhd|full\s*hd|fhd)\b", "{v}"),
    ],
    "optical_zoom": [
        (TEXT, r"(?P<v>\d{1,2}(?:[.,]\d)?)\s*x\s*optisk\s*zoom", "{v}x"),
    ],
    "updates": [
        (TEXT, r"(?P<v>\d)\s*(?:års?|år med)\s*(?:\w+\s){0,3}?(?:oppdatering|programvareoppdatering|os-oppgradering)", "{v} år"),
    ],
    "release_year": [
        (NAME, r"\((?P<v>20[1-3]\d)\)", "{v}"),   # 'LG 65" C5 OLED 4K Smart TV (2025)'
    ],
    # ---------------------------------------------------------------- TV & AV
    "panel": [
        (NAME, r"\b(?P<v>oled|neo\s*qled|qled|mini\s*led|qned|nanocell)\b", "{v}"),
    ],
    "screen_type": [
        (NAME, r"\b(?P<v>oled|amoled|lcd)\b", "{v}"),
        (TEXT, r"\b(?P<v>dynamic\s+amoled[\w ]{0,4}|amoled|oled|lcd)\b", "{v}"),
    ],
    "channels": [
        (NAME, r"\b(?P<v>\d\.\d(?:\.\d)?)\b", "{v}"),
    ],
    # ------------------------------------------------------------ white goods
    "energy": [
        (TEXT, r"energiklasse\s*:?\s*(?P<v>[a-g]\+{0,3})(?![a-z])", "{v}"),
    ],
    "noise": [
        (TEXT, r"(?P<v>\d{2})\s*db\b", "{v} dB"),
    ],
    "capacity_kg": [
        (NAME, r"\b(?P<v>\d{1,2}(?:[.,]\d)?)\s*kg\b", "{v} kg"),
        (TEXT, r"(?P<v>\d{1,2}(?:[.,]\d)?)\s*kg\s*(?:kapasitet|tøy|klesvask)", "{v} kg"),
    ],
    "spin": [
        (TEXT, r"(?P<v>1\s?[0-9]00)\s*(?:o/min|omdreininger|rpm)", "{v} o/min"),
    ],
    "place_settings": [
        (TEXT, r"(?P<v>\d{1,2})\s*kuverter", "{v}"),
    ],
    "volume": [
        (NAME, r"\b(?P<v>\d{2,4})\s*(?:l|liter)\b", "{v} liter"),
        (TEXT, r"(?P<v>\d{2,4})\s*liter", "{v} liter"),
    ],
    "oven_volume": [
        (NAME, r"\b(?P<v>\d{2,3})\s*(?:l|liter)\b", "{v} liter"),
        (TEXT, r"(?P<v>\d{2,3})\s*liter", "{v} liter"),
    ],
    "capacity_l": [
        (NAME, r"\b(?P<v>\d{1,2}(?:[.,]\d)?)\s*(?:l|liter)\b", "{v} liter"),
        (TEXT, r"(?P<v>\d{1,2}(?:[.,]\d)?)\s*liter", "{v} liter"),
    ],
    "tech": [
        (NAME, r"\b(?P<v>varmepumpe|kondens\w*|ventil\w*)\b", "{v}"),
    ],
    "zones": [
        (TEXT, r"(?P<v>\d)\s*(?:kokesoner|soner|kokeplater)", "{v}"),
    ],
    # --------------------------------------------- vacuums, e-mobility, small
    "suction": [
        (TEXT, rf"(?P<v>{_NUM})\s*pa\b", "{v} Pa"),
        (TEXT, r"(?P<v>\d{2,3})\s*aw\b", "{v} AW"),
    ],
    "range": [
        (TEXT, r"(?P<v>\d{1,3})\s*km(?![/\w])", "{v} km"),
    ],
    "battery_life": [
        (TEXT, r"(?:batteritid|spilletid|brukstid)[^.|]{0,30}?(?P<v>\d{1,3})\s*(?:timer|t\b)", "{v} timer"),
        (TEXT, r"(?P<v>\d{1,3})\s*timers?\s*(?:batteritid|spilletid|avspilling)", "{v} timer"),
    ],
    # ------------------------------------------- kitchen machines (description)
    "motor_power": [
        (TEXT, r"(?P<v>\d{3,4})\s*-?\s*w(?:att)?\b", "{v} W"),
    ],
    "bowl_volume": [
        (TEXT, r"bolle\w*\s*(?:på\s*)?(?P<v>\d{1,2}(?:[.,]\d)?)\s*(?:l|liter)\b", "{v} liter"),
        (TEXT, r"(?P<v>\d{1,2}(?:[.,]\d)?)\s*(?:l|liter)s?\s*(?:\w+\s){0,2}bolle", "{v} liter"),
    ],
    "scale": [
        (TEXT, r"(?P<v>integrert vekt|innebygd vekt|easyweight|vekt med 1 ?g|veier direkte i bollen)", "Ja"),
    ],
    "timer": [
        (TEXT, r"(?P<v>timerfunksjon|innebygd timer|integrert timer|digital timer)", "Ja"),
        # plain "timer" also means hours ("4 timer") – only accept it with no number in front
        (TEXT, r"(?<!\d)(?<!\d )(?P<v>\btimer\b)(?!\s*\d)", "Ja"),
    ],
    "display": [
        (TEXT, r"(?P<v>berøringsskjerm|touch-?skjerm|tft-skjerm|digitalt display|lcd-display)", "Ja"),
    ],
    "auto_programs": [
        (TEXT, r"(?P<v>automatiske programmer|sensorstyrt\w*|sensordrevne|sensorteknologi)", "Ja"),
    ],
    "pulse": [
        (TEXT, r"(?P<v>pulsfunksjon|pulsknapp|turbofunksjon)", "Ja"),
    ],
    "dishwasher_safe": [
        (TEXT, r"(?P<v>tåler oppvaskmaskin|kan maskinvaskes|oppvaskmaskinsikker|kan vaskes i oppvaskmaskin)", "Ja"),
    ],
    # ------------------------------------------- features often only in the text
    # Everything here returns "Ja" and is shown as "nevnt i beskrivelsen".
    "mop": [
        (TEXT, r"(?P<v>moppe\w*|mopping|mop-?system|deep mop|vibrarise|gulvvask|våtvask)", "Ja"),
    ],
    "auto_empty": [
        (TEXT, r"(?P<v>tømmestasjon|selvtømm\w*|tømmer seg selv|automatisk tømming)", "Ja"),
    ],
    "obstacle": [
        (TEXT, r"(?P<v>hindringsgjenkjenning|unngår hindringer|hinderunngåelse|objektgjenkjenning)", "Ja"),
    ],
    "hepa": [(TEXT, r"(?P<v>hepa)", "Ja")],
    "anc": [(TEXT, r"(?P<v>aktiv støydemping|\banc\b|støykansellering)", "Ja")],
    "gps": [(TEXT, r"(?P<v>innebygd gps|integrert gps|\bgps\b)", "Ja")],
    "nfc": [(TEXT, r"(?P<v>\bnfc\b)", "Ja")],
    "esim": [(TEXT, r"(?P<v>\besim\b)", "Ja")],
    "wireless_charge": [(TEXT, r"(?P<v>trådløs lading|qi2?\b|magsafe)", "Ja")],
    "atmos": [(TEXT, r"(?P<v>dolby atmos)", "Ja")],
    "dolby_vision": [(TEXT, r"(?P<v>dolby vision)", "Ja")],
    "nofrost": [(TEXT, r"(?P<v>no ?frost|frostfri)", "Ja")],
    "zero_zone": [(TEXT, r"(?P<v>nullsone|0 ?°c-sone|vitafresh|freshzone)", "Ja")],
    "ice_crush": [(TEXT, r"(?P<v>knuser is|isknus\w*)", "Ja")],
    "auto_open": [(TEXT, r"(?P<v>automatisk døråpning|autoopen|døren åpnes automatisk)", "Ja")],
    "steam": [(TEXT, r"(?P<v>dampfunksjon|dampprogram|damprens\w*|damp\w* (?:assist|stek|vask))", "Ja")],
    "auto_dose": [(TEXT, r"(?P<v>auto ?dose|automatisk dosering|autodosering|twindos|i-?dos)", "Ja")],
    "multipoint": [(TEXT, r"(?P<v>multipoint|flerpunkt|koble til to enheter)", "Ja")],
    "brew_group": [(TEXT, r"(?P<v>avtakbar bryggeenhet|uttakbar bryggeenhet|bryggeenheten kan tas ut)", "Ja")],
    "heat_pump": [(TEXT, r"(?P<v>varmepumpe)", "Ja")],
    "vrr": [(TEXT, r"(?P<v>\bvrr\b|variable refresh rate)", "Ja")],
    # ------------------------------------------------------------ added v9
    "app": [(TEXT, r"(?P<v>\bapp(?:en)?\b|bluetooth-tilkob\w*)", "Ja")],
    "read_speed": [(TEXT, r"(?:opptil|inntil|lese\w*)\s*(?:hastighet\w*\s*(?:på|:)?\s*)?(?P<v>\d{3,5})\s*mb/s", "{v} MB/s"),
                   (TEXT, r"(?P<v>\d{3,5})\s*mb/s", "{v} MB/s")],
    "brush_modes": [(TEXT, r"(?P<v>\d)\s*(?:puss|rengjørings)?(?:moduser|pussemoduser|programmer)", "{v}")],
    "smart_sensor": [(TEXT, r"(?P<v>smart trykksensor|360.{0,20}trykk|visible pressure|synlig trykk)", "Ja")],
    "brush_reminder": [(TEXT, r"(?P<v>brushsync|påminnelse om (?:å )?bytte)", "Ja")],
    "ai_tracking": [(TEXT, r"(?P<v>ai-?(?:gjenkjenning|sporing)|3d-?sporing|kunstig intelligens)", "Ja")],
    "charging_case": [(TEXT, r"(?P<v>ladende reiseetui|reiseetui med lad\w*|ladeetui)", "Ja")],
    "travel_case": [(TEXT, r"(?P<v>reiseetui|reiseveske|oppbevaringsetui)", "Ja")],
    "clean_station": [(TEXT, r"(?P<v>rensestasjon|rense- og ladestasjon|cleaning pod|clean ?& ?charge)", "Ja")],
    "pet": [(TEXT, r"(?P<v>dyrehår|kjæledyr)", "Ja")],
    "dust_sensor": [(TEXT, r"(?P<v>støvsensor|piezo\w*|lasersensor|partikkelsensor)", "Ja")],
    "ice_maker": [(TEXT, r"(?P<v>ismaskin|isbitmaskin|isterningmaskin)", "Ja")],
    "door_in_door": [(TEXT, r"(?P<v>door-?in-?door|instaview)", "Ja")],
    "pyrolysis": [(TEXT, r"(?P<v>pyrolyse)", "Ja")],
    "hob2hood": [(TEXT, r"(?P<v>hob2hood|hood ?link)", "Ja")],
    "certified": [(TEXT, r"(?P<v>ecbc|sca-godkjent|godkjent av (?:det )?europeiske kaffebryggesenter)", "Ja")],
    "thermos": [(TEXT, r"(?P<v>termokanne|termoskanne)", "Ja")],
    "hall_effect": [(TEXT, r"(?P<v>hall ?effect)", "Ja")],
    "paddles": [(TEXT, r"(?P<v>bakknapper|paddles)", "Ja")],
    "force_feedback": [(TEXT, r"(?P<v>force ?feedback)", "Ja")],
    "direct_drive": [(TEXT, r"(?P<v>direct ?drive)", "Ja")],
    "dehum_capacity": [(NAME, r"(?P<v>\d{1,2})\s*(?:l|liter)\s*/?\s*(?:døgn|dogn|24 ?t)", "{v} liter per døgn"),
                       (TEXT, r"(?P<v>\d{1,2})\s*(?:l|liter) (?:i|per) døgn", "{v} liter per døgn")],
    "bottles": [(NAME, r"(?P<v>\d{1,3})\s*(?:flasker|fl\.)", "{v}"), (TEXT, r"(?:plass til|opptil)\s*(?P<v>\d{1,3})\s*flasker", "{v}")],
    "wine_zones": [(TEXT, r"(?P<v>to|2|tre|3)\s*(?:temperatur)?soner", "{v}")],
    "airflow": [(TEXT, r"(?P<v>\d{3,4})\s*m(?:3|³)\s*/\s*(?:h|t)", "{v} m³/t")],
    "cadr": [(TEXT, r"cadr[^0-9]{0,30}(?P<v>\d{2,4})", "{v} m³/t")],
    "flashes": [(TEXT, r"(?P<v>\d{2,3}[  ]?\d{3})\s*(?:lys)?blink", "{v}")],
    "power_w": [
        (NAME, r"\b(?P<v>\d{3,4})\s*w\b", "{v} W"),
    ],
    "pressure": [
        (TEXT, r"(?P<v>\d{1,2})\s*bar\b", "{v} bar"),
    ],
}


def _format(template: str, raw: str) -> str:
    """Fill the template and tidy spacing/case (e.g. '256gb' → '256 GB')."""
    value = re.sub(r"\s+", " ", raw.strip())
    value = re.sub(r"(\d)\s*(gb|tb)\b", lambda m: f"{m.group(1)} {m.group(2).upper()}", value, flags=re.I)
    if not any(ch.isdigit() for ch in value) and value == value.lower():
        # Lowercase words from running text: short ones are acronyms (OLED, LCD).
        value = " ".join(w.upper() if len(w) <= 5 else w.capitalize() for w in value.split())
    return template.format(v=value)


def extract_all(product: Product, key: str) -> list[tuple[str, str]]:
    """Every (value, source) found in name and description, for max-type rules."""
    found = []
    for source, pattern, template in EXTRACTORS.get(key, []):
        text = product.name if source == NAME else product.description
        for match in re.finditer(pattern, text or "", flags=re.IGNORECASE):
            if match.group("v"):
                found.append((_format(template, match.group("v")), source))
    return found


def extract(product: Product, key: str) -> tuple[str | None, str]:
    """Return (value, source) for a rule key from name/description, or (None, "")."""
    for source, pattern, template in EXTRACTORS.get(key, []):
        text = product.name if source == NAME else product.description
        match = re.search(pattern, text or "", flags=re.IGNORECASE)
        if match and match.group("v"):
            return _format(template, match.group("v")), source
    return None, ""
